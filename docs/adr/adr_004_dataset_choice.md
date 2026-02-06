# ADR 004: Dataset Choice — ABCD over Syncora

**Status**: Accepted
**Date**: 2026-02-05
**Context**: Pre-hackathon data source decision

## Decision

Use the ABCD (Action-Based Conversations Dataset) instead of the Syncora dataset.

## Why ABCD

- **Real human conversations**: 10,042 human-to-human customer service dialogues (not synthetic)
- **Rich metadata**: Each conversation has flow, subflow, scenario details, customer profile, order info
- **Ground truth skills**: `kb.json` maps each of 55 subflows to its required action sequence — this is exactly what our system should learn
- **Structured taxonomy**: `ontology.json` provides 10 flows, ~55 subflows, all actions with parameters
- **Academic credibility**: Published at NAACL 2021, well-documented, MIT license
- **Multiple representations**: `original` field (raw dialogue) and `delexed` field (with action targets and utterance IDs)

## Data Mapping

| ABCD field | Skills-Squared field | Example |
|------------|---------------------|---------|
| `scenario.flow` | `skill.product_area` | "product_defect" |
| `scenario.subflow` | `skill.issue_type` | "return_size" |
| Agent utterances | `skill.resolution` | Step-by-step resolution text |
| `kb.json[subflow]` | Ground truth skill | `["pull-up-account", "search-order", "select-order", "make-return"]` |

## Dataset Stats

- **Train**: 8,034 conversations
- **Dev**: 1,004 conversations
- **Test**: 1,004 conversations
- **Avg turns**: 22 per conversation
- **Flows**: 10 (balanced ~10% each)
- **Subflows**: 96 in conversations, 55 with KB ground truth
- **Unique actions**: 30

## Why Not Syncora

Syncora is synthetic. ABCD is human-generated with richer metadata and ground truth action sequences. The kb.json mapping gives us an objective evaluation target — we can measure whether our learned skills match the expected action sequences.

## Consequences

- All dataset references updated from Syncora to ABCD
- `data/abcd/` contains the cloned ABCD repo with all data files
- Evaluation strategy uses kb.json as ground truth (see `docs/specs/evaluation_strategy.md`)
- `scripts/explore_abcd.py` provides dataset exploration and statistics
