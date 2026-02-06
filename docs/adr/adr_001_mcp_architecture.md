# ADR 001: MCP Architecture — FastAPI Server with 3 Tools

**Status**: Accepted
**Date**: 2026-02-05
**Context**: Hackathon architecture decision, pre-sprint

## Decision

Build a FastAPI-based MCP server that exposes exactly 3 tools: Search Skills, Create Skill, Update Skill.

## Why FastAPI

- **Native async**: Neo4j and Gemini calls are I/O-bound. FastAPI's async support means we don't block on DB or LLM latency.
- **Fast to build**: Decorator-based routing, automatic OpenAPI docs, Pydantic validation for free. Three experienced devs can have endpoints up in < 1 hour.
- **MCP-compatible**: The MCP protocol is HTTP + JSON. FastAPI is the natural fit — no framework fighting.
- **Team familiarity**: All three devs have built FastAPI services before.

## Why Exactly 3 Tools

The product is a learning loop: **search** for existing knowledge, **create** new knowledge from successful resolutions, **update** existing knowledge when better patterns emerge. Every other feature is downstream of these three operations.

We considered more granular tools (separate search by keyword vs vector, bulk create, delete, etc.) and rejected them:
- More tools = more interface contracts = more integration risk in 6 hours
- The 3-tool design maps cleanly to the demo's 3-beat story
- Additional operations (delete, bulk import) can be added post-hackathon without changing the core architecture

## Tool Routing

```
Client (Fin/Claude) → MCP Server (FastAPI)
                          ├── /search  → Neo4j hybrid query → return skills
                          ├── /create  → Gemini Pro extraction → Neo4j write → confirm
                          └── /update  → Gemini Pro refinement → Neo4j update → confirm
```

Each tool is a single endpoint. No middleware chains, no plugin systems, no tool orchestration layer. The server is a thin router between the client and the backend services.

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| LangChain/LangGraph | Too much abstraction for 3 tools. Framework overhead > value. |
| Raw HTTP server | Lose Pydantic validation, async support, auto docs. |
| gRPC | Team less familiar. Overkill for a hackathon demo. |
| Serverless (Cloud Functions) | Cold starts hurt the demo. Need persistent Neo4j connections. |

## Consequences

- All three devs can work on their modules independently and integrate at the FastAPI layer
- Server module is Josh's responsibility — Torrin and Griffin build clients that the server calls
- If we need a 4th tool, adding one is trivial (one new endpoint + handler)
