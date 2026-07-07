from __future__ import annotations

from dataclasses import dataclass

from backend.app.utils.math import clamp


@dataclass(frozen=True)
class RiskResult:
    risk_score: float
    risk_level: str
    categories: dict[str, float]


def analyze_supply_risk(
    supplier_count: int,
    avg_lead_time: float,
    certification_score: float,
    return_risk: float,
    quality_score: float,
) -> RiskResult:
    categories = {
        "quality_risk": clamp(100 - quality_score),
        "supplier_concentration_risk": clamp(100 - supplier_count * 12),
        "logistics_risk": clamp(max(avg_lead_time - 10, 0) * 4),
        "regulation_risk": clamp(100 - certification_score),
        "return_risk": clamp(return_risk),
    }
    risk_score = round(sum(categories.values()) / len(categories), 2)
    level = "LOW" if risk_score < 35 else "MEDIUM" if risk_score < 65 else "HIGH"
    return RiskResult(risk_score=risk_score, risk_level=level, categories=categories)
