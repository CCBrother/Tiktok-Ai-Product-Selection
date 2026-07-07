from __future__ import annotations

from backend.app.utils.math import clamp


def copy_score(brand_risk: float, patent_risk: float, production_difficulty: float) -> float:
    risk = brand_risk * 0.35 + patent_risk * 0.35 + production_difficulty * 0.3
    return round(clamp(100 - risk), 2)
