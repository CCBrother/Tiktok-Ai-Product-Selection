from __future__ import annotations

from dataclasses import dataclass

from backend.app.decision_engine.lifecycle import predict_lifecycle
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.services.snapshot_service import calculate_growth
from backend.app.utils.math import clamp


@dataclass(frozen=True)
class OpportunityObject:
    product_id: str
    opportunity_score: float
    reason: str
    stage: str
    signals: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "opportunity_score": self.opportunity_score,
            "reason": self.reason,
            "stage": self.stage,
            "signals": self.signals,
        }


def discover_opportunity(product: Product, score: AIScore, history: list[ProductSnapshot]) -> OpportunityObject:
    growth = calculate_growth(history)
    lifecycle = predict_lifecycle(history)
    signals = {
        "sales_acceleration": max(0, lifecycle.metrics.sales_velocity_change),
        "creator_growth": growth["creator_growth"],
        "video_engagement_spike": growth["engagement_growth"],
        "low_competition": float(score.competition_score),
        "price_margin": float(score.profit_score),
        "supply_feasibility": float(score.supply_score),
    }
    opportunity_score = round(
        clamp(
            clamp(signals["sales_acceleration"]) * 0.18
            + clamp(signals["creator_growth"]) * 0.18
            + clamp(signals["video_engagement_spike"]) * 0.16
            + signals["low_competition"] * 0.16
            + signals["price_margin"] * 0.16
            + signals["supply_feasibility"] * 0.16
        ),
        2,
    )
    reason = (
        f"Sales acceleration {signals['sales_acceleration']:.0f}, creator growth {signals['creator_growth']:.0f}%, "
        f"competition score {signals['low_competition']:.0f}, margin score {signals['price_margin']:.0f}."
    )
    return OpportunityObject(product.product_id, opportunity_score, reason, lifecycle.stage, signals)
