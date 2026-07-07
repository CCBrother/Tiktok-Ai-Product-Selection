from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import NORMALIZED_WEIGHTS, aggregate_final_score, score_product
from ai_product_radar.copy_model import calculate_copy_score
from ai_product_radar.supply import calculate_supply_score


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


def test_aggregation_engine_is_weighted_sum():
    component_scores = {
        "growth_score": 80,
        "trend_score": 53,
        "competition_score": 89,
        "profit_score": 100,
        "review_score": 82,
        "supply_score": 85,
        "copy_difficulty_score": 75,
        "viral_score": 70,
        "lifecycle_score": 86,
        "content_score": 72,
        "risk_score": 88,
    }

    expected = round(sum(component_scores[key] * weight for key, weight in NORMALIZED_WEIGHTS.items()))

    assert aggregate_final_score(component_scores) == expected


def test_score_product_returns_bounded_final_score_with_adjustments():
    score = score_product(make_product(sales_growth_pct_7d=240, lifecycle_stage="上升"))

    assert 0 <= score.ai_score <= 100
    assert score.lifecycle_stage


def test_growth_score_uses_sales_growth_when_available():
    weak_sales = score_product(
        make_product(
            mention_growth_pct_7d=20,
            sales_growth_pct_7d=20,
            sales_growth_pct_30d=100,
            creator_growth_pct=100,
        )
    )
    strong_sales = score_product(
        make_product(
            mention_growth_pct_7d=20,
            sales_growth_pct_7d=300,
            sales_growth_pct_30d=100,
            creator_growth_pct=100,
        )
    )

    assert weak_sales.growth_score < strong_sales.growth_score


def test_growth_model_uses_three_weighted_inputs():
    score = score_product(
        make_product(
            sales_growth_pct_7d=300,
            sales_growth_pct_30d=150,
            creator_growth_pct=1,
        )
    )

    assert score.growth_score == 55


def test_supply_model_uses_five_weighted_inputs():
    product = make_product(
        supplier_count=0,
        avg_price_stability=100,
        moq_feasibility=50,
        lead_time_speed=0,
        lead_time_days=45,
        shipping_cost_estimation=100,
    )

    assert calculate_supply_score(product) == 40


def test_copy_model_subtracts_risk_terms():
    easy = calculate_copy_score(
        make_product(
            brand_strength=0,
            patent_risk=0,
            content_complexity=0,
            production_complexity=0,
            influencer_dependency=0,
            compliance_risk=1,
            copy_difficulty=1,
            shipping_complexity=1,
        )
    )
    hard = calculate_copy_score(
        make_product(
            brand_strength=100,
            patent_risk=100,
            content_complexity=100,
            production_complexity=100,
            influencer_dependency=100,
        )
    )

    assert easy == 100
    assert hard == 0
