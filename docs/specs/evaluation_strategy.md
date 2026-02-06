# Evaluation Strategy

How we measure that the system actually learns and improves over time.

## Primary Metrics

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **Resolution rate** | % of conversations resolved successfully | +15-25pp over baseline |
| **Flash/Pro ratio** | % of queries handled by Flash (cached skills) vs Pro (reasoning) | 60-70% fewer Pro calls after ~100 conversations |
| **Search hit rate** | % of queries where search returns a relevant skill (score > min_score) | Increasing over time as skills accumulate |

## Ground Truth: kb.json

The ABCD dataset includes `data/abcd/data/kb.json` — a mapping from each subflow to its required action sequence. This is the ground truth "skill set" the system should learn.

Example:
```
"recover_password": ["pull-up-account", "enter-details", "make-password"]
"return_size":      ["pull-up-account", "search-order", "select-order", "make-return"]
```

55 subflows, each with a defined action sequence. Our system should eventually produce skill documents that capture these resolution patterns.

## Evaluation Flow

### Phase 1: Baseline (no skills)

- Process dev split conversations (1,004 conversations)
- No skills in the database — every query goes to Gemini Pro
- Record: resolution rate, response time, model usage
- This establishes the flat baseline

### Phase 2: Learning Loop (train split)

- Process train conversations sequentially (8,034 conversations)
- After each successful resolution → Create Skill
- After each search hit → Update Skill with new data
- Checkpoint metrics every 100 conversations to show the learning curve

### Phase 3: Post-Learning Evaluation (dev split)

- Re-run dev split conversations against learned skills
- Compare to Phase 1 baseline
- Record: resolution rate, Flash ratio, search hit rate, avg score

## Resolution Heuristic

Since ABCD conversations are complete transcripts, we determine resolution by:

1. **Action sequence match**: Compare agent actions in the conversation to the expected actions from `kb.json` for that subflow. Full match = resolved.
2. **Partial match scoring**: Count how many expected actions appear in the conversation. Score = matched / expected.
3. **Escalation detection**: Check for escalation indicators in the last turns (e.g., "transfer to supervisor", "I'll escalate this"). Escalation = unresolved.
4. **Sentiment proxy**: Check last customer utterance for satisfaction signals ("thank you", "that worked") vs frustration signals ("this is ridiculous", "let me speak to").

The primary metric is action sequence match. Sentiment is a secondary signal.

## Demo Script

Three conversations from the dev split, chosen to tell the story:

1. **Simple/common flow** (e.g., `recover_password` — many training examples)
   - Baseline: Pro handles it (slow but works)
   - After learning: Flash retrieves skill instantly
   - Story: Even for simple cases, learning helps

2. **Complex/rare flow** (e.g., multi-step return with conditions)
   - Baseline: Pro reasons from scratch (slow)
   - First encounter: Pro creates a skill
   - Story: The system encounters something new and learns

3. **Repeat of complex flow**
   - After learning: Flash retrieves the skill created in step 2
   - Story: What was slow is now fast. The system improved.

## Expected Results

| Metric | Baseline | After 100 convos | After 500 convos |
|--------|----------|-------------------|-------------------|
| Resolution rate | ~55-60% | ~65-70% | ~75-80% |
| Flash ratio | 0% | ~40% | ~65% |
| Search hit rate | 0% | ~35% | ~60% |
| Avg response time | ~3-5s | ~2-3s | ~1-2s |

These are estimates. Actual numbers depend on skill extraction quality and search accuracy.

## Metrics Implementation

- `src/eval/metrics.py` — `ConversationMetrics` (per-conversation), `AggregateMetrics` (computed), `MetricsTracker` (accumulator with checkpoints)
- `src/eval/harness.py` — `EvaluationHarness` runs baseline and learning phases (stubbed until search/create work)
- Output: JSON file with per-conversation metrics, checkpoints, and final aggregates

## What's NOT Measured (by design)

- Individual skill quality (too subjective for a hackathon)
- User satisfaction (ABCD is pre-recorded, no live users)
- Latency breakdown by component (nice to have, not critical for demo)
- Skill deduplication accuracy (check manually if needed)
