import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class ConversationMetrics:
    conversation_id: str
    resolved: bool
    model_used: str  # "flash" or "pro"
    skill_found: bool  # Did judge pick a matching skill? (skill is not None)
    used_pro_fallback: bool  # Did we fall back to Pro because no skill matched?
    resolution_time_ms: float = 0.0


@dataclass
class AggregateMetrics:
    total_conversations: int = 0
    resolution_rate: float = 0.0
    flash_ratio: float = 0.0  # Fraction of queries handled by Flash
    judge_hit_rate: float = 0.0  # Fraction where judge picked a skill
    pro_fallback_rate: float = 0.0  # Fraction that fell back to Pro
    avg_resolution_time_ms: float = 0.0


class MetricsTracker:
    def __init__(self):
        self._metrics: list[ConversationMetrics] = []
        self._checkpoints: list[dict] = []

    def record(self, metrics: ConversationMetrics):
        self._metrics.append(metrics)

    def aggregate(self) -> AggregateMetrics:
        if not self._metrics:
            return AggregateMetrics()

        n = len(self._metrics)
        resolved = sum(1 for m in self._metrics if m.resolved)
        flash = sum(1 for m in self._metrics if m.model_used == "flash")
        hits = sum(1 for m in self._metrics if m.skill_found)
        fallbacks = sum(1 for m in self._metrics if m.used_pro_fallback)
        times = [m.resolution_time_ms for m in self._metrics if m.resolution_time_ms > 0]

        return AggregateMetrics(
            total_conversations=n,
            resolution_rate=resolved / n,
            flash_ratio=flash / n,
            judge_hit_rate=hits / n,
            pro_fallback_rate=fallbacks / n,
            avg_resolution_time_ms=sum(times) / len(times) if times else 0.0,
        )

    def checkpoint(self, label: str = ""):
        agg = self.aggregate()
        self._checkpoints.append({
            "label": label or f"checkpoint_{len(self._checkpoints)}",
            "timestamp": time.time(),
            "conversations_so_far": len(self._metrics),
            "metrics": asdict(agg),
        })

    def export_json(self, output_path: str):
        data = {
            "conversations": [asdict(m) for m in self._metrics],
            "checkpoints": self._checkpoints,
            "final": asdict(self.aggregate()),
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
