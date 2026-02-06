"""Run a small eval harness slice for validation before committing to full dataset.

Usage:
    venv/bin/python3 scripts/run_eval_slice.py
    venv/bin/python3 scripts/run_eval_slice.py --dev 50 --train 100
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from src.eval.harness import EvaluationHarness, load_dataset

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "eval_output"

logger = logging.getLogger(__name__)


async def main(dev_size: int, train_size: int, checkpoint_interval: int, clear_legacy: bool = False):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    OUTPUT_DIR.mkdir(exist_ok=True)

    logger.info("Loading datasets...")
    dev = load_dataset("dev")[:dev_size]
    train = load_dataset("train")[:train_size]
    logger.info("Slice: %d dev, %d train conversations", len(dev), len(train))

    harness = EvaluationHarness()
    await harness.setup()
    await harness.clear_eval_skills(clear_legacy=clear_legacy)

    # Phase 1: Baseline
    logger.info("=== Phase 1: Baseline (%d conversations) ===", len(dev))
    baseline = await harness.run_baseline(dev)
    EvaluationHarness.export_dual(baseline, str(OUTPUT_DIR / "baseline.json"))

    # Phase 2: Learning
    logger.info("=== Phase 2: Learning (%d conversations, checkpoint every %d) ===", len(train), checkpoint_interval)
    learning = await harness.run_learning(train, checkpoint_interval=checkpoint_interval)
    EvaluationHarness.export_dual(learning, str(OUTPUT_DIR / "learning.json"))

    skills_created = len(harness._eval_owned_ids)
    if skills_created == 0:
        logger.warning("No eval skills created — results may be inconclusive")

    # Phase 3: Post-Learning
    logger.info("=== Phase 3: Post-Learning (%d conversations) ===", len(dev))
    post = await harness.run_post_learning(dev)
    EvaluationHarness.export_dual(post, str(OUTPUT_DIR / "post_learning.json"))

    # Summary
    b = baseline["eval_scoped"].aggregate()
    p = post["eval_scoped"].aggregate()
    l = learning["eval_scoped"].aggregate()

    print("\n" + "=" * 60)
    print("EVAL SLICE SUMMARY (eval-scoped)")
    print("=" * 60)
    print(f"  Dev slice:         {len(dev)}")
    print(f"  Train slice:       {len(train)}")
    print(f"  Skills created:    {skills_created}")
    print(f"  Baseline hit rate: {b.judge_hit_rate:.1%}")
    print(f"  Learning hit rate: {l.judge_hit_rate:.1%}")
    print(f"  Post-learning:     {p.judge_hit_rate:.1%}")
    print(f"  Improvement:       +{(p.judge_hit_rate - b.judge_hit_rate):.1%}")
    print(f"  Flash ratio:       {b.flash_ratio:.1%} → {p.flash_ratio:.1%}")
    print(f"  Pro fallback:      {b.pro_fallback_rate:.1%} → {p.pro_fallback_rate:.1%}")
    print("=" * 60)
    print(f"  Output: {OUTPUT_DIR}/")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval harness on a small slice")
    parser.add_argument("--dev", type=int, default=100, help="Number of dev conversations (default: 100)")
    parser.add_argument("--train", type=int, default=200, help="Number of train conversations (default: 200)")
    parser.add_argument("--checkpoint", type=int, default=25, help="Checkpoint interval (default: 25)")
    parser.add_argument("--clear-legacy", action="store_true", help="Also remove old un-prefixed eval skills")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.dev, args.train, args.checkpoint, args.clear_legacy))
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        sys.exit(1)
