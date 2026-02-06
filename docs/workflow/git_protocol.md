# Git Protocol

Fast merges, small commits, no surprises.

## Branching

- **Branch naming**: `{name}/{module}` — e.g., `torrin/neo4j-client`, `josh/mcp-server`, `griffin/gemini-client`
- **Branch from main**, always up to date
- **One branch per task**, not per day or per feature area
- **Short-lived branches**: merge within 30-60 minutes

## Workflow

```
git checkout main
git pull origin main
git checkout -b torrin/neo4j-client

# ... do work, commit often ...

git checkout main
git pull origin main
git checkout torrin/neo4j-client
git rebase main
git checkout main
git merge torrin/neo4j-client
git push origin main
git branch -d torrin/neo4j-client
```

## Commit Messages

Format: `[module] description`

Module tags:
- `[server]` — FastAPI, endpoints, tool routing
- `[db]` — Neo4j client, queries, connection
- `[llm]` — Gemini clients, prompts
- `[skills]` — Skill CRUD, schema, validation
- `[analysis]` — Conversation analysis, sentiment
- `[test]` — Tests
- `[scripts]` — Setup, demo, benchmark scripts
- `[docs]` — Documentation
- `[fix]` — Bug fixes
- `[infra]` — Config, deps, CI

Examples:
```
[db] add neo4j connection pool
[server] wire search skills endpoint
[llm] implement gemini flash client with retry
[fix] handle empty vector on new skill creation
[scripts] add demo runner with timing output
```

## Rules

1. **No force pushes.** Ever.
2. **Pull before branching.** Always start from latest main.
3. **Rebase before merging.** Keep history linear.
4. **Merge to main every 30-60 minutes.** Small merges, often.
5. **If you break main, fix or revert within 5 minutes.**

## Conflict Resolution

1. **Tell the team immediately.** Don't silently resolve conflicts.
2. **The person who hit the conflict resolves it** — but ask if unsure.
3. **If in doubt, merge and fix forward.** Speed > perfection.
4. **If two people need the same file**: coordinate who merges first. Second person rebases after.

## What NOT To Do

- Don't sit on a branch for 2 hours
- Don't rewrite history on shared branches
- Don't merge without pulling first
- Don't create branches for single-line fixes (commit directly to main)
