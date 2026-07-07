from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .models import ProductSignal, ScoreBreakdown


@dataclass(frozen=True)
class ProductContext:
    product_data: ProductSignal
    sales_history: list[dict[str, Any]] = field(default_factory=list)
    video_data: list[dict[str, Any]] = field(default_factory=list)
    creator_data: list[dict[str, Any]] = field(default_factory=list)
    shop_data: list[dict[str, Any]] = field(default_factory=list)
    review_data: list[dict[str, Any]] = field(default_factory=list)
    supply_data: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GoNoGoDecision:
    status: str
    reasons: list[str]


@dataclass(frozen=True)
class PositioningPlan:
    positioning: str
    target_audience: list[str]
    usage_scenarios: list[str]
    emotional_selling_point: str


@dataclass(frozen=True)
class PricingPlan:
    price_min_usd: float
    price_anchor_usd: float
    price_max_usd: float
    cost_min_usd: float
    cost_max_usd: float
    multiplier: float
    rationale: str


@dataclass(frozen=True)
class VideoScript:
    angle: str
    hook_0_3s: str
    problem_3_6s: str
    solution_6_12s: str
    demo_12_20s: str
    reaction_20_25s: str
    cta_25_30s: str


@dataclass(frozen=True)
class SupplyRecommendation:
    supplier_availability: str
    moq: str
    risk: str
    time_to_launch_days: str
    marks: list[str]


@dataclass(frozen=True)
class FinalCeoDecision:
    launch_or_not: str
    why_now: str
    expected_win_rate: str
    expected_lifecycle_days: str
    recommended_budget: str
    expected_roi_range: str


@dataclass(frozen=True)
class DecisionEngineOutput:
    go_no_go: GoNoGoDecision
    positioning: PositioningPlan
    pricing: PricingPlan
    video_scripts: list[VideoScript]
    supply: SupplyRecommendation
    final_decision: FinalCeoDecision

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_ai_decision_engine(context: ProductContext, score: ScoreBreakdown) -> DecisionEngineOutput:
    product = context.product_data
    go_no_go = decide_go_no_go(product, score)
    positioning = generate_positioning(product)
    pricing = generate_pricing(product, score)
    scripts = generate_video_scripts(product, positioning)
    supply = generate_supply_recommendation(product)
    final_decision = generate_final_ceo_decision(product, score, go_no_go, pricing, supply)
    return DecisionEngineOutput(
        go_no_go=go_no_go,
        positioning=positioning,
        pricing=pricing,
        video_scripts=scripts,
        supply=supply,
        final_decision=final_decision,
    )


def decide_go_no_go(product: ProductSignal, score: ScoreBreakdown) -> GoNoGoDecision:
    reasons: list[str] = []
    competition_signal = 100 - score.competition_score
    if score.growth_score > 75:
        reasons.append("Growth Score > 75")
    if competition_signal < 60:
        reasons.append("Competition pressure < 60")
    if score.supply_score > 70:
        reasons.append("Supply Score > 70")

    if len(reasons) == 3:
        status = "GO"
    elif score.ai_score >= 68 and score.growth_score >= 55 and score.supply_score >= 55:
        status = "TEST"
        reasons.append("Core score is strong enough for controlled validation")
    else:
        status = "SKIP"
        reasons.append("Signal strength is below launch threshold")
    return GoNoGoDecision(status=status, reasons=reasons)


def generate_positioning(product: ProductSignal) -> PositioningPlan:
    text = f"{product.product_name} {product.category}".lower()
    if "blender" in text:
        return PositioningPlan(
            positioning="便携健康果昔神器",
            target_audience=["健身人群", "减脂人群", "上班族"],
            usage_scenarios=["办公室", "健身房", "出差"],
            emotional_selling_point="把健康饮食变成随手可做的小仪式。",
        )
    if "pet" in text:
        return PositioningPlan(
            positioning="宠物家庭的高频清洁小工具",
            target_audience=["养猫人群", "养狗人群", "租房宠物家庭"],
            usage_scenarios=["沙发清洁", "衣物清洁", "出门前快速整理"],
            emotional_selling_point="让宠物陪伴更轻松，减少毛发带来的日常烦躁。",
        )
    if "beauty" in text or "makeup" in text:
        return PositioningPlan(
            positioning="低门槛变美效率工具",
            target_audience=["美妆新手", "通勤女性", "旅行人群"],
            usage_scenarios=["早八通勤", "旅行收纳", "夜间护理"],
            emotional_selling_point="用很小的成本，获得看得见的精致感。",
        )
    return PositioningPlan(
        positioning=f"{product.category} 场景下的高频问题解决工具",
        target_audience=["TikTok 冲动购买人群", "实用小工具爱好者", "礼品消费人群"],
        usage_scenarios=["日常家用", "办公室", "旅行或外出"],
        emotional_selling_point="用一个小工具立刻解决一个烦人的日常问题。",
    )


def generate_pricing(product: ProductSignal, score: ScoreBreakdown) -> PricingPlan:
    multiplier = 2.5
    if score.viral_score >= 80:
        multiplier += 0.45
    if score.competition_score >= 75:
        multiplier += 0.35
    if product.visual_demo_score >= 5 or product.problem_intensity >= 5:
        multiplier += 0.35
    if score.competition_score < 50:
        multiplier -= 0.25
    multiplier = min(4.0, max(2.5, multiplier))

    price_min = round(product.unit_cost_usd * max(2.5, multiplier - 0.35), 2)
    price_anchor = round(product.unit_cost_usd * multiplier, 2)
    price_max = round(product.unit_cost_usd * min(4.0, multiplier + 0.45), 2)
    if product.target_price_usd > 0:
        price_anchor = round((price_anchor + product.target_price_usd) / 2, 2)
        price_min = round(max(price_min, product.target_price_usd * 0.8), 2)
        price_max = round(max(price_anchor, min(price_max, product.target_price_usd * 1.25)), 2)

    return PricingPlan(
        price_min_usd=price_min,
        price_anchor_usd=price_anchor,
        price_max_usd=price_max,
        cost_min_usd=round(product.unit_cost_usd * 0.8, 2),
        cost_max_usd=round(product.unit_cost_usd * 1.2, 2),
        multiplier=round(multiplier, 2),
        rationale="Cost × 2.5-4.0，并根据竞争、病毒传播和感知价值调整。",
    )


def generate_video_scripts(product: ProductSignal, positioning: PositioningPlan) -> list[VideoScript]:
    product_name = product.product_name
    audience = positioning.target_audience[0]
    return [
        VideoScript(
            angle="爆款UGC",
            hook_0_3s=f"我以为这只是个普通的 {product_name}，结果...",
            problem_3_6s=f"{audience} 最大的问题是想要方便，但不想增加麻烦。",
            solution_6_12s=f"这个产品把 {positioning.positioning} 做成了随手可用的小工具。",
            demo_12_20s="直接展示开箱、使用步骤、前后对比和关键效果。",
            reaction_20_25s="给一个真实反应：这比我想象中方便太多。",
            cta_25_30s="想看我测 7 天真实体验，评论区告诉我。",
        ),
        VideoScript(
            angle="对比型",
            hook_0_3s="传统方案 vs 这个便携方案，差距有多大？",
            problem_3_6s="传统方案占空间、麻烦、很难坚持。",
            solution_6_12s=f"{product_name} 把步骤压缩到一个更轻的动作。",
            demo_12_20s="左右分屏对比时间、清洁难度、携带难度和最终效果。",
            reaction_20_25s="结论很直接：我会选更容易坚持的那个。",
            cta_25_30s="需要链接和避坑点，可以先收藏。",
        ),
    ]


def generate_supply_recommendation(product: ProductSignal) -> SupplyRecommendation:
    marks: list[str] = []
    if product.supplier_count > 0:
        marks.append("EASY COPY")
    if product.min_order_quantity < 200 or product.min_order_quantity == 0:
        marks.append("GOOD MOQ")
    if product.lead_time_days < 10 or product.lead_time_days == 0:
        marks.append("FAST SHIPPING")
    if product.compliance_risk >= 2:
        marks.append("CERTIFICATION RISK")

    availability = "HIGH" if product.supplier_count >= 50 else "MEDIUM" if product.supplier_count >= 10 else "LOW"
    moq = "LOW" if product.min_order_quantity < 200 or product.min_order_quantity == 0 else "MEDIUM"
    risk = "MEDIUM" if product.compliance_risk >= 2 or product.patent_risk >= 20 else "LOW"
    launch_min = 5 if product.lead_time_days <= 10 or product.lead_time_days == 0 else 10
    launch_max = max(launch_min + 5, int(product.lead_time_days or 7) + 5)
    return SupplyRecommendation(
        supplier_availability=availability,
        moq=moq,
        risk=risk,
        time_to_launch_days=f"{launch_min}-{launch_max} days",
        marks=marks,
    )


def generate_final_ceo_decision(
    product: ProductSignal,
    score: ScoreBreakdown,
    go_no_go: GoNoGoDecision,
    pricing: PricingPlan,
    supply: SupplyRecommendation,
) -> FinalCeoDecision:
    launch = "Launch" if go_no_go.status == "GO" else "Test" if go_no_go.status == "TEST" else "Do not launch"
    win_rate = min(82, max(28, round(score.ai_score * 0.8 + score.viral_score * 0.15)))
    lifecycle = "21-45 days" if score.growth_score >= 75 else "14-30 days" if score.growth_score >= 55 else "7-21 days"
    budget = "$300-$800" if go_no_go.status == "GO" else "$100-$300" if go_no_go.status == "TEST" else "$0"
    roi_low = max(10, round(product.gross_margin_pct * 0.45))
    roi_high = max(roi_low + 20, round(product.gross_margin_pct * 0.9))
    return FinalCeoDecision(
        launch_or_not=launch,
        why_now=f"增长 {score.growth_score}/100、病毒传播 {score.viral_score}/100，仍处于可快速验证窗口。",
        expected_win_rate=f"{win_rate}%",
        expected_lifecycle_days=lifecycle,
        recommended_budget=budget,
        expected_roi_range=f"{roi_low}%-{roi_high}%",
    )
