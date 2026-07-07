from __future__ import annotations

from dataclasses import asdict, dataclass

from backend.app.decision_engine.explanation import generate_explanation
from backend.app.decision_engine.lifecycle import LifecyclePrediction, lifecycle_score, predict_lifecycle
from backend.app.decision_engine.pricing import PricingRecommendation, recommend_pricing
from backend.app.decision_engine.recommendation import decision_from_level, opportunity_level, recommended_action
from backend.app.decision_engine.roi import ROIPrediction, predict_roi
from backend.app.decision_engine.rules import RuleAdjustment, apply_adjustments, apply_decision_rules
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.utils.math import clamp


WEIGHTS = {
    "growth_score": 0.20,
    "trend_score": 0.15,
    "competition_score": 0.15,
    "profit_score": 0.10,
    "supply_score": 0.10,
    "copy_score": 0.10,
    "virality_score": 0.10,
    "lifecycle_score": 0.10,
}


@dataclass(frozen=True)
class DecisionResult:
    product_id: str
    lifecycle: LifecyclePrediction
    market_opportunity_score: float
    supply_feasibility_score: float
    overall_score: float
    opportunity_level: str
    decision: str
    confidence: int
    reason: str
    recommended_action: str
    pricing: PricingRecommendation
    roi: ROIPrediction
    explanation: str
    rule_adjustments: list[RuleAdjustment]

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "lifecycle": self.lifecycle.stage,
            "lifecycle_confidence": self.lifecycle.confidence,
            "lifecycle_metrics": asdict(self.lifecycle.metrics),
            "market_opportunity_score": self.market_opportunity_score,
            "supply_feasibility_score": self.supply_feasibility_score,
            "overall_score": self.overall_score,
            "opportunity_level": self.opportunity_level,
            "decision": self.decision,
            "confidence": self.confidence,
            "reason": self.reason,
            "recommended_action": self.recommended_action,
            "pricing": asdict(self.pricing),
            "roi": asdict(self.roi),
            "explanation": self.explanation,
            "rules": [asdict(item) for item in self.rule_adjustments],
        }


def build_decision(product: Product, score: AIScore, history: list[ProductSnapshot]) -> DecisionResult:
    lifecycle = predict_lifecycle(history)
    scores = _score_dict(score, lifecycle)
    market_score = _weighted_score(scores)
    supply_feasibility = scores["supply_score"]
    base_score = round(clamp(market_score * 0.7 + supply_feasibility * 0.3), 2)
    adjustments = apply_decision_rules(scores, lifecycle.stage)
    overall = apply_adjustments(base_score, adjustments)
    level = opportunity_level(overall)
    decision = decision_from_level(level)
    latest_raw = history[-1].raw_json if history and history[-1].raw_json else {}
    price = float(product.price or latest_raw.get("price") or 0)
    estimated_cost = float(latest_raw.get("estimated_cost", price * 0.35))
    pricing = recommend_pricing(price, estimated_cost, scores["competition_score"], scores["trend_score"])
    roi = predict_roi(pricing.recommended_price_main, pricing.estimated_cost, scores["virality_score"], overall)
    reason = _reason(level, lifecycle.stage, adjustments)
    confidence = _decision_confidence(overall, lifecycle.confidence, adjustments)
    explanation = generate_explanation(product.title, scores, lifecycle, decision, pricing, roi, adjustments)
    return DecisionResult(
        product_id=product.product_id,
        lifecycle=lifecycle,
        market_opportunity_score=market_score,
        supply_feasibility_score=supply_feasibility,
        overall_score=overall,
        opportunity_level=level,
        decision=decision,
        confidence=confidence,
        reason=reason,
        recommended_action=recommended_action(level),
        pricing=pricing,
        roi=roi,
        explanation=explanation,
        rule_adjustments=adjustments,
    )


def _score_dict(score: AIScore, lifecycle: LifecyclePrediction) -> dict[str, float]:
    return {
        "growth_score": float(score.growth_score),
        "trend_score": float(score.trend_score),
        "competition_score": float(score.competition_score),
        "profit_score": float(score.profit_score),
        "supply_score": float(score.supply_score),
        "copy_score": float(score.copy_score),
        "virality_score": float(score.virality_score),
        "lifecycle_score": lifecycle_score(lifecycle.stage),
    }


def _weighted_score(scores: dict[str, float]) -> float:
    return round(clamp(sum(scores[key] * weight for key, weight in WEIGHTS.items())), 2)


def _reason(level: str, stage: str, adjustments: list[RuleAdjustment]) -> str:
    if adjustments:
        return f"{level} opportunity driven by {stage} lifecycle timing. " + " ".join(item.reason for item in adjustments)
    return f"{level} opportunity based on weighted growth, trend, competition, profit, supply, copy, virality, and lifecycle scores."


def _decision_confidence(score: float, lifecycle_confidence: int, adjustments: list[RuleAdjustment]) -> int:
    distance_confidence = 55 + min(abs(score - 60), 40) * 0.75
    rule_bonus = min(len(adjustments) * 3, 9)
    return round(clamp(distance_confidence * 0.55 + lifecycle_confidence * 0.45 + rule_bonus, 45, 96))
