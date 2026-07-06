from __future__ import annotations


RAW_WEIGHTS = {
    "growth_score": 20,
    "trend_score": 15,
    "competition_score": 15,
    "profit_score": 10,
    "supply_score": 10,
    "copy_difficulty_score": 10,
    "viral_score": 10,
    "lifecycle_score": 10,
    "content_score": 5,
    "risk_score": 5,
}

TOTAL_WEIGHT = sum(RAW_WEIGHTS.values())
NORMALIZED_WEIGHTS = {key: value / TOTAL_WEIGHT for key, value in RAW_WEIGHTS.items()}


def aggregate_final_score(component_scores: dict[str, int]) -> int:
    """Aggregate component scores into a 0-100 final score."""
    final_score = sum(component_scores[key] * NORMALIZED_WEIGHTS[key] for key in NORMALIZED_WEIGHTS)
    return round(max(0, min(100, final_score)))
