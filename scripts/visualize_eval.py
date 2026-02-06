"""Generate visualization charts from eval harness JSON output.

Reads JSON files from eval_output/ and produces 3 PNG charts:
  1. Learning curve (hit rate over conversations processed)
  2. Before/after comparison (grouped bars)
  3. Model usage (stacked bars: Flash vs Pro)

Usage:
    venv/bin/python3 scripts/visualize_eval.py
"""

import json
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "eval_output"


def load_json(name: str) -> dict:
    path = OUTPUT_DIR / name
    with open(path) as f:
        return json.load(f)


def chart_learning_curve(learning: dict, baseline: dict):
    """Chart 1: Hit rate over conversations processed during learning phase."""
    checkpoints = learning["eval_scoped"]["checkpoints"]
    if not checkpoints:
        logger.warning("No checkpoints in learning data — skipping learning curve chart")
        return

    xs = [cp["conversations_so_far"] for cp in checkpoints]
    ys = [cp["metrics"]["judge_hit_rate"] * 100 for cp in checkpoints]

    baseline_rate = baseline["eval_scoped"]["final"]["judge_hit_rate"] * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(xs, ys, "b-o", linewidth=2, markersize=6, label="Learning Phase")
    ax.axhline(y=baseline_rate, color="r", linestyle="--", linewidth=1.5, label=f"Baseline ({baseline_rate:.1f}%)")

    ax.set_xlabel("Conversations Processed", fontsize=12)
    ax.set_ylabel("Judge Hit Rate (%)", fontsize=12)
    ax.set_title("Learning Curve: Skill Hit Rate Over Time", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    out = OUTPUT_DIR / "learning_curve.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def chart_comparison(baseline: dict, post: dict):
    """Chart 2: Grouped bar chart comparing baseline vs post-learning metrics."""
    b = baseline["eval_scoped"]["final"]
    p = post["eval_scoped"]["final"]

    metrics = ["judge_hit_rate", "flash_ratio", "pro_fallback_rate"]
    labels = ["Hit Rate", "Flash Ratio", "Pro Fallback Rate"]
    baseline_vals = [b[m] * 100 for m in metrics]
    post_vals = [p[m] * 100 for m in metrics]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar([i - width / 2 for i in x], baseline_vals, width, label="Baseline", color="#e74c3c", alpha=0.85)
    bars2 = ax.bar([i + width / 2 for i in x], post_vals, width, label="Post-Learning", color="#2ecc71", alpha=0.85)

    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title("Before vs After Learning", fontsize=14)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, 105)

    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)

    fig.tight_layout()
    out = OUTPUT_DIR / "comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def chart_model_usage(baseline: dict, learning: dict, post: dict):
    """Chart 3: Stacked bar chart showing Flash vs Pro usage across phases."""
    phases = ["Baseline", "Learning", "Post-Learning"]
    flash_counts = []
    pro_counts = []

    for data in [baseline, learning, post]:
        convs = data["eval_scoped"]["conversations"]
        flash = sum(1 for c in convs if c["model_used"] == "flash")
        pro = sum(1 for c in convs if c["model_used"] == "pro")
        flash_counts.append(flash)
        pro_counts.append(pro)

    x = range(len(phases))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, flash_counts, label="Flash (cached skill)", color="#3498db", alpha=0.85)
    ax.bar(x, pro_counts, bottom=flash_counts, label="Pro (reasoning fallback)", color="#e67e22", alpha=0.85)

    ax.set_ylabel("Conversations", fontsize=12)
    ax.set_title("Model Usage by Phase", fontsize=14)
    ax.set_xticks(list(x))
    ax.set_xticklabels(phases, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, axis="y", alpha=0.3)

    for i in x:
        total = flash_counts[i] + pro_counts[i]
        if total > 0:
            ax.annotate(f"{flash_counts[i]}F / {pro_counts[i]}P",
                        xy=(i, total), xytext=(0, 4), textcoords="offset points",
                        ha="center", fontsize=9)

    fig.tight_layout()
    out = OUTPUT_DIR / "model_usage.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    required = ["baseline.json", "learning.json", "post_learning.json"]
    for name in required:
        if not (OUTPUT_DIR / name).exists():
            print(f"Missing {OUTPUT_DIR / name} — run scripts/run_eval_slice.py first", file=sys.stderr)
            sys.exit(1)

    baseline = load_json("baseline.json")
    learning = load_json("learning.json")
    post = load_json("post_learning.json")

    print("Generating charts...")
    chart_learning_curve(learning, baseline)
    chart_comparison(baseline, post)
    chart_model_usage(baseline, learning, post)
    print("Done.")


if __name__ == "__main__":
    main()
