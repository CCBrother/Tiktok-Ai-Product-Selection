from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.decision_engine.engine import DecisionResult, build_decision
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_opportunity import ProductOpportunity
from backend.app.services.product_service import latest_score
from backend.app.services.scoring_service import score_product, top_ranked_products
from backend.app.services.snapshot_service import get_product_history


def decide_product(db: Session, product: Product, score: AIScore | None = None) -> DecisionResult:
    active_score = score or latest_score(product) or score_product(db, product)
    history = get_product_history(db, product.product_id, days=30)
    result = build_decision(product, active_score, history)
    _save_opportunity(db, result)
    db.commit()
    return result


def latest_opportunity(db: Session, product_id: str) -> ProductOpportunity | None:
    stmt = (
        select(ProductOpportunity)
        .where(ProductOpportunity.product_id == product_id)
        .order_by(ProductOpportunity.decision_time.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def top_opportunities(db: Session, limit: int = 20) -> list[tuple[Product, AIScore, DecisionResult]]:
    rows = top_ranked_products(db, limit=max(limit * 2, limit))
    decisions = [(product, score, decide_product(db, product, score)) for product, score in rows]
    return sorted(decisions, key=lambda item: item[2].overall_score, reverse=True)[:limit]


def _save_opportunity(db: Session, result: DecisionResult) -> ProductOpportunity:
    opportunity = ProductOpportunity(
        product_id=result.product_id,
        overall_score=Decimal(str(result.overall_score)),
        opportunity_level=result.opportunity_level,
        decision=result.decision,
        confidence=Decimal(str(result.confidence)),
        reason=result.reason,
        recommended_action=result.recommended_action,
    )
    db.add(opportunity)
    return opportunity
