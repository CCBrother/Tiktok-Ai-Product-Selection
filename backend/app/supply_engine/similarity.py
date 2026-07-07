from __future__ import annotations

from backend.app.utils.math import clamp


def copy_difficulty_score(patent_risk: float, brand_dependency: float, technology_complexity: float, manufacturing_barrier: float) -> float:
    return round(clamp(patent_risk * 0.25 + brand_dependency * 0.2 + technology_complexity * 0.3 + manufacturing_barrier * 0.25), 2)
