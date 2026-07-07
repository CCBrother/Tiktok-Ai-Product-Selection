from __future__ import annotations


def supply_recommendation(supply_score: float, margin_score: float, risk_score: float, copy_score: float) -> tuple[str, str]:
    if supply_score >= 75 and margin_score >= 60 and risk_score < 45:
        return "SOURCE", "Product has strong demand potential and sufficient suppliers. Recommended initial order: 500 units."
    if supply_score >= 55 and margin_score >= 40 and risk_score < 70:
        return "TEST", "Demand is promising but supply or risk needs validation. Start with small inventory."
    return "AVOID", "Low margin, weak supply, or high copy/supply risk makes this unattractive right now."
