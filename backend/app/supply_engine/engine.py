from __future__ import annotations

from dataclasses import asdict, dataclass

from backend.app.models.product import Product
from backend.app.supply_engine.cost import CostBreakdown, calculate_total_cost
from backend.app.supply_engine.inventory import initial_order_quantity
from backend.app.supply_engine.logistics import LogisticsOption, choose_logistics
from backend.app.supply_engine.margin import MarginResult, calculate_margin
from backend.app.supply_engine.recommendation import supply_recommendation
from backend.app.supply_engine.risk import RiskResult, analyze_supply_risk
from backend.app.supply_engine.similarity import copy_difficulty_score
from backend.app.supply_engine.supplier import SupplierProfile, recommended_supplier_profile, score_supplier
from backend.app.utils.math import clamp


@dataclass(frozen=True)
class SupplyAnalysisResult:
    product_id: str
    supply_score: float
    margin_score: float
    risk_score: float
    copy_score: float
    estimated_cost: float
    recommended_price: float
    estimated_margin: float
    supplier_count: int
    recommendation: str
    ai_summary: str
    cost_breakdown: CostBreakdown
    margin: MarginResult
    risk: RiskResult
    logistics: LogisticsOption
    supplier_profile: dict
    initial_order_quantity: int

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "supply_score": self.supply_score,
            "margin_score": self.margin_score,
            "risk_score": self.risk_score,
            "copy_score": self.copy_score,
            "estimated_cost": self.estimated_cost,
            "recommended_price": self.recommended_price,
            "estimated_margin": self.estimated_margin,
            "supplier_count": self.supplier_count,
            "recommendation": self.recommendation,
            "ai_summary": self.ai_summary,
            "cost_breakdown": asdict(self.cost_breakdown),
            "margin_detail": asdict(self.margin),
            "risk_detail": {"risk_score": self.risk.risk_score, "risk_level": self.risk.risk_level, "categories": self.risk.categories},
            "logistics": asdict(self.logistics),
            "supplier_profile": self.supplier_profile,
            "initial_order_quantity": self.initial_order_quantity,
        }


def analyze_supply(product: Product, suppliers: list[SupplierProfile] | None = None, expected_daily_sales: int = 20) -> SupplyAnalysisResult:
    supplier_profiles = suppliers or [_fallback_supplier(product)]
    supplier_count = len(supplier_profiles)
    avg_moq = sum(item.moq for item in supplier_profiles) / max(supplier_count, 1)
    avg_lead_time = sum(item.lead_time for item in supplier_profiles) / max(supplier_count, 1)
    avg_factory = sum(item.factory_capability for item in supplier_profiles) / max(supplier_count, 1)
    avg_custom = sum(item.customization_ability for item in supplier_profiles) / max(supplier_count, 1)
    supplier_count_score = clamp(supplier_count * 12)
    moq_score = clamp(100 - max(avg_moq - 50, 0) / 5)
    lead_time_score = clamp(100 - max(avg_lead_time - 5, 0) * 4)
    supply_score = round(clamp(supplier_count_score * 0.3 + moq_score * 0.2 + lead_time_score * 0.2 + avg_factory * 0.2 + avg_custom * 0.1), 2)

    supplier_price = min(item.price for item in supplier_profiles)
    recommended_price = _recommended_price(float(product.price or 0), supplier_price)
    logistics = choose_logistics(recommended_price, urgency="test")
    cost = calculate_total_cost(supplier_price, recommended_price, sea_freight=logistics.cost_per_unit)
    margin = calculate_margin(recommended_price, cost.total_cost, supplier_price, advertising_cost=cost.advertising_cost)
    margin_score = round(clamp(margin.net_margin * 1.4), 2)
    certification = sum(item.certification for item in supplier_profiles) / max(supplier_count, 1)
    export = sum(item.export_experience for item in supplier_profiles) / max(supplier_count, 1)
    risk = analyze_supply_risk(supplier_count, avg_lead_time, (certification + export) / 2, return_risk=35, quality_score=avg_factory)
    copy_score = copy_difficulty_score(patent_risk=30, brand_dependency=25, technology_complexity=avg_factory, manufacturing_barrier=avg_moq / 5)
    recommendation, summary = supply_recommendation(supply_score, margin_score, risk.risk_score, copy_score)
    initial_qty = initial_order_quantity(expected_daily_sales, int(avg_lead_time), safety_stock=200)
    return SupplyAnalysisResult(
        product_id=product.product_id,
        supply_score=supply_score,
        margin_score=margin_score,
        risk_score=risk.risk_score,
        copy_score=copy_score,
        estimated_cost=cost.total_cost,
        recommended_price=recommended_price,
        estimated_margin=margin.net_margin,
        supplier_count=supplier_count,
        recommendation=recommendation,
        ai_summary=summary,
        cost_breakdown=cost,
        margin=margin,
        risk=risk,
        logistics=logistics,
        supplier_profile=recommended_supplier_profile(product.category),
        initial_order_quantity=initial_qty,
    )


def _fallback_supplier(product: Product) -> SupplierProfile:
    price = float(product.price or 20)
    supplier_price = round(max(price * 0.32, 2.2), 2)
    return SupplierProfile(
        supplier_name="Mock verified supplier",
        platform="1688",
        factory_type=recommended_supplier_profile(product.category)["factory_type"],
        location="Zhejiang, China",
        price=supplier_price,
        moq=200,
        lead_time=12,
        monthly_capacity=20_000,
        customization_ability=72,
        certification=68,
        export_experience=70,
        factory_capability=76,
    )


def _recommended_price(current_price: float, supplier_price: float) -> float:
    target = max(current_price, supplier_price * 3.2)
    anchors = [19.99, 24.99, 29.99, 34.99, 39.99, 49.99, 59.99, 79.99, 99.99]
    return min(anchors, key=lambda item: abs(item - target))
