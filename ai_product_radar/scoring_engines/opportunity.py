from __future__ import annotations

from .normalization import normalize_score


def calculate_opportunity_score(component_scores: dict[str, int], momentum_score: int) -> int:
    return normalize_score(
        component_scores["growth_score"] * 0.22
        + component_scores["trend_score"] * 0.18
        + component_scores["competition_score"] * 0.18
        + component_scores["profit_score"] * 0.16
        + component_scores["supply_score"] * 0.10
        + component_scores["viral_score"] * 0.10
        + momentum_score * 0.06
    )
