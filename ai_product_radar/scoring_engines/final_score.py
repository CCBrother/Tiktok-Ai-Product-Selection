from __future__ import annotations

from .config import WEIGHTED_SCORING_CONFIG
from .normalization import normalize_score, normalize_weights


NORMALIZED_WEIGHTS = normalize_weights(WEIGHTED_SCORING_CONFIG)


def aggregate_final_score(component_scores: dict[str, int]) -> int:
    final_score = sum(component_scores[key] * NORMALIZED_WEIGHTS[key] for key in NORMALIZED_WEIGHTS)
    return normalize_score(final_score)
