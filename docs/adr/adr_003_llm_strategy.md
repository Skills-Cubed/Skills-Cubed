# ADR 003: LLM Strategy — Gemini Flash + Pro Split

**Status**: Accepted
**Date**: 2026-02-05
**Context**: Hackathon architecture decision, pre-sprint

## Decision

Use a two-tier LLM strategy:
- **Gemini Flash**: Fast, cheap model for real-time tool responses (search result ranking, quick formatting)
- **Gemini Pro**: Capable model for reflection tasks (skill extraction from conversations, sentiment analysis, skill refinement)

## Why Two Tiers

The demo's value proposition is cost reduction through learning. The split makes this concrete:

| Task | Model | Why |
|------|-------|-----|
| Search result ranking/formatting | Flash | Speed. User is waiting. Sub-second response needed. |
| Skill extraction from conversation | Pro | Quality. Extracting structured knowledge from messy conversation text requires reasoning. |
| Sentiment analysis | Flash | Speed + cost. Sentiment is a simpler task. Flash handles it well. |
| Skill refinement/update | Pro | Quality. Merging new information with existing skill requires careful reasoning. |

The learning effect means Pro is called less over time: as the skill library grows, more queries are answered by Search (Flash) instead of reasoning from scratch (Pro). This is the cost curve the benchmark shows.

## Why Gemini (Not OpenAI, Anthropic, etc.)

- **Hackathon sponsor**: Google DeepMind is co-hosting. Gemini API access is provided.
- **Flash is genuinely fast**: Sub-200ms for simple tasks. Good for demo responsiveness.
- **Unified API**: Same SDK for both tiers. One client, two model strings.

## Implementation

Griffin owns `src/llm/`. Single client module, two model configs:

```python
# Conceptual — Griffin will implement the actual client
FLASH_MODEL = "gemini-2.0-flash"
PRO_MODEL = "gemini-2.0-pro"

async def call_flash(prompt: str, **kwargs) -> str:
    """Fast, cheap. Use for search ranking, sentiment, formatting."""
    ...

async def call_pro(prompt: str, **kwargs) -> str:
    """Capable. Use for skill extraction, refinement, complex reasoning."""
    ...
```

## Prompt Management

- Prompts live alongside the code that uses them (not in a separate prompts directory)
- Keep prompts as simple as possible — no few-shot examples unless accuracy requires it
- Structured output via Gemini's JSON mode where possible

## Fallback

If Gemini API has issues during the hackathon:
- Flash tasks → try Pro (slower but works)
- Pro tasks → no fallback. Flag and debug.
- If both are down → the hackathon is effectively paused. Escalate to mentors.

## Consequences

- Griffin builds the LLM client module (`src/llm/`) with two entry points (flash/pro)
- Griffin's orchestration layer (`src/orchestration/`) decides which model to invoke based on the operation (search ranking → Flash, skill extraction → Pro)
- Josh's server calls Griffin's orchestration layer, which calls the appropriate LLM function
- Torrin's evaluation harness (`src/eval/`) tracks which model handled each query to show the cost curve in the benchmark
- Embedding generation (for Neo4j vector search) uses a separate Gemini embedding model. Griffin's LLM/orchestration layer computes embeddings for both write-time (skill creation) and query-time (search). The DB layer never imports LLM code — it only accepts pre-computed vectors.
