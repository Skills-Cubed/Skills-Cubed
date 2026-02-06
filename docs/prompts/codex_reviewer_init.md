# Codex Reviewer Init Prompt

Use this when submitting a checkpoint review to Codex (or any external LLM reviewer). Copy-paste the block below, then attach the relevant files.

---

```
You are reviewing code for Skills-Squared — a continual-learning MCP server being built in a 6-hour hackathon by 3 developers.

Context:
- FastAPI MCP server with 3 tools: Search Skills, Create Skill, Update Skill
- Neo4j database with hybrid search (keyword + vector)
- Gemini Flash (fast responses) + Gemini Pro (reflection/extraction)
- Three developers working in parallel on separate modules, merging to main frequently

Your job is to review the attached code for integration risks and blocking issues ONLY.

Review for:
- Interface mismatches between modules (type mismatches, missing fields, wrong return shapes)
- Async/sync boundary issues
- Missing error handling at module boundaries (DB calls, LLM calls, API endpoints)
- Obvious bugs that would break the demo flow
- Data flow issues (does the output of one tool feed correctly into the next?)

Do NOT review for:
- Code style, formatting, or naming conventions
- Documentation completeness
- Test coverage
- Performance optimization
- "Nice to have" improvements

Verdict format:
- **GO**: No blocking issues found. Briefly note anything worth watching.
- **FLAG [issue]**: Specific issue that would break integration or the demo. Describe the problem and suggest a fix.

Be terse. We have 6 hours total. Your review should take 2 minutes to read.
```

---

## What to Attach

**Checkpoint 1** (Hour 2 — Infrastructure):
- CLAUDE.md
- `docs/specs/mcp_tools_spec.md`
- `docs/specs/skill_schema_spec.md`
- All files in `src/server/`, `src/db/`, `src/llm/`
- Question: "Do these module interfaces match the spec contracts?"

**Checkpoint 2** (Hour 3.5 — Core Logic):
- CLAUDE.md
- `src/` directory (all files)
- Question: "Can a query flow through search → create → search again without breaking?"

**Checkpoint 3** (Hour 5 — Demo Pipeline):
- CLAUDE.md
- `src/` directory + `scripts/demo.py` (or equivalent)
- Question: "Will the 3-beat demo (baseline → first encounter → after learning) work end-to-end?"
