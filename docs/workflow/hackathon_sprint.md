# Hackathon Sprint Structure

6-hour build. 3 developers. 4 blocks. 3 checkpoints.

## Schedule

| Block | Time | Focus | Exit Criteria |
|-------|------|-------|---------------|
| **0: Setup** | 0:00–0:30 | Git sync, env setup, confirm module ownership | Everyone can run the server locally |
| **1: Infrastructure** | 0:30–2:00 | MCP server skeleton, Neo4j connection, Gemini clients, data loading | Server starts, DB connects, LLM responds |
| **Checkpoint 1** | 2:00 | Quick sync: do interfaces match? Codex review of contracts | |
| **2: Core Logic** | 2:00–3:30 | Search/Create/Update tool implementations, skill CRUD | All 3 tools callable end-to-end |
| **Checkpoint 2** | 3:30 | Integration test: query → search → create → search again | |
| **3: Demo Pipeline** | 3:30–5:00 | Benchmark harness, conversation simulation, visualization | Demo script runs the 3-beat story |
| **Checkpoint 3** | 5:00 | End-to-end test of full demo flow | |
| **4: Polish** | 5:00–6:00 | Demo prep, slides, presentation practice, edge case fixes | Ready to present |

## Module Ownership (Default)

| Developer | Primary Modules | Block 1 Focus |
|-----------|----------------|---------------|
| **Torrin** | `src/db/`, `src/skills/`, `src/eval/` | Neo4j client + connection, skill schema, data loading |
| **Josh** | `src/server/` | FastAPI MCP server, hosting setup, auth, endpoint wiring |
| **Griffin** | `src/orchestration/`, `src/llm/`, `src/analysis/` | Agent decision logic, Gemini clients, sentiment pipeline |

These are starting points. Shift as needed — communicate when you do.

**Integration note**: Griffin's orchestration layer defines _when_ each tool fires. Josh's server exposes the endpoints. Torrin's DB layer handles the reads/writes. The orchestration → server → DB flow is the critical integration path.

## Checkpoint Protocol

Each checkpoint is a ~5 minute sync:

1. **Stand up**: What's done, what's blocked, what's next
2. **Integration check**: Does my output match your input?
3. **Codex review** (optional): If interfaces feel shaky, run a quick Codex check
4. **Adjust plan**: Re-allocate work if someone is ahead/behind

If you're behind schedule, skip the Codex review. The sync is non-negotiable.

## Coordination Rules

- **Never block on a teammate.** If you need their module, stub the interface and keep going.
- **Merge to main frequently.** Every 30-60 minutes minimum.
- **Shout conflicts immediately.** Don't silently resolve merge conflicts.
- **Specs are pre-loaded.** ADRs and interface specs are in `docs/`. Read them before building.
- **If something breaks main, fix it or revert within 5 minutes.**

## Stubs

When you need a teammate's module that doesn't exist yet:

```python
# stub — replace when Griffin's LLM client lands
async def analyze_sentiment(text: str) -> float:
    return 0.5  # neutral placeholder
```

Mark stubs clearly. They'll get replaced at integration.

## Demo Prep (Block 4)

The last hour is sacred. No new features. Only:
- Bug fixes that affect the demo flow
- The demo script itself
- Presentation talking points
- One full dry run
