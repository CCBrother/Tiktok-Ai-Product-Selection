from __future__ import annotations

from dataclasses import dataclass

from backend.app.autonomous_radar.opportunity import OpportunityObject
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.utils.math import clamp


@dataclass(frozen=True)
class RankedOpportunity:
    product: Product
    score: AIScore
    opportunity: OpportunityObject
    radar_score: float

    def to_dict(self) -> dict:
        return {
            "product_id": self.product.product_id,
            "title": self.product.title,
            "radar_score": self.radar_score,
            "stage": self.opportunity.stage,
            "reason": self.opportunity.reason,
        }


LIFECYCLE_TIMING = {"NEW": 74, "RISING": 94, "HOT": 88, "PEAK": 55, "DECLINING": 25, "DEAD": 5}


def radar_score(score: AIScore, opportunity: OpportunityObject, creative_potential: float | None = None) -> float:
    creative = creative_potential if creative_potential is not None else (float(score.trend_score) + float(score.virality_score)) / 2
    total = (
        opportunity.opportunity_score * 0.25
        + LIFECYCLE_TIMING.get(opportunity.stage, 55) * 0.20
        + float(score.competition_score) * 0.15
        + float(score.profit_score) * 0.15
        + float(score.supply_score) * 0.15
        + creative * 0.10
    )
    return round(clamp(total), 2)


def rank_opportunities(candidates: list[tuple[Product, AIScore, OpportunityObject]]) -> list[RankedOpportunity]:
    ranked = [RankedOpportunity(product, score, opportunity, radar_score(score, opportunity)) for product, score, opportunity in candidates]
    return sorted(ranked, key=lambda item: item.radar_score, reverse=True)
