from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.app.autonomous_radar.agent import decide_candidate
from backend.app.autonomous_radar.feedback import calculate_prediction_accuracy
from backend.app.autonomous_radar.notification import format_notification, send_notification
from backend.app.autonomous_radar.opportunity import discover_opportunity
from backend.app.autonomous_radar.ranking import rank_opportunities
from backend.app.autonomous_radar.report import generate_daily_report
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot


def make_product(product_id: str = "radar-1", title: str = "Portable Mini Blender") -> Product:
    return Product(product_id=product_id, title=title, category="Kitchen + Wellness", price=Decimal("29.99"))


def make_score(**overrides) -> AIScore:
    base = dict(
        product_id="radar-1",
        growth_score=Decimal("92"),
        trend_score=Decimal("88"),
        competition_score=Decimal("82"),
        profit_score=Decimal("86"),
        supply_score=Decimal("78"),
        copy_score=Decimal("72"),
        virality_score=Decimal("90"),
        lifecycle_score=Decimal("88"),
        final_score=Decimal("86"),
        recommendation_level="A",
        ai_explanation="Radar candidate",
    )
    base.update(overrides)
    return AIScore(**base)


def make_history(product_id: str = "radar-1") -> list[ProductSnapshot]:
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    return [
        ProductSnapshot(
            product_id=product_id,
            snapshot_time=start + timedelta(days=i),
            sales_count=20 + i * i,
            creator_count=2 + i,
            video_count=5 + i * 2,
            shop_count=8 + i // 8,
            engagement_score=Decimal(str(55 + i)),
            raw_json={},
        )
        for i in range(30)
    ]


def test_opportunity_discovery_detects_candidate():
    opportunity = discover_opportunity(make_product(), make_score(), make_history())

    assert opportunity.opportunity_score > 60
    assert opportunity.stage == "RISING"
    assert "creator growth" in opportunity.reason


def test_ranking_orders_by_radar_score():
    first = (make_product("radar-1", "Strong Product"), make_score(product_id="radar-1"), discover_opportunity(make_product("radar-1"), make_score(product_id="radar-1"), make_history("radar-1")))
    weak_score = make_score(product_id="radar-2", growth_score=Decimal("40"), trend_score=Decimal("35"), supply_score=Decimal("35"))
    second = (make_product("radar-2", "Weak Product"), weak_score, discover_opportunity(make_product("radar-2"), weak_score, make_history("radar-2")))

    ranked = rank_opportunities([second, first])

    assert ranked[0].radar_score >= ranked[1].radar_score


def test_agent_decision_generation():
    opportunity = discover_opportunity(make_product(), make_score(), make_history())
    ranked = rank_opportunities([(make_product(), make_score(), opportunity)])[0]
    decision = decide_candidate(ranked)

    assert decision.decision in {"TEST NOW", "TEST", "WATCH", "SKIP"}
    assert decision.action
    assert decision.expected_outcome


def test_report_generation_contains_daily_sections():
    report = generate_daily_report(
        [
            {
                "product_name": "Portable Mini Blender",
                "reason": "Sales increased 300%",
                "opportunity_score": 93,
                "lifecycle": "RISING",
                "supply_score": 88,
                "creative_angle": "Healthy drinks anywhere",
                "action": "Test within 72 hours",
            }
        ]
    )

    assert "AI Product Radar Daily Report" in report
    assert "TOP S PRODUCTS" in report
    assert "Portable Mini Blender" in report


def test_notification_and_feedback_helpers():
    item = {"product_name": "Portable Blender", "opportunity_score": 93, "lifecycle": "RISING", "action": "Test within 72 hours"}
    message = format_notification(item)
    sent = send_notification(message, channel="telegram")
    accuracy = calculate_prediction_accuracy({"roi": 3.0}, {"roi": 2.7})

    assert "New Opportunity Found" in message
    assert sent["status"] == "queued"
    assert accuracy >= 80
