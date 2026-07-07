from __future__ import annotations

from backend.app.utils.math import clamp


def profit_score(price: float, estimated_cost: float) -> float:
    if price <= 0:
        return 0
    margin = (price - estimated_cost) / price * 100
    return round(clamp(margin * 1.35), 2)
