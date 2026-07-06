from __future__ import annotations

import math

from .aggregation import NORMALIZED_WEIGHTS, RAW_WEIGHTS, aggregate_final_score
from .copy_model import calculate_copy_score
from .explanations import generate_explanations
from .growth import calculate_growth_score
from .models import Decision, ProductSignal, ScoreBreakdown
from .supply import calculate_supply_score


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_log(value: float, scale: float, cap: float = 100) -> float:
    if value <= 0:
        return 0
    return clamp(math.log1p(value) / math.log1p(scale) * cap)


def score_inverse(value: float, worst: float) -> float:
    return clamp((1 - min(value, worst) / worst) * 100)


def score_one_to_five(value: float) -> float:
    return clamp((value - 1) / 4 * 100)


def score_low_one_to_five(value: float) -> float:
    return clamp((5 - value) / 4 * 100)


def score_product(product: ProductSignal) -> ScoreBreakdown:
    heat = score_log(product.tiktok_mentions_7d, scale=800)
    mention_growth = clamp(product.mention_growth_pct_7d / 300 * 100)
    creator_spread = score_log(product.creator_count_7d, scale=80)
    engagement = clamp(product.avg_video_engagement_pct / 12 * 100)
    visual = score_one_to_five(product.visual_demo_score)
    impulse = score_one_to_five(product.impulse_buy_score)
    problem = score_one_to_five(product.problem_intensity)

    growth_score = calculate_growth_score(product)

    trend_score = round(creator_spread * 0.42 + heat * 0.28 + mention_growth * 0.18 + engagement * 0.12)

    interaction_velocity = product.interaction_velocity or (product.avg_video_engagement_pct * product.tiktok_mentions_7d / 100)
    viral_score = round(clamp(score_log(interaction_velocity, scale=120) * 0.62 + engagement * 0.38))

    seller_count = product.seller_count or product.shop_competitor_count
    low_shop_competition = score_inverse(seller_count, worst=180)
    mature_elsewhere = score_log(product.amazon_review_count, scale=2500)
    signal_without_saturation = clamp((mention_growth * 0.35 + heat * 0.25 + mature_elsewhere * 0.15 + low_shop_competition * 0.25))
    blue_ocean_score = round(signal_without_saturation)
    competition_score = round(low_shop_competition)

    copy_difficulty_score = calculate_copy_score(product)

    margin = clamp(product.gross_margin_pct / 75 * 100)
    profit_score = round(margin)

    review_sentiment = product.review_sentiment_score
    if review_sentiment == 0:
        review_sentiment = clamp((product.rating_avg - 3.2) / 1.8 * 100) if product.rating_avg > 0 else mature_elsewhere * 0.50
    review_score = round(clamp(review_sentiment))

    lifecycle_score = score_lifecycle(product.lifecycle_stage, product.days_since_first_seen)

    supply_score = calculate_supply_score(product)

    content_ease = score_one_to_five(product.content_creation_ease) if product.content_creation_ease > 0 else 0
    content_score = round((content_ease or visual) * 0.45 + impulse * 0.25 + problem * 0.18 + score_low_one_to_five(product.shipping_complexity) * 0.12)

    risk_penalty = round(
        score_one_to_five(product.compliance_risk) * 0.60
        + score_one_to_five(product.shipping_complexity) * 0.20
        + score_one_to_five(product.copy_difficulty) * 0.20
    )
    risk_score = round(100 - risk_penalty)

    component_scores = {
        "growth_score": growth_score,
        "trend_score": trend_score,
        "competition_score": competition_score,
        "profit_score": profit_score,
        "lifecycle_score": lifecycle_score,
        "supply_score": supply_score,
        "copy_difficulty_score": copy_difficulty_score,
        "content_score": content_score,
        "viral_score": viral_score,
        "risk_score": risk_score,
    }
    ai_score = aggregate_final_score(component_scores)

    explanation = build_explanation(
        product,
        viral_score=viral_score,
        blue_ocean_score=blue_ocean_score,
        growth_score=growth_score,
        easy_copy_score=copy_difficulty_score,
        profit_score=profit_score,
        risk_penalty=risk_penalty,
        ai_score=ai_score,
    )

    return ScoreBreakdown(
        growth_score=growth_score,
        trend_score=trend_score,
        competition_score=competition_score,
        profit_score=profit_score,
        review_score=review_score,
        lifecycle_score=lifecycle_score,
        supply_score=supply_score,
        copy_difficulty_score=copy_difficulty_score,
        content_score=content_score,
        viral_score=viral_score,
        risk_score=risk_score,
        easy_copy_score=copy_difficulty_score,
        blue_ocean_score=blue_ocean_score,
        risk_penalty=risk_penalty,
        weights=NORMALIZED_WEIGHTS,
        ai_score=ai_score,
        explanation=explanation,
    )


def score_lifecycle(stage: str, days_since_first_seen: float) -> int:
    normalized = stage.strip().lower()
    stage_scores = {
        "emerging": 92,
        "新兴": 92,
        "rising": 86,
        "上升": 86,
        "peak": 64,
        "高峰": 64,
        "declining": 28,
        "下降": 28,
    }
    if normalized in stage_scores:
        return stage_scores[normalized]
    if days_since_first_seen <= 0:
        return 62
    if days_since_first_seen <= 21:
        return 92
    if days_since_first_seen <= 60:
        return 86
    if days_since_first_seen <= 120:
        return 64
    return 28


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
        strengths.append(f"近7天增长快（{product.mention_growth_pct_7d:.0f}%）")
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

    strength_text = "、".join(strengths[:4]) if strengths else "信号温和，需继续观察"
    caution_text = "；风险：" + "、".join(cautions[:3]) if cautions else "；主要风险暂低"
    return f"AI评分 {ai_score}/100：{strength_text}{caution_text}。"


def decide_product(product: ProductSignal, score: ScoreBreakdown | None = None) -> Decision:
    score = score or score_product(product)
    explanations = generate_explanations(product, score)
    if score.ai_score >= 82 and score.viral_score >= 75:
        level = "S"
    elif score.ai_score >= 72:
        level = "A"
    elif score.ai_score >= 58:
        level = "B"
    else:
        level = "C"

    risks: list[str] = []
    if product.compliance_risk >= 4:
        risks.append("合规风险高，需要先排查平台禁限售、功效宣称和认证要求")
    if product.shipping_complexity >= 4:
        risks.append("履约复杂，可能压低真实利润和发货稳定性")
    if product.shop_competitor_count >= 120:
        risks.append("TikTok Shop 同类供给已经拥挤，需用素材或套装做差异")
    if score.review_score < 35:
        risks.append("评价信号弱，需小批量验证退货率和差评点")
    if not risks:
        risks.append("主要风险暂低，但仍需检查侵权、认证和真实履约成本")

    price_min = round(max(product.unit_cost_usd * 2.6, product.target_price_usd * 0.86), 2)
    price_max = round(max(price_min, product.target_price_usd * 1.12), 2)
    procurement = round(min(product.unit_cost_usd, price_min * 0.36), 2)

    reasoning = (
        f"{level}级：总分 {score.ai_score}/100。"
        f"增长 {score.growth_score}、趋势 {score.trend_score}、竞争 {score.competition_score}、"
        f"利润 {score.profit_score}、内容 {score.content_score}、病毒传播 {score.viral_score}。"
        "优先看未来 7-30 天短视频扩散，而不是完整市场规模。"
    )

    return Decision(
        recommendation_level=level,
        reasoning=explanations.gpt_explanation + " " + reasoning,
        risk_analysis=explanations.risk_explanation,
        suggested_price_min_usd=price_min,
        suggested_price_max_usd=price_max,
        suggested_procurement_cost_usd=procurement,
        explanation_bundle=explanations.to_dict(),
    )
