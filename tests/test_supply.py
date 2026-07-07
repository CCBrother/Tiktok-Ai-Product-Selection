from __future__ import annotations

from decimal import Decimal

from backend.app.models.product import Product
from backend.app.supply_engine.cost import calculate_total_cost
from backend.app.supply_engine.engine import analyze_supply
from backend.app.supply_engine.margin import calculate_margin
from backend.app.supply_engine.recommendation import supply_recommendation
from backend.app.supply_engine.risk import analyze_supply_risk
from backend.app.supply_engine.supplier import SupplierProfile, score_supplier


def make_product(**overrides) -> Product:
    base = dict(product_id="supply-1", title="Portable Mini Blender", category="Kitchen + Wellness", price=Decimal("29.99"))
    base.update(overrides)
    return Product(**base)


def test_cost_calculation_includes_all_cost_categories():
    cost = calculate_total_cost(product_cost=6.0, selling_price=29.99, advertising_cost=1.5)

    assert cost.tiktok_fees == 2.4
    assert cost.total_cost > 6
    assert cost.last_mile_shipping > 0


def test_margin_calculation_returns_gross_net_and_roi():
    margin = calculate_margin(selling_price=29.99, total_cost=9.5, supplier_price=6.0, advertising_cost=1.5)

    assert margin.gross_margin > 70
    assert margin.net_margin > 60
    assert margin.roi > 2


def test_supplier_scoring_rewards_low_moq_and_fast_lead_time():
    strong = SupplierProfile("A", "1688", "small appliance", "Zhejiang", 6.2, 50, 7, 100_000, 90, 85, 90, 88)
    weak = SupplierProfile("B", "1688", "trader", "Unknown", 9.0, 1000, 35, 2_000, 30, 20, 25, 30)

    assert score_supplier(strong) > score_supplier(weak)
    assert score_supplier(strong) >= 80


def test_risk_detection_flags_concentration_and_logistics():
    risk = analyze_supply_risk(supplier_count=1, avg_lead_time=35, certification_score=30, return_risk=80, quality_score=45)

    assert risk.risk_level == "HIGH"
    assert risk.categories["supplier_concentration_risk"] > 80
    assert risk.categories["logistics_risk"] > 80


def test_recommendation_output_for_source_and_avoid():
    source, source_summary = supply_recommendation(88, 75, 25, 65)
    avoid, avoid_summary = supply_recommendation(40, 25, 80, 10)

    assert source == "SOURCE"
    assert "Recommended initial order" in source_summary
    assert avoid == "AVOID"
    assert "Low margin" in avoid_summary


def test_supply_analysis_output_contains_business_fields():
    suppliers = [
        SupplierProfile("Factory A", "1688", "Zhejiang small appliance factory", "Zhejiang", 7.5, 100, 10, 50_000, 85, 80, 82, 84),
        SupplierProfile("Factory B", "Alibaba", "Guangdong appliance factory", "Guangdong", 8.2, 200, 14, 40_000, 75, 76, 80, 78),
    ]
    result = analyze_supply(make_product(), suppliers=suppliers, expected_daily_sales=20)

    assert result.supply_score >= 60
    assert result.recommendation in {"SOURCE", "TEST", "AVOID"}
    assert result.initial_order_quantity >= 400
    assert result.supplier_profile["factory_type"] == "Zhejiang small appliance factory"
