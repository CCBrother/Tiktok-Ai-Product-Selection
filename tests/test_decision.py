from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.app.decision_engine.engine import build_decision
from backend.app.decision_engine.pricing import recommend_pricing
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot


def make_product() -> Product:
    return Product(product_id="p-decision", title="Portable Mini Blender", category="Kitchen", price=Decimal("24.99"))


def make_score(**overrides) -> AIScore:
    base = dict(
        product_id="p-decision",
        growth_score=Decimal("88"),
        trend_score=Decimal("84"),
        competition_score=Decimal("78"),
        profit_score=Decimal("82"),
        supply_score=Decimal("76"),
        copy_score=Decimal("74"),
        virality_score=Decimal("86"),
        lifecycle_score=Decimal("80"),
        final_score=Decimal("82"),
        recommendation_level="A",
        ai_explanation="Strong opportunity",
    )
    base.update(overrides)
    return AIScore(**base)


def make_rising_history() -> list[ProductSnapshot]:
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    return [
        ProductSnapshot(
            product_id="p-decision",
            snapshot_time=start + timedelta(days=i),
            sales_count=30 + i * i,
            creator_count=3 + i,
            video_count=8 + i * 2,
            shop_count=10 + i // 8,
            engagement_score=Decimal(str(55 + i)),
            raw_json={"estimated_cost": 7.5},
        )
        for i in range(30)
    ]


def test_decision_output_contains_business_fields():
    result = build_decision(make_product(), make_score(), make_rising_history())

    assert result.decision in {"LAUNCH", "TEST", "WATCH", "SKIP"}
    assert result.opportunity_level in {"S", "A", "B", "C", "D"}
    assert result.lifecycle.stage == "RISING"
    assert result.pricing.recommended_price_main >= 19.99
    assert result.roi.roi >= 0
    assert "Recommended decision" in result.explanation


def test_supply_risk_limits_recommendation():
    result = build_decision(make_product(), make_score(supply_score=Decimal("35")), make_rising_history())

    assert result.overall_score <= 69
    assert result.decision in {"WATCH", "SKIP"}


def test_pricing_output_uses_psychological_prices():
    pricing = recommend_pricing(price=24.99, estimated_cost=7.5, competition_score=82, perceived_value_score=85)

    assert pricing.multiplier >= 4
    assert pricing.recommended_price_main in {24.99, 29.99, 34.99, 39.99}
