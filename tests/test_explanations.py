from ai_product_radar.explanations import generate_explanations
from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import decide_product, score_product


def make_product(**overrides):
    base = dict(
        product_name="Test Product",
        category="Test",
        signal_source="Unit Test",
        tiktok_mentions_7d=500,
        mention_growth_pct_7d=220,
        creator_count_7d=35,
        avg_video_engagement_pct=9,
        shop_competitor_count=24,
        amazon_review_count=700,
        unit_cost_usd=4,
        target_price_usd=19.99,
        shipping_complexity=2,
        copy_difficulty=2,
        problem_intensity=4,
        visual_demo_score=5,
        impulse_buy_score=4,
        compliance_risk=1,
        supplier_count=20,
        min_order_quantity=80,
        lead_time_days=10,
        lifecycle_stage="上升",
    )
    base.update(overrides)
    return ProductSignal(**base)


def test_explanation_bundle_contains_g_group_outputs():
    product = make_product()
    score = score_product(product)
    bundle = generate_explanations(product, score)

    assert bundle.gpt_explanation
    assert bundle.risk_explanation
    assert bundle.recommendation_text
    assert bundle.pricing_suggestion
    assert bundle.sourcing_suggestion
    assert bundle.competition_explanation
    assert bundle.lifecycle_explanation
    assert bundle.virality_explanation
    assert bundle.summary
    assert isinstance(bundle.alerts, list)


def test_decision_includes_explanation_bundle():
    product = make_product()
    decision = decide_product(product, score_product(product))

    assert "summary" in decision.explanation_bundle
    assert "pricing_suggestion" in decision.explanation_bundle
