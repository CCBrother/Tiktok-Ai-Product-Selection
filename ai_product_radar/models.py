from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductSignal:
    product_name: str
    category: str
    signal_source: str
    tiktok_mentions_7d: float
    mention_growth_pct_7d: float
    creator_count_7d: float
    avg_video_engagement_pct: float
    shop_competitor_count: float
    amazon_review_count: float
    unit_cost_usd: float
    target_price_usd: float
    shipping_complexity: float
    copy_difficulty: float
    problem_intensity: float
    visual_demo_score: float
    impulse_buy_score: float
    compliance_risk: float
    rating_avg: float = 0.0
    rating_count: float = 0.0
    days_since_first_seen: float = 0.0
    supplier_count: float = 0.0
    inventory_depth: float = 0.0
    sales_growth_pct_7d: float = 0.0
    sales_growth_pct_30d: float = 0.0
    creator_growth_pct: float = 0.0
    seller_count: float = 0.0
    review_sentiment_score: float = 0.0
    lifecycle_stage: str = ""
    min_order_quantity: float = 0.0
    lead_time_days: float = 0.0
    avg_price_stability: float = 0.0
    moq_feasibility: float = 0.0
    lead_time_speed: float = 0.0
    shipping_cost_estimation: float = 0.0
    brand_strength: float = 0.0
    patent_risk: float = 0.0
    content_complexity: float = 0.0
    production_complexity: float = 0.0
    influencer_dependency: float = 0.0
    content_creation_ease: float = 0.0
    interaction_velocity: float = 0.0
    notes: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def gross_margin_pct(self) -> float:
        if self.target_price_usd <= 0:
            return 0.0
        return max(0.0, (self.target_price_usd - self.unit_cost_usd) / self.target_price_usd * 100)

    @property
    def landed_profit_usd(self) -> float:
        return max(0.0, self.target_price_usd - self.unit_cost_usd)


@dataclass(frozen=True)
class ScoreBreakdown:
    growth_score: int
    trend_score: int
    competition_score: int
    profit_score: int
    review_score: int
    lifecycle_score: int
    supply_score: int
    copy_difficulty_score: int
    content_score: int
    viral_score: int
    risk_score: int
    easy_copy_score: int
    blue_ocean_score: int
    risk_penalty: int
    weights: dict[str, float]
    ai_score: int
    explanation: str
    opportunity_score: int = 0
    confidence_score: int = 0
    momentum_score: int = 0
    acceleration_score: int = 0
    decay_score: int = 0
    anomaly_adjustment: int = 0
    lifecycle_stage: str = ""
    lifecycle_confidence: int = 0


@dataclass(frozen=True)
class Decision:
    recommendation_level: str
    reasoning: str
    risk_analysis: str
    suggested_price_min_usd: float
    suggested_price_max_usd: float
    suggested_procurement_cost_usd: float
    explanation_bundle: dict[str, object] = field(default_factory=dict)
