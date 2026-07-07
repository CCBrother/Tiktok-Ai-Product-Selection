from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.product import Product
from backend.app.models.supply_chain import LogisticsCost, SupplierProduct, SupplyAnalysis
from backend.app.supply_engine.engine import SupplyAnalysisResult, analyze_supply
from backend.app.supply_engine.supplier import SupplierProfile, recommended_supplier_profile


def analyze_and_save_supply(db: Session, product: Product) -> SupplyAnalysisResult:
    suppliers = [_supplier_profile(row) for row in db.scalars(select(SupplierProduct).where(SupplierProduct.product_id == product.product_id)).all()]
    result = analyze_supply(product, suppliers=suppliers or None)
    db.add(
        SupplyAnalysis(
            product_id=product.product_id,
            supply_score=Decimal(str(result.supply_score)),
            margin_score=Decimal(str(result.margin_score)),
            risk_score=Decimal(str(result.risk_score)),
            copy_score=Decimal(str(result.copy_score)),
            estimated_cost=Decimal(str(result.estimated_cost)),
            recommended_price=Decimal(str(result.recommended_price)),
            estimated_margin=Decimal(str(result.estimated_margin)),
            supplier_count=result.supplier_count,
            recommendation=result.recommendation,
            ai_summary=result.ai_summary,
        )
    )
    db.add(
        LogisticsCost(
            product_id=product.product_id,
            shipping_method=result.logistics.shipping_method,
            origin=result.logistics.origin,
            destination=result.logistics.destination,
            cost_per_unit=Decimal(str(result.logistics.cost_per_unit)),
            shipping_days=result.logistics.shipping_days,
        )
    )
    db.commit()
    return result


def supplier_match(product: Product) -> dict:
    profile = recommended_supplier_profile(product.category)
    return {
        "product_id": product.product_id,
        "category": product.category,
        "recommended_supplier_profile": profile,
        "search_keywords": _keywords(product),
        "recommended_platforms": ["1688", "Alibaba", "Made-in-China"],
    }


def latest_supply_analysis(db: Session, product_id: str) -> SupplyAnalysis | None:
    stmt = select(SupplyAnalysis).where(SupplyAnalysis.product_id == product_id).order_by(SupplyAnalysis.analysis_time.desc()).limit(1)
    return db.scalar(stmt)


def serialize_supply_result(result: SupplyAnalysisResult) -> dict:
    payload = result.to_dict()
    payload["margin"] = result.estimated_margin
    payload["risk"] = result.risk.risk_level
    payload["summary"] = result.ai_summary
    return payload


def _supplier_profile(row: SupplierProduct) -> SupplierProfile:
    return SupplierProfile(
        supplier_name=row.supplier_name,
        platform=row.platform,
        factory_type=row.factory_type,
        location=row.location,
        price=float(row.price),
        moq=row.moq,
        lead_time=row.lead_time,
        monthly_capacity=row.monthly_capacity,
    )


def _keywords(product: Product) -> list[str]:
    words = [word for word in product.title.replace("#", "").split() if not word.isdigit()]
    return [" ".join(words[:3]), product.category or "TikTok product", f"{product.title} 1688"]
