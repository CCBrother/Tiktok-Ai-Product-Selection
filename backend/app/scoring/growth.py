from __future__ import annotations

from backend.app.utils.math import clamp


def growth_score(seven_day_growth: float, thirty_day_growth: float, creator_growth: float) -> float:
    raw = seven_day_growth * 0.4 + thirty_day_growth * 0.3 + creator_growth * 0.3
    return round(clamp(raw), 2)
