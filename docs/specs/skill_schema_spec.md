# Skill Schema Specification

A "skill" is a structured document representing a learned resolution pattern. This is what gets stored in Neo4j, returned by search, created from conversations, and refined over time.

## Schema

```python
class Skill(BaseModel):
    # Identity
    skill_id: str             # UUID, generated on creation
    title: str                # Short, descriptive title (e.g., "Password Reset for Enterprise SSO Users")
    version: int = 1          # Incremented on each update

    # Content
    problem: str              # What issue does this skill address?
    resolution: str           # Step-by-step resolution (the actual value)
    conditions: list[str]     # When does this skill apply? (e.g., ["user is on enterprise plan", "SSO is enabled"])
    keywords: list[str]       # Explicit keyword tags for BM25 search

    # Embeddings
    embedding: list[float]    # Vector embedding of problem + resolution text (for semantic search)

    # Metadata
    product_area: str = ""    # e.g., "billing", "authentication", "onboarding"
    issue_type: str = ""      # e.g., "how-to", "bug", "feature-request"
    confidence: float = 0.5   # 0-1, increases with successful uses and positive feedback
    times_used: int = 0       # How many times this skill was returned by search
    times_confirmed: int = 0  # How many times use led to confirmed resolution

    # Timestamps
    created_at: str           # ISO 8601
    updated_at: str           # ISO 8601
```

## Neo4j Node Structure

```cypher
(:Skill {
    skill_id: "uuid-here",
    title: "Password Reset for Enterprise SSO Users",
    version: 1,
    problem: "Customer cannot reset password because...",
    resolution: "1. Navigate to admin console\n2. ...",
    conditions: ["user is on enterprise plan", "SSO is enabled"],
    keywords: ["password", "reset", "SSO", "enterprise"],
    embedding: [0.123, -0.456, ...],  // vector index
    product_area: "authentication",
    issue_type: "how-to",
    confidence: 0.75,
    times_used: 12,
    times_confirmed: 9,
    created_at: "2026-02-05T10:30:00Z",
    updated_at: "2026-02-05T14:15:00Z"
})
```

## Vector Index

```cypher
CREATE VECTOR INDEX skill_embedding IF NOT EXISTS
FOR (s:Skill)
ON (s.embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
}}
```

Embedding dimension is configurable via `EMBEDDING_DIM` env var (default: 768, Gemini embedding model).

**Validation**: A Pydantic `model_validator` on `Skill` enforces that `embedding` is non-empty and has length == `EMBEDDING_DIM` on every construction path (including `create_new()`, `from_neo4j_node()`, and direct construction). `src/utils/config.py` provides `validate_embedding()` as a standalone check for use at other boundaries (e.g., `hybrid_search()` must validate `query_embedding` when implemented).

## Full-Text Index

```cypher
CREATE FULLTEXT INDEX skill_keywords IF NOT EXISTS
FOR (n:Skill)
ON EACH [n.title, n.problem, n.resolution, n.keywords]
```

## Hybrid Search Query

```cypher
// Vector search
CALL db.index.vector.queryNodes('skill_embedding', $top_k, $query_embedding)
YIELD node, score AS vector_score

// Full-text search (in parallel or as fallback)
CALL db.index.fulltext.queryNodes('skill_keywords', $query_text)
YIELD node, score AS keyword_score

// Combine scores (simple weighted average)
// weight_vector = 0.7, weight_keyword = 0.3
```

The exact hybrid scoring formula can be tuned. Start with 70/30 vector/keyword and adjust based on demo results.

### Score Normalization

1. **Vector scores**: Use raw Neo4j vector score as returned (typically [0,1] for cosine). If runtime returns out-of-range values, clamp to [0,1]. Add a smoke test that logs observed score range on first search to catch version/config surprises.
2. **Keyword scores (BM25/fulltext)**: Min-max normalize within result set: `(score - min) / (max - min)`
   - Edge case: if `max == min` (all scores identical), all normalized scores = 1.0
   - Edge case: if only 1 result, normalized keyword score = 1.0
3. **Combined**: `0.7 * norm_vector + 0.3 * norm_keyword`
4. **Clamp** final score to [0.0, 1.0]
5. **min_score filter** is applied AFTER combining and clamping — results below min_score are dropped from the response

## Confidence Scoring

Confidence starts at 0.5 (neutral) and adjusts:
- **+0.1** on each confirmed resolution (`times_confirmed++`)
- **-0.05** on each use without confirmation (used but user sentiment was negative or neutral)
- Clamped to [0.0, 1.0]

This is a simple heuristic. Good enough for the demo. Don't over-engineer the scoring formula.

## Skill Lifecycle

```
Conversation → LLM extraction (Pro) → Create Skill (confidence=0.5)
    → Used in Search → times_used++
        → Positive feedback → times_confirmed++, confidence++
        → Negative feedback → confidence--
    → Update from new conversation → version++, resolution refined
```

## Example Skill Document

```json
{
    "skill_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Resolve Billing Discrepancy for Annual Plan Downgrade",
    "version": 2,
    "problem": "Customer was charged the full annual rate after downgrading mid-cycle. They expect a prorated refund for the remaining months.",
    "resolution": "1. Verify the downgrade date in the billing system\n2. Calculate prorated amount: (remaining_months / 12) * annual_rate\n3. Issue refund via Stripe dashboard\n4. Confirm with customer and provide refund timeline (3-5 business days)\n5. Note: If downgrade was > 30 days ago, escalate to billing manager",
    "conditions": [
        "customer is on annual plan",
        "downgrade occurred mid-billing-cycle",
        "customer requests refund"
    ],
    "keywords": ["billing", "refund", "downgrade", "annual", "prorated"],
    "embedding": [0.123, -0.456, "...768 floats..."],
    "product_area": "billing",
    "issue_type": "how-to",
    "confidence": 0.75,
    "times_used": 8,
    "times_confirmed": 6,
    "created_at": "2026-02-05T10:30:00Z",
    "updated_at": "2026-02-05T14:15:00Z"
}
```

## What NOT To Over-Engineer

- Don't add skill categories, tags, or hierarchies beyond `product_area` and `issue_type`
- Don't build a skill versioning system with diffs — just overwrite and increment version
- Don't add relationships between skills (e.g., "prerequisite") during the hackathon — the graph supports it later
- Don't validate every field on every operation — trust the LLM output for now, validate at boundaries
