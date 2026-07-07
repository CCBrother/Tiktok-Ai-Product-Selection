from __future__ import annotations

from .scoring_engines.config import WEIGHTED_SCORING_CONFIG as RAW_WEIGHTS


TOTAL_WEIGHT = sum(RAW_WEIGHTS.values())
NORMALIZED_WEIGHTS = {key: value / TOTAL_WEIGHT for key, value in RAW_WEIGHTS.items()}


def aggregate_final_score(component_scores: dict[str, int]) -> int:
    final_score = sum(component_scores.get(key, 0) * NORMALIZED_WEIGHTS[key] for key in NORMALIZED_WEIGHTS)
    return round(max(0, min(100, final_score)))

__all__ = ["RAW_WEIGHTS", "NORMALIZED_WEIGHTS", "aggregate_final_score"]
