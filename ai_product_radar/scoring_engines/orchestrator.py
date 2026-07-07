from __future__ import annotations

from dataclasses import dataclass

from ai_product_radar.models import ProductSignal

from .anomaly import apply_anomaly_adjustment, calculate_anomaly_adjustment
from .calibration import calibrate_score
from .competition import calculate_blue_ocean_score, calculate_competition_score
from .confidence import calculate_confidence_score
from .content import calculate_content_score
from .copy import calculate_copy_score
from .final_score import NORMALIZED_WEIGHTS, aggregate_final_score
from .growth import calculate_growth_score
from .lifecycle import classify_lifecycle
from .momentum import MomentumSignals, detect_momentum_signals
from .opportunity import calculate_opportunity_score
from .profit import calculate_profit_score
from .review import calculate_review_score
from .risk import calculate_risk_penalty, calculate_risk_score
from .supply import calculate_supply_score
from .trend import calculate_trend_score
from .virality import calculate_virality_score


@dataclass(frozen=True)
class ScoreEngineResult:
    component_scores: dict[str, int]
    blue_ocean_score: int
    risk_penalty: int
    lifecycle_stage: str
    lifecycle_confidence: int
    momentum_signals: MomentumSignals
    anomaly_adjustment: int
    opportunity_score: int
    risk_score: int
    confidence_score: int
    final_score: int
    weights: dict[str, float]


def score_with_engines(product: ProductSignal) -> ScoreEngineResult:
    copy_score = calculate_copy_score(product)
    lifecycle = classify_lifecycle(product.lifecycle_stage, product.days_since_first_seen)
    momentum = detect_momentum_signals(product)
    risk_score = calculate_risk_score(product, momentum.decay_score)
    component_scores = {
        "growth_score": calculate_growth_score(product),
        "trend_score": calculate_trend_score(product),
        "competition_score": calculate_competition_score(product),
        "profit_score": calculate_profit_score(product),
        "review_score": calculate_review_score(product),
        "lifecycle_score": lifecycle.score,
        "supply_score": calculate_supply_score(product, copy_score),
        "copy_difficulty_score": copy_score,
        "content_score": calculate_content_score(product),
        "viral_score": calculate_virality_score(product),
        "risk_score": risk_score,
    }
    raw_final = aggregate_final_score(component_scores)
    calibrated_final = calibrate_score(raw_final)
    anomaly_adjustment = calculate_anomaly_adjustment(product)
    final_score = apply_anomaly_adjustment(calibrated_final, anomaly_adjustment)
    opportunity_score = calculate_opportunity_score(component_scores, momentum.momentum_score)
    confidence_score = calculate_confidence_score(product, lifecycle.confidence)

    return ScoreEngineResult(
        component_scores=component_scores,
        blue_ocean_score=calculate_blue_ocean_score(product),
        risk_penalty=calculate_risk_penalty(product),
        lifecycle_stage=lifecycle.stage,
        lifecycle_confidence=lifecycle.confidence,
        momentum_signals=momentum,
        anomaly_adjustment=anomaly_adjustment,
        opportunity_score=opportunity_score,
        risk_score=risk_score,
        confidence_score=confidence_score,
        final_score=final_score,
        weights=NORMALIZED_WEIGHTS,
    )
