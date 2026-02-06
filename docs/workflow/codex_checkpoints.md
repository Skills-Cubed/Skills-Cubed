# Codex Checkpoints

Lightweight review gates at 3 points during the hackathon. Not full review loops — targeted sanity checks.

## Schedule

| Checkpoint | Time | Trigger | Focus |
|-----------|------|---------|-------|
| **1** | ~2:00 | End of Block 1 (Infrastructure) | Do interface contracts match across modules? |
| **2** | ~3:30 | End of Block 2 (Core Logic) | Does integration work? Any obvious bugs? |
| **3** | ~5:00 | End of Block 3 (Demo Pipeline) | Does the end-to-end demo flow hold? |

## Protocol

Each checkpoint:

1. **Prepare input**: CLAUDE.md + relevant source files + one specific question
2. **Submit to Codex**: Use the reviewer init prompt from `docs/prompts/codex_reviewer_init.md`
3. **Turnaround target**: 5-10 minutes
4. **Act on result**: GO → keep moving. FLAG → fix the flagged issue before proceeding.

## What Codex Reviews

- Interface mismatches between modules (e.g., Search tool expects a field the DB doesn't return)
- Integration risks (e.g., async/sync mismatch, missing error handling at boundaries)
- Obvious bugs that would break the demo flow

## What Codex Does NOT Review

- Code style or formatting
- Documentation completeness
- Test coverage
- Performance optimization
- "Could be better" suggestions

## Verdicts

- **GO**: No blocking issues. Continue building.
- **FLAG**: Specific issue that would break integration or the demo. Must fix before proceeding.

There is no REJECT. We don't have time for rework cycles. If something is flagged, the fix should take < 10 minutes. If it would take longer, note it and work around it.

## Skip Policy

If the team is behind schedule at a checkpoint:
- Skip the Codex review
- Do the team sync anyway (2-3 minutes)
- Focus sync on: "What's blocked? What's the critical path to demo?"

The team sync is non-negotiable. The Codex review is optional.
