# ADR 002: Database Choice — Neo4j

**Status**: Accepted
**Date**: 2026-02-05
**Context**: Hackathon architecture decision, pre-sprint

## Decision

Use Neo4j (hosted on GCP) as the single data store for skill documents, supporting hybrid search (keyword + vector) without requiring re-indexing on updates.

## Why Neo4j

### Hybrid Search Without Re-Indexing

The core requirement is: when a skill is created or updated, it should be searchable immediately — both by keyword and by semantic similarity. Neo4j's vector index supports this natively:

- **Vector search**: Neo4j stores embeddings as node properties and supports approximate nearest neighbor (ANN) search via its vector index. New nodes are indexed on write — no separate re-indexing step.
- **Keyword search**: Cypher full-text indexes handle keyword matching. Also indexed on write.
- **Hybrid**: A single query can combine both, weighted by relevance.

This is critical for the demo. The "after learning" beat depends on a skill being searchable seconds after creation.

### Graph Structure Fits the Domain

Skills aren't flat documents. They have structure:
- A skill **relates to** product areas, issue types, customer segments
- Skills can **reference** other skills (prerequisite knowledge)
- Resolution patterns have **conditional paths** (if X then Y else Z)

Neo4j represents these relationships natively. A future version could traverse the graph to find related skills, build resolution chains, or identify knowledge gaps. We won't build all of this in 6 hours, but the data model supports it.

### GCP Hosting

Neo4j Aura (managed) on GCP. Zero ops. Connection via Bolt driver. Free tier is sufficient for hackathon-scale data.

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| **Pinecone** | Vector-only. No keyword search without a separate system. No graph relationships. |
| **PostgreSQL + pgvector** | Hybrid search possible but requires manual index management. No graph structure. |
| **Elasticsearch** | Good hybrid search, but overkill for our scale. No native graph. More ops overhead. |
| **ChromaDB** | Good for prototyping vector search, but no keyword search, no graph, no managed hosting. |
| **MongoDB Atlas** | Vector search is new and less mature. No graph relationships. |

## Connection Details

- **Driver**: `neo4j` Python package (official Bolt driver)
- **Auth**: URI + username + password via environment variables
- **Connection pooling**: Use the driver's built-in pool (default settings are fine for hackathon)

```python
from neo4j import AsyncGraphDatabase

driver = AsyncGraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
)
```

## Consequences

- Torrin owns the DB layer (`src/db/`) and skill write logic (`src/skills/`). All Neo4j queries go through these modules.
- Josh's server and Griffin's orchestration layer never talk to Neo4j directly — they call functions in `src/db/` or `src/skills/`.
- Embedding generation happens in the LLM layer (Griffin) before being passed to the DB layer for storage.
- Torrin also owns evaluation (`src/eval/`) — running tests against prior conversation data to prove the knowledge base improves over time.
- If Neo4j Aura has issues during the hackathon, we can fall back to a local Docker instance.
