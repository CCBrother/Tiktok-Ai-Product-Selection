from ai_product_radar.decision_engine import ProductContext, run_ai_decision_engine
from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import decide_product, score_product


def make_product(**overrides):
    base = dict(
        product_name="Portable Mini Blender",
        category="Kitchen + Wellness",
        signal_source="Unit Test",
        tiktok_mentions_7d=820,
        mention_growth_pct_7d=320,
        creator_count_7d=78,
        avg_video_engagement_pct=12.4,
        shop_competitor_count=26,
        amazon_review_count=640,
        unit_cost_usd=7.5,
        target_price_usd=24.99,
        shipping_complexity=2,
        copy_difficulty=1,
        problem_intensity=5,
        visual_demo_score=5,
        impulse_buy_score=5,
        compliance_risk=2,
        sales_growth_pct_7d=320,
        sales_growth_pct_30d=480,
        creator_growth_pct=180,
        seller_count=26,
        supplier_count=86,
        min_order_quantity=100,
        lead_time_days=7,
        avg_price_stability=86,
        moq_feasibility=84,
        lead_time_speed=86,
        shipping_cost_estimation=78,
        patent_risk=8,
        content_creation_ease=5,
        interaction_velocity=62,
    )
    base.update(overrides)
    return ProductSignal(**base)


def test_decision_engine_returns_go_for_strong_product():
    product = make_product()
    score = score_product(product)
    output = run_ai_decision_engine(ProductContext(product_data=product), score)

    assert output.go_no_go.status == "GO"
    assert output.positioning.positioning == "便携健康果昔神器"
    assert output.pricing.multiplier >= 2.5
    assert output.video_scripts[0].hook_0_3s
    assert output.supply.supplier_availability == "HIGH"
    assert output.final_decision.launch_or_not == "Launch"


def test_decision_engine_can_skip_weak_product():
    product = make_product(
        tiktok_mentions_7d=10,
        sales_growth_pct_7d=5,
        sales_growth_pct_30d=4,
        creator_growth_pct=2,
        supplier_count=0,
        min_order_quantity=500,
        lead_time_days=35,
        target_price_usd=12,
        unit_cost_usd=9,
    )
    score = score_product(product)
    output = run_ai_decision_engine(ProductContext(product_data=product), score)

    assert output.go_no_go.status in {"TEST", "SKIP"}
    assert output.final_decision.recommended_budget in {"$0", "$100-$300"}


def test_decide_product_embeds_ai_decision_engine_bundle():
    product = make_product()
    decision = decide_product(product, score_product(product))

    engine = decision.explanation_bundle["ai_decision_engine"]
    assert engine["go_no_go"]["status"] == "GO"
    assert engine["video_scripts"][0]["hook_0_3s"]
    assert "expected_roi_range" in engine["final_decision"]
