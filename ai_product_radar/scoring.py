from __future__ import annotations

import math

from .explanations import generate_explanations
from .models import Decision, ProductSignal, ScoreBreakdown
from .decision_engine import ProductContext, run_ai_decision_engine
from .scoring_engines.config import WEIGHTED_SCORING_CONFIG as RAW_WEIGHTS
from .scoring_engines.final_score import NORMALIZED_WEIGHTS, aggregate_final_score
from .scoring_engines.lifecycle import classify_lifecycle
from .scoring_engines.orchestrator import score_with_engines
from .scoring_engines.utils import clamp, score_inverse, score_log, score_low_one_to_five, score_one_to_five


def score_product(product: ProductSignal) -> ScoreBreakdown:
    result = score_with_engines(product)
    component_scores = result.component_scores

    explanation = build_explanation(
        product,
        viral_score=component_scores["viral_score"],
        blue_ocean_score=result.blue_ocean_score,
        growth_score=component_scores["growth_score"],
        easy_copy_score=component_scores["copy_difficulty_score"],
        profit_score=component_scores["profit_score"],
        risk_penalty=result.risk_penalty,
        ai_score=result.final_score,
    )

    return ScoreBreakdown(
        growth_score=component_scores["growth_score"],
        trend_score=component_scores["trend_score"],
        competition_score=component_scores["competition_score"],
        profit_score=component_scores["profit_score"],
        review_score=component_scores["review_score"],
        lifecycle_score=component_scores["lifecycle_score"],
        supply_score=component_scores["supply_score"],
        copy_difficulty_score=component_scores["copy_difficulty_score"],
        content_score=component_scores["content_score"],
        viral_score=component_scores["viral_score"],
        easy_copy_score=component_scores["copy_difficulty_score"],
        blue_ocean_score=result.blue_ocean_score,
        risk_penalty=result.risk_penalty,
        weights=result.weights,
        ai_score=result.final_score,
        explanation=explanation,
        opportunity_score=result.opportunity_score,
        risk_score=result.risk_score,
        confidence_score=result.confidence_score,
        momentum_score=result.momentum_signals.momentum_score,
        acceleration_score=result.momentum_signals.acceleration_score,
        decay_score=result.momentum_signals.decay_score,
        anomaly_adjustment=result.anomaly_adjustment,
        lifecycle_stage=result.lifecycle_stage,
        lifecycle_confidence=result.lifecycle_confidence,
    )


def score_lifecycle(stage: str, days_since_first_seen: float) -> int:
    return classify_lifecycle(stage, days_since_first_seen).score


def build_explanation(
    product: ProductSignal,
    *,
    viral_score: int,
    blue_ocean_score: int,
    growth_score: int,
    easy_copy_score: int,
    profit_score: int,
    risk_penalty: int,
    ai_score: int,
) -> str:
    strengths: list[str] = []
    cautions: list[str] = []

    if growth_score >= 70:
        growth_text = product.sales_growth_pct_7d or product.mention_growth_pct_7d
        strengths.append(f"近7天增长快（{growth_text:.0f}%）")
    if product.creator_count_7d >= 25:
        strengths.append(f"创作者扩散明显（{product.creator_count_7d:.0f}人）")
    if product.visual_demo_score >= 4:
        strengths.append("视频演示冲击力强")
    if product.impulse_buy_score >= 4:
        strengths.append("适合冲动购买")
    if blue_ocean_score >= 70:
        strengths.append("TikTok Shop 竞争仍偏低")
    if profit_score >= 70:
        strengths.append(f"毛利空间好（约{product.gross_margin_pct:.0f}%）")
    if easy_copy_score >= 70:
        strengths.append("供应链/履约复制较容易")

    if product.compliance_risk >= 4:
        cautions.append("合规风险偏高")
    if product.shipping_complexity >= 4:
        cautions.append("物流复杂度偏高")
    if product.shop_competitor_count >= 120:
        cautions.append("TikTok Shop 同类竞争开始拥挤")
    if viral_score < 45:
        cautions.append("当前病毒传播信号还不够强")
    if risk_penalty >= 70:
        cautions.append("综合风险惩罚偏高")

    strength_text = "、".join(strengths[:4]) if strengths else "信号温和，需继续观察"
    caution_text = "；风险：" + "、".join(cautions[:3]) if cautions else "；主要风险暂低"
    return f"AI评分 {ai_score}/100：{strength_text}{caution_text}。"


def decide_product(product: ProductSignal, score: ScoreBreakdown | None = None) -> Decision:
    score = score or score_product(product)
    explanations = generate_explanations(product, score)
    decision_engine_output = run_ai_decision_engine(ProductContext(product_data=product), score)
    if score.ai_score >= 82 and score.viral_score >= 75:
        level = "S"
    elif score.ai_score >= 72:
        level = "A"
    elif score.ai_score >= 58:
        level = "B"
    else:
        level = "C"

    price_min = round(max(product.unit_cost_usd * 2.6, product.target_price_usd * 0.86), 2)
    price_max = round(max(price_min, product.target_price_usd * 1.12), 2)
    procurement = round(min(product.unit_cost_usd, price_min * 0.36), 2)

    reasoning = (
        f"{level}级：总分 {score.ai_score}/100。"
        f"增长 {score.growth_score}、趋势 {score.trend_score}、竞争 {score.competition_score}、"
        f"机会 {score.opportunity_score}、风险 {score.risk_score}、置信度 {score.confidence_score}。"
        "优先看未来 7-30 天短视频扩散，而不是完整市场规模。"
    )

    return Decision(
        recommendation_level=level,
        reasoning=explanations.gpt_explanation + " " + reasoning,
        risk_analysis=explanations.risk_explanation,
        suggested_price_min_usd=price_min,
        suggested_price_max_usd=price_max,
        suggested_procurement_cost_usd=procurement,
        explanation_bundle={
            **explanations.to_dict(),
            "ai_decision_engine": decision_engine_output.to_dict(),
        },
    )
