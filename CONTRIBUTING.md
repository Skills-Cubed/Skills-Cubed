# Contributing

Three devs, six hours, one repo. Here's how we stay out of each other's way.

## Git Workflow

See `docs/workflow/git_protocol.md` for full details. The essentials:

1. **Branch naming**: `{name}/{module}` — e.g., `torrin/neo4j-client`, `josh/mcp-server`
2. **Merge to main every 30-60 minutes**. Small, frequent merges beat big scary ones.
3. **Pull before branching, rebase before merging.**
4. **No force pushes.**

## Commit Messages

Format: `[module] description`

```
[db] add neo4j connection helper
[server] wire search skills endpoint
[llm] implement gemini flash client
[skills] add skill validation logic
[analysis] add sentiment scoring
[test] add search tool integration test
[docs] update demo script
[fix] handle empty search results
```

Keep it lowercase, imperative, terse.

## Directory Ownership

| Directory | Primary Owner | Description |
|-----------|---------------|-------------|
| `src/server/` | Josh | FastAPI MCP server, hosting, auth, endpoints |
| `src/db/` | Torrin | Neo4j client, queries, indexing, connection |
| `src/skills/` | Torrin | Skill CRUD logic, schema, write/mutation |
| `src/orchestration/` | Griffin | Agent decision logic (search/create/update routing), learning loop |
| `src/llm/` | Griffin | Gemini Flash/Pro clients, prompts |
| `src/analysis/` | Griffin | Sentiment analysis, pattern extraction |
| `src/eval/` | Torrin | Evaluation harness, benchmark, improvement tests |
| `src/utils/` | Shared | Logging, config, helpers |
| `tests/` | Whoever wrote the code | Mirror src/ structure |
| `scripts/` | Shared | Setup, demo, benchmarks |

Ownership means you're the primary author, not the gatekeeper. Anyone can touch any file — just note it in the commit message if you're working outside your area.

## Handling Conflicts

1. **If you hit a merge conflict**: Tell the team immediately. Don't silently resolve it.
2. **If in doubt**: Merge and fix forward. A broken main that gets fixed in 5 minutes is better than a blocked developer.
3. **If two people need the same file**: Coordinate on who goes first. The second person rebases after.

## Code Standards

- Python 3.11+
- Type hints on function signatures
- pytest for tests
- No linter wars during the hackathon — just keep it readable
- See CLAUDE.md for full conventions

## Pull Requests

We're not doing PRs during the hackathon. Merge directly to main. Codex checkpoints at hours 2, 3.5, and 5 serve as lightweight review gates.

Post-hackathon, if development continues, we'll switch to PR-based workflow.
