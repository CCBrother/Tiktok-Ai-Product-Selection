from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import score_product
from ai_product_radar.scoring_engines.anomaly import calculate_anomaly_adjustment
from ai_product_radar.scoring_engines.momentum import detect_momentum_signals
from ai_product_radar.scoring_engines.ranking import rank_products


def make_product(**overrides):
    base = dict(
        product_name="D Engine Product",
        category="Test",
        signal_source="Unit Test",
        tiktok_mentions_7d=180,
        mention_growth_pct_7d=120,
        creator_count_7d=18,
        avg_video_engagement_pct=7,
        shop_competitor_count=35,
        amazon_review_count=600,
        unit_cost_usd=4,
        target_price_usd=18,
        shipping_complexity=2,
        copy_difficulty=2,
        problem_intensity=4,
        visual_demo_score=4,
        impulse_buy_score=4,
        compliance_risk=1,
    )
    base.update(overrides)
    return ProductSignal(**base)


def test_d_group_score_outputs_are_present():
    score = score_product(
        make_product(
            sales_growth_pct_7d=220,
            sales_growth_pct_30d=160,
            creator_growth_pct=140,
            lifecycle_stage="新兴",
            supplier_count=20,
            min_order_quantity=100,
            lead_time_days=10,
            review_sentiment_score=78,
            interaction_velocity=70,
        )
    )

    assert 0 <= score.ai_score <= 100
    assert score.opportunity_score > 0
    assert score.risk_score >= 0
    assert score.confidence_score > 0
    assert score.momentum_score > 0
    assert score.acceleration_score >= 0
    assert score.decay_score >= 0
    assert score.lifecycle_stage == "新兴"
    assert score.lifecycle_confidence > 0


def test_anomaly_adjustment_penalizes_implausible_spike():
    product = make_product(mention_growth_pct_7d=700, creator_count_7d=2)

    assert calculate_anomaly_adjustment(product) < 0


def test_momentum_detects_growth_pressure():
    slow = detect_momentum_signals(make_product(mention_growth_pct_7d=10, creator_count_7d=2, tiktok_mentions_7d=20))
    fast = detect_momentum_signals(make_product(mention_growth_pct_7d=260, creator_count_7d=45, tiktok_mentions_7d=600))

    assert fast.momentum_score > slow.momentum_score


def test_ranking_engine_orders_by_opportunity():
    weak = make_product(product_name="Weak", sales_growth_pct_7d=20, creator_count_7d=3)
    strong = make_product(product_name="Strong", sales_growth_pct_7d=260, creator_count_7d=60, tiktok_mentions_7d=700)
    scored = [(weak, score_product(weak)), (strong, score_product(strong))]

    ranked = rank_products(scored, field="opportunity_score", limit=2)

    assert ranked[0][0].product_name == "Strong"
