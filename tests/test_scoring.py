from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import NORMALIZED_WEIGHTS, score_product


def make_product(**overrides):
    base = dict(
        product_name="Test Product",
        category="Test",
        signal_source="Unit Test",
        tiktok_mentions_7d=100,
        mention_growth_pct_7d=100,
        creator_count_7d=10,
        avg_video_engagement_pct=5,
        shop_competitor_count=40,
        amazon_review_count=500,
        unit_cost_usd=5,
        target_price_usd=20,
        shipping_complexity=2,
        copy_difficulty=2,
        problem_intensity=3,
        visual_demo_score=3,
        impulse_buy_score=3,
        compliance_risk=1,
    )
    base.update(overrides)
    return ProductSignal(**base)


def test_stronger_viral_signals_increase_ai_score():
    weak = score_product(make_product())
    strong = score_product(
        make_product(
            tiktok_mentions_7d=700,
            mention_growth_pct_7d=290,
            creator_count_7d=60,
            avg_video_engagement_pct=11,
            visual_demo_score=5,
            impulse_buy_score=5,
        )
    )

    assert strong.ai_score > weak.ai_score


def test_high_risk_reduces_score():
    low_risk = score_product(make_product(compliance_risk=1, shipping_complexity=1, copy_difficulty=1))
    high_risk = score_product(make_product(compliance_risk=5, shipping_complexity=5, copy_difficulty=5))

    assert low_risk.ai_score > high_risk.ai_score


def test_final_score_is_weighted_sum():
    score = score_product(
        make_product(
            sales_growth_pct_7d=240,
            seller_count=20,
            review_sentiment_score=82,
            lifecycle_stage="上升",
            supplier_count=35,
            min_order_quantity=80,
            lead_time_days=9,
            content_creation_ease=5,
            interaction_velocity=90,
        )
    )

    expected = round(
        score.growth_score * NORMALIZED_WEIGHTS["growth_score"]
        + score.trend_score * NORMALIZED_WEIGHTS["trend_score"]
        + score.competition_score * NORMALIZED_WEIGHTS["competition_score"]
        + score.profit_score * NORMALIZED_WEIGHTS["profit_score"]
        + score.review_score * NORMALIZED_WEIGHTS["review_score"]
        + score.lifecycle_score * NORMALIZED_WEIGHTS["lifecycle_score"]
        + score.supply_score * NORMALIZED_WEIGHTS["supply_score"]
        + score.copy_difficulty_score * NORMALIZED_WEIGHTS["copy_difficulty_score"]
        + score.content_score * NORMALIZED_WEIGHTS["content_score"]
        + score.viral_score * NORMALIZED_WEIGHTS["viral_score"]
    )

    assert score.ai_score == expected


def test_growth_score_uses_sales_growth_when_available():
    weak_sales = score_product(make_product(mention_growth_pct_7d=300, sales_growth_pct_7d=20))
    strong_sales = score_product(make_product(mention_growth_pct_7d=20, sales_growth_pct_7d=300))

    assert weak_sales.growth_score < strong_sales.growth_score
