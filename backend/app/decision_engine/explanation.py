from __future__ import annotations

from backend.app.decision_engine.lifecycle import LifecyclePrediction
from backend.app.decision_engine.pricing import PricingRecommendation
from backend.app.decision_engine.roi import ROIPrediction
from backend.app.decision_engine.rules import RuleAdjustment


def generate_explanation(
    product_title: str,
    scores: dict[str, float],
    lifecycle: LifecyclePrediction,
    decision: str,
    pricing: PricingRecommendation,
    roi: ROIPrediction,
    adjustments: list[RuleAdjustment],
) -> str:
    rule_text = " ".join(item.reason for item in adjustments[:2])
    return (
        f"{product_title} is currently in the {lifecycle.stage} stage with {lifecycle.confidence}% confidence. "
        f"7-day sales growth is {lifecycle.metrics.sales_growth_7d:.0f}% and creator growth is {lifecycle.metrics.creator_growth_rate:.0f}%. "
        f"Growth score {scores['growth_score']:.0f}, competition score {scores['competition_score']:.0f}, supply score {scores['supply_score']:.0f}. "
        f"Recommended decision: {decision}. Main test price: ${pricing.recommended_price_main:.2f}. "
        f"Expected test ROI: {roi.roi:.1f}x. {rule_text}".strip()
    )
