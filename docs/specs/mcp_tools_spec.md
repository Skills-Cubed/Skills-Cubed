# MCP Tools Specification

Interface contracts for the three core tools. These are the boundaries where modules meet — get these right and integration is trivial.

## 1. Search Skills

Find existing skills that match a customer query.

### Request

```python
class SearchRequest(BaseModel):
    query: str            # Customer's question or issue description
    top_k: int = 5        # Max number of skills to return
    min_score: float = 0.0  # Minimum relevance threshold (0-1)
```

### Response

```python
class SkillMatch(BaseModel):
    skill_id: str         # UUID (application-generated)
    title: str            # Human-readable skill title
    score: float          # Relevance score (0-1, hybrid of keyword + vector)
    resolution: str       # The resolution content
    conditions: list[str] # When this skill applies

class SearchResponse(BaseModel):
    matches: list[SkillMatch]
    query: str            # Echo back the original query
    search_time_ms: float # For benchmarking
```

### Flow

```
Client → POST /search → Server [Josh]
  → Orchestration [Griffin] computes query embedding, prepares search params
  → db.hybrid_search(query_embedding, query_text, top_k, min_score) [Torrin]
  → Neo4j returns matching skill nodes with scores
  → Return SearchResponse
```

### Notes
- Hybrid search combines keyword (BM25-style) and vector (cosine similarity) scores
- Query embedding is computed by the orchestration layer and passed to `db.hybrid_search(query_embedding, query_text, top_k, min_score)` — the DB layer only accepts pre-computed vectors
- Empty results return `matches: []`, not an error

---

## 2. Create Skill

Extract a new skill from a successful support conversation.

### Request

```python
class CreateRequest(BaseModel):
    conversation: str     # Full conversation transcript
    resolution_confirmed: bool = False  # Was the resolution explicitly confirmed?
    metadata: dict = {}   # Optional: product area, issue type, customer segment
```

### Response

```python
class CreateResponse(BaseModel):
    skill_id: str         # UUID (application-generated) of the created skill
    title: str            # Generated title
    skill: dict           # Full skill document (see skill_schema_spec.md)
    created: bool         # True if new, False if duplicate detected
```

### Flow

```
Client → POST /create → Server [Josh]
  → Orchestration [Griffin] decides to create (based on conversation analysis)
  → llm.extract_skill(conversation) [Griffin, Gemini Pro]
  → LLM returns structured skill document
  → db.check_duplicate(skill.embedding, threshold=0.95) [Torrin]
  → If duplicate: return existing skill with created=False
  → If new: db.create_skill(skill) [Torrin]
  → Return CreateResponse
```

### Notes
- Skill extraction uses Gemini Pro — this is the expensive call that the learning loop eliminates over time
- Duplicate detection is approximate (vector similarity > 0.95 threshold)
- The `metadata` field is optional — LLM will infer what it can from the conversation

---

## 3. Update Skill

Refine an existing skill with new conversation data.

### Request

```python
class UpdateRequest(BaseModel):
    skill_id: str         # ID of the skill to update
    conversation: str     # New conversation that used/refined this skill
    feedback: str = ""    # Optional: explicit feedback on the skill's accuracy
```

### Response

```python
class UpdateResponse(BaseModel):
    skill_id: str         # Same ID
    title: str            # Possibly updated title
    changes: list[str]    # Human-readable list of what changed
    version: int          # Incremented version number
```

### Flow

```
Client → POST /update → Server [Josh]
  → Orchestration [Griffin] decides to update (vs create new)
  → db.get_skill(skill_id) [Torrin]
  → llm.refine_skill(existing_skill, conversation, feedback) [Griffin, Gemini Pro]
  → LLM returns updated fields + change summary
  → Orchestration builds SkillUpdate from LLM output
  → db.update_skill(skill_id, updates: SkillUpdate) [Torrin]
  → Return UpdateResponse
```

### Notes
- Skill updates are additive — they refine, not replace
- The `changes` list is for human consumption (demo, logging)
- Version number is a simple integer counter, not semantic versioning
- If skill_id doesn't exist, return 404

---

## Error Handling

All endpoints return standard HTTP errors:

| Code | When |
|------|------|
| 200 | Success |
| 400 | Invalid request (bad query, missing fields) |
| 404 | Skill not found (update/get by ID) |
| 500 | Internal error (DB down, LLM failure) |

Error response body:

```python
class ErrorResponse(BaseModel):
    error: str            # Machine-readable error code
    detail: str           # Human-readable description
```

Keep error messages useful. `"Neo4j connection failed: timeout after 5s"` > `"Internal server error"`.

---

## DB Layer Contracts (`src/db/queries.py`)

Canonical function signatures — code and docs must match these:

```python
async def hybrid_search(
    query_embedding: list[float],   # Pre-computed by orchestration layer
    query_text: str,                # Raw text for keyword search
    top_k: int = 5,
    min_score: float = 0.0,
) -> list[dict]:                    # [{"skill": Skill, "score": float}]

async def create_skill(skill: Skill) -> Skill

async def get_skill(skill_id: str) -> Skill | None

async def update_skill(skill_id: str, updates: SkillUpdate) -> Skill
    # Applies partial updates, increments version. Raises ValueError if not found.

async def check_duplicate(
    embedding: list[float],         # Pre-computed by orchestration layer
    threshold: float = 0.95,
) -> Skill | None                   # Returns existing skill if similarity > threshold
```

The DB layer never computes embeddings — it only accepts pre-computed vectors from the orchestration layer.

---

## Endpoint Summary

| Method | Path | Tool | Handler |
|--------|------|------|---------|
| POST | `/search` | Search Skills | `server.search_handler` |
| POST | `/create` | Create Skill | `server.create_handler` |
| POST | `/update` | Update Skill | `server.update_handler` |
| GET | `/health` | — | Return 200 if server + DB are up |
