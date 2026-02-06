# Claude Code Init Prompt

Use this at the start of your Claude Code session. Copy-paste the block below.

---

```
You are helping build Skills-Squared — a continual-learning MCP server for customer support. This is a 6-hour hackathon project (Intercom x Google DeepMind). Three experienced developers are building in parallel, each with their own Claude Code instance.

Read CLAUDE.md first. It is the single source of truth for this project.

Key context:
- FastAPI MCP server with 3 tools: Search Skills, Create Skill, Update Skill
- Neo4j database (GCP) with hybrid search (keyword + vector)
- Gemini Flash for fast tool responses, Gemini Pro for reflection/extraction
- ABCD dataset (10K+ dialogues, 55 intents, JSON format)

Architecture decisions are documented in docs/adr/. Interface contracts are in docs/specs/. Read these before writing code that touches the boundaries.

Ground rules:
- Move fast. No gold-plating, no premature abstraction.
- If you need a module that doesn't exist yet, stub it and keep going.
- Commit messages: [module] description (e.g., [db] add connection helper)
- Merge to main every 30-60 minutes. Rebase before merging.
- Type hints on function signatures. Skip docstrings on obvious functions.
- Let errors surface — no silent exception swallowing.
- Everything serves the demo: baseline RAG → first complex query (slow) → same query after learning (fast).

My role on the team: [STATE YOUR ROLE — e.g., "I'm Torrin — I own src/db/, src/skills/, and src/eval/ (knowledge base, data layer, evaluation)" or "I'm Griffin — I own src/orchestration/, src/llm/, and src/analysis/ (agent logic, learning loop)" or "I'm Josh — I own src/server/ (infrastructure, hosting, auth)"]

Start by reading CLAUDE.md, then the relevant spec in docs/specs/ for my module.
```

---

## Usage

1. Open Claude Code in the Skills-Squared repo
2. Paste the prompt above as your first message
3. Replace `[STATE YOUR ROLE]` with your actual assignment
4. Claude will read CLAUDE.md and the relevant specs, then be ready to build

## Notes

- This prompt is dev-agnostic. All three teammates use the same one.
- The module ownership line is the only thing that differs per developer.
- If the plan changes mid-hackathon (e.g., module reassignment), just tell your Claude instance directly.
