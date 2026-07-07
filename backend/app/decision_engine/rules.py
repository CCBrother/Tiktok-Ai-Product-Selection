from __future__ import annotations

from dataclasses import dataclass

from backend.app.utils.math import clamp


@dataclass(frozen=True)
class RuleAdjustment:
    name: str
    delta: float
    reason: str
    max_score: float | None = None


def apply_decision_rules(scores: dict[str, float], lifecycle_stage: str) -> list[RuleAdjustment]:
    adjustments: list[RuleAdjustment] = []

    if scores["growth_score"] > 80 and scores["competition_score"] > 70:
        adjustments.append(
            RuleAdjustment(
                name="high_growth_low_competition",
                delta=6,
                reason="High growth with favorable low-competition conditions.",
            )
        )

    if scores["virality_score"] > 90 and scores["competition_score"] < 40:
        adjustments.append(
            RuleAdjustment(
                name="viral_but_saturated",
                delta=-8,
                reason="Viral signal is strong, but seller/listing saturation is already high.",
            )
        )

    if scores["supply_score"] < 50:
        adjustments.append(
            RuleAdjustment(
                name="supply_risk",
                delta=-12,
                reason="Supply score is below 50, so launch priority is capped until sourcing risk improves.",
                max_score=69,
            )
        )

    if lifecycle_stage == "RISING":
        adjustments.append(
            RuleAdjustment(
                name="rising_lifecycle",
                delta=5,
                reason="Product is in the Rising stage, so timing priority increases.",
            )
        )
    elif lifecycle_stage == "PEAK":
        adjustments.append(
            RuleAdjustment(
                name="peak_lifecycle",
                delta=-6,
                reason="Product appears near Peak stage, so priority is reduced.",
            )
        )

    return adjustments


def apply_adjustments(base_score: float, adjustments: list[RuleAdjustment]) -> float:
    score = base_score + sum(item.delta for item in adjustments)
    for item in adjustments:
        if item.max_score is not None:
            score = min(score, item.max_score)
    return round(clamp(score), 2)
