# CLAUDE.md

Single source of truth for all Claude Code instances working on this repo.

## Project

Skills-Squared: a continual-learning MCP server for customer support. An AI agent handles support conversations, and Skills-Squared learns from successful resolutions — extracting reusable "skill" documents that turn expensive LLM reasoning into fast cached lookups.

**Data source**: ABCD (Action-Based Conversations Dataset) — 10K+ human-to-human customer service dialogues, 55 intents.

## Team

Three experienced developers, each running their own Claude Code instance on this shared repo:
- **Torrin** — Knowledge base & data layer. Owns Neo4j, schema, hybrid search, skill CRUD write logic, indexing. Leads evaluation: designs and runs tests proving the agent improves over time. Coordinates end-to-end testing once all pieces land.
- **Griffin** — Agent orchestration & learning logic. Owns the decision layer: when to Search vs Create vs Update. Sentiment analysis, pattern extraction, continual learning loop. Defines the integration interface so any external agent can connect to the MCP server. Supports Torrin's evaluation effort.
- **Josh** — Infrastructure & MCP hosting. Owns deployment, connectivity, auth, endpoint config. Gets the prototype hosted for demo day. Designs hosting with general use in mind (not just hackathon). Supports Torrin's evaluation effort.

Ownership is indicative, not exclusive. If you need to touch another module, do it — just mention it in the commit message.

## Tech Stack

- **Server**: FastAPI MCP server (Python 3.11+)
- **Database**: Neo4j on GCP (hybrid search: keyword + vector, no re-indexing on updates)
- **LLM**: Google Gemini Flash (fast tool responses) + Gemini Pro (reflection/extraction)
- **Feedback**: Sentiment analysis on user responses (assumed + confirmed resolution signals)

## Three Core Tools

| Tool | Purpose | Hot path? |
|------|---------|-----------|
| **Search Skills** | Query existing resolution patterns via hybrid search | Yes — every incoming query |
| **Create Skill** | Extract new skill document from successful resolution | No — post-conversation |
| **Update Skill** | Refine existing skill with new conversation data | No — post-conversation |

## Demo Strategy

The demo tells a story in three beats:
1. **Baseline**: Show standard RAG on a simple query — works fine
2. **First encounter**: Complex query with no existing skill — slow (Gemini Pro reasons from scratch)
3. **After learning**: Same complex query — instant (skill was created, Flash retrieves it)

**Benchmark**: Resolution rate improvement curve vs flat baseline RAG over ~100 conversations. Show the learning effect.

**Framing**: Self-reinforcing resolutions, cost reduction (Flash vs Pro), organization-specific knowledge that grows with use.

## Directory Layout

```
Skills-Squared/
├── CLAUDE.md              # You are here
├── CONTRIBUTING.md        # Git conventions, ownership, commit format
├── README.md              # Project overview
├── src/
│   ├── server/            # [Josh] FastAPI MCP server, hosting, auth, endpoints
│   ├── db/                # [Torrin] Neo4j client, queries, indexing, connection
│   ├── skills/            # [Torrin] Skill CRUD logic, schema, write/mutation
│   ├── orchestration/     # [Griffin] Agent decision logic, learning loop, tool routing
│   ├── llm/               # [Griffin] Gemini Flash/Pro clients, prompts
│   ├── analysis/          # [Griffin] Sentiment analysis, pattern extraction
│   ├── eval/              # [Torrin] Evaluation harness, benchmark, improvement tests
│   └── utils/             # Shared helpers (logging, config)
├── tests/                 # Mirror src/ structure
├── data/                  # ABCD dataset (cloned repo)
├── docs/
│   ├── workflow/          # Sprint structure, git protocol, values
│   ├── prompts/           # Claude/Codex init prompts
│   ├── adr/               # Architecture Decision Records
│   └── specs/             # Interface contracts, schemas
└── scripts/               # Setup, demo, benchmarks
```

## Conventions

**Naming**: snake_case for files and functions. PascalCase for classes. ALL_CAPS for constants.

**Imports**: stdlib first, third-party second, local third. Separate with blank lines.

**Error handling**: Let errors surface. Don't wrap everything in try/except. Catch specific exceptions at boundaries (API endpoints, DB calls). Use `raise` not `return None` for unexpected states.

**Commit messages**: `[module] description` — e.g., `[db] add neo4j connection helper`, `[server] wire search endpoint`.

**Type hints**: Use them on function signatures. Skip on obvious locals.

**Tests**: Write them for non-trivial logic. Skip for glue code. Use pytest.

## What NOT To Do

- **No gold-plating**: If it works, ship it. Don't add "nice to have" features.
- **No premature abstraction**: Three similar functions are fine. Don't extract a base class for two implementations.
- **No over-engineering**: No factory patterns, no dependency injection frameworks, no config systems beyond a simple dict or env vars.
- **No blocking**: If you're waiting on a teammate's module, stub the interface and move on.
- **No docstrings on obvious functions**: `def get_skill(skill_id: str)` doesn't need a docstring.
- **No unnecessary files**: Don't create util modules "just in case."

## Reference Docs

- `docs/adr/` — Architecture decisions (MCP architecture, Neo4j choice, LLM strategy)
- `docs/specs/` — Interface contracts (tool specs, skill schema)
- `docs/workflow/` — Sprint structure, git protocol, coordination
- `docs/prompts/` — Init prompts for Claude and Codex instances
