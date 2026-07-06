from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import ProductSignal, ScoreBreakdown


@dataclass(frozen=True)
class ExplanationBundle:
    gpt_explanation: str
    risk_explanation: str
    recommendation_text: str
    pricing_suggestion: str
    sourcing_suggestion: str
    competition_explanation: str
    lifecycle_explanation: str
    virality_explanation: str
    summary: str
    alerts: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def generate_explanations(product: ProductSignal, score: ScoreBreakdown) -> ExplanationBundle:
    return ExplanationBundle(
        gpt_explanation=generate_gpt_explanation(product, score),
        risk_explanation=generate_risk_explanation(product, score),
        recommendation_text=generate_recommendation_text(product, score),
        pricing_suggestion=generate_pricing_suggestion(product, score),
        sourcing_suggestion=generate_sourcing_suggestion(product, score),
        competition_explanation=generate_competition_explanation(product, score),
        lifecycle_explanation=generate_lifecycle_explanation(product, score),
        virality_explanation=generate_virality_explanation(product, score),
        summary=generate_summary(product, score),
        alerts=generate_alerts(product, score),
    )


def generate_gpt_explanation(product: ProductSignal, score: ScoreBreakdown) -> str:
    return (
        f"{product.product_name} 的最终得分为 {score.ai_score}/100。"
        f"主要驱动来自增长 {score.growth_score}、趋势 {score.trend_score}、"
        f"竞争 {score.competition_score}、利润 {score.profit_score} 和病毒传播 {score.viral_score}。"
        "判断重点是未来 7-30 天在 TikTok Shop 美国站的短视频扩散潜力。"
    )


def generate_risk_explanation(product: ProductSignal, score: ScoreBreakdown) -> str:
    risks: list[str] = []
    if product.compliance_risk >= 4:
        risks.append("法律/平台合规风险偏高")
    if product.copy_difficulty >= 4:
        risks.append("产品结构或供应链复制复杂")
    if product.shipping_complexity >= 4:
        risks.append("物流履约复杂")
    if score.competition_score < 45:
        risks.append("卖家数量较多，竞争拥挤")
    if score.review_score < 35:
        risks.append("评论情感或评价信号偏弱")
    if not risks:
        return "主要风险暂低，仍需在上架前检查侵权、认证、禁限售和真实履约成本。"
    return "风险点：" + "；".join(risks) + "。"


def generate_recommendation_text(product: ProductSignal, score: ScoreBreakdown) -> str:
    if score.ai_score >= 82:
        return "建议进入小批量测试，优先验证素材转化率、退货原因和真实采购成本。"
    if score.ai_score >= 72:
        return "建议进入观察和样品评估，等增长或竞争信号进一步确认后放量。"
    if score.ai_score >= 58:
        return "建议保留在候选池，暂不重仓，重点寻找差异化包装或内容角度。"
    return "暂不建议推进，除非发现新的内容爆点或供应端成本明显下降。"


def generate_pricing_suggestion(product: ProductSignal, score: ScoreBreakdown) -> str:
    price_min = round(max(product.unit_cost_usd * 2.6, product.target_price_usd * 0.86), 2)
    price_max = round(max(price_min, product.target_price_usd * 1.12), 2)
    return f"建议售价区间 ${price_min}-${price_max}，目标毛利率不低于 {min(70, max(45, round(product.gross_margin_pct)))}%。"


def generate_sourcing_suggestion(product: ProductSignal, score: ScoreBreakdown) -> str:
    target_cost = round(max(0.01, min(product.unit_cost_usd, product.target_price_usd * 0.34)), 2)
    if score.supply_score >= 75:
        return f"供应可行性较好，建议目标采购成本控制在 ${target_cost} 以下，并优先找支持低 MOQ 的供应商。"
    return f"供应端仍需验证，建议先询价 3-5 家供应商，目标采购成本不高于 ${target_cost}，重点确认 MOQ 和交期。"


def generate_competition_explanation(product: ProductSignal, score: ScoreBreakdown) -> str:
    seller_count = product.seller_count or product.shop_competitor_count
    if score.competition_score >= 75:
        return f"竞争仍偏蓝海，当前卖家/竞品约 {seller_count:.0f} 个，适合抢先测试。"
    if score.competition_score >= 50:
        return f"竞争中等，当前卖家/竞品约 {seller_count:.0f} 个，需要用内容角度或套装差异化。"
    return f"竞争偏拥挤，当前卖家/竞品约 {seller_count:.0f} 个，不建议只做同质化铺货。"


def generate_lifecycle_explanation(product: ProductSignal, score: ScoreBreakdown) -> str:
    stage = product.lifecycle_stage or infer_lifecycle_stage(score.lifecycle_score)
    return f"生命周期判断为 {stage}，置信参考分 {score.lifecycle_score}/100。"


def generate_virality_explanation(product: ProductSignal, score: ScoreBreakdown) -> str:
    return (
        f"病毒传播分 {score.viral_score}/100。"
        f"近 7 天提及 {product.tiktok_mentions_7d:.0f}，创作者 {product.creator_count_7d:.0f}，"
        f"平均互动率 {product.avg_video_engagement_pct:.1f}%。"
    )


def generate_summary(product: ProductSignal, score: ScoreBreakdown) -> str:
    return (
        f"{product.product_name}：{score.ai_score}/100，"
        f"增长 {score.growth_score}、竞争 {score.competition_score}、利润 {score.profit_score}。"
        f"{generate_recommendation_text(product, score)}"
    )


def generate_alerts(product: ProductSignal, score: ScoreBreakdown) -> list[str]:
    alerts: list[str] = []
    if score.ai_score >= 85:
        alerts.append("高优先级：进入今日 Top 测试清单")
    if score.growth_score >= 85 and score.competition_score >= 70:
        alerts.append("增长快且竞争低：建议 24 小时内复核供应链")
    if score.competition_score < 40:
        alerts.append("竞争预警：同类卖家/商品已明显增多")
    if product.compliance_risk >= 4:
        alerts.append("合规预警：上架前必须检查禁限售、认证和功效宣称")
    if product.lead_time_days >= 30:
        alerts.append("供应预警：交期过长，可能错过 7-30 天窗口")
    return alerts


def infer_lifecycle_stage(lifecycle_score: int) -> str:
    if lifecycle_score >= 90:
        return "新兴"
    if lifecycle_score >= 75:
        return "上升"
    if lifecycle_score >= 50:
        return "高峰"
    return "下降"
