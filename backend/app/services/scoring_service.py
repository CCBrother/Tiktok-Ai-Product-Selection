from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.models.video import Video
from backend.app.scoring.competition import competition_score
from backend.app.scoring.copy import copy_score
from backend.app.scoring.final_score import ScoreResult, final_score
from backend.app.scoring.growth import growth_score
from backend.app.scoring.profit import profit_score
from backend.app.scoring.supply import supply_score
from backend.app.scoring.trend import trend_score
from backend.app.scoring.virality import virality_score
from backend.app.services.snapshot_service import calculate_growth, get_product_history


def score_product(db: Session, product: Product) -> AIScore:
    history = get_product_history(db, product.product_id, days=30)
    latest = history[-1] if history else None
    growth = calculate_growth(history)
    video_metrics = _video_metrics(db, product.product_id)
    raw = latest.raw_json if latest and latest.raw_json else {}
    estimated_cost = float(raw.get("estimated_cost", (float(product.price or 0) * 0.35)))

    result = final_score(
        growth_score=growth_score(growth["sales_growth_7d"], growth["sales_growth_30d"], growth["creator_growth"]),
        trend_score=trend_score(growth["video_growth"], growth["creator_growth"], growth["engagement_growth"]),
        competition_score=competition_score(latest.sales_count if latest else 0, latest.shop_count if latest else 99),
        profit_score=profit_score(float(product.price or 0), estimated_cost),
        supply_score=supply_score(float(raw.get("supplier_availability", 55)), float(raw.get("moq", 250)), float(raw.get("lead_time_days", 18))),
        copy_score=copy_score(float(raw.get("brand_risk", 30)), float(raw.get("patent_risk", 25)), float(raw.get("production_difficulty", 30))),
        virality_score=virality_score(video_metrics["views"], video_metrics["likes"], video_metrics["shares"], video_metrics["comments"]),
        lifecycle_score=float(raw.get("lifecycle_score", _lifecycle_score(history))),
    )
    score = _save_score(db, product.product_id, result)
    db.commit()
    db.refresh(score)
    return score


def top_ranked_products(db: Session, limit: int = 20) -> list[tuple[Product, AIScore]]:
    latest_score_ids = (
        select(AIScore.product_id, AIScore.id)
        .distinct(AIScore.product_id)
        .order_by(AIScore.product_id, AIScore.score_time.desc())
        .subquery()
    )
    stmt = (
        select(Product, AIScore)
        .join(latest_score_ids, latest_score_ids.c.product_id == Product.product_id)
        .join(AIScore, AIScore.id == latest_score_ids.c.id)
        .order_by(AIScore.final_score.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def _save_score(db: Session, product_id: str, result: ScoreResult) -> AIScore:
    score = AIScore(
        product_id=product_id,
        growth_score=Decimal(str(result.growth_score)),
        trend_score=Decimal(str(result.trend_score)),
        competition_score=Decimal(str(result.competition_score)),
        profit_score=Decimal(str(result.profit_score)),
        supply_score=Decimal(str(result.supply_score)),
        copy_score=Decimal(str(result.copy_score)),
        virality_score=Decimal(str(result.virality_score)),
        lifecycle_score=Decimal(str(result.lifecycle_score)),
        final_score=Decimal(str(result.final_score)),
        recommendation_level=result.recommendation_level,
        ai_explanation=result.ai_explanation,
    )
    db.add(score)
    return score


def _video_metrics(db: Session, product_id: str) -> dict[str, int]:
    videos = list(db.scalars(select(Video).where(Video.product_id == product_id)).all())
    return {
        "views": sum(video.views for video in videos),
        "likes": sum(video.likes for video in videos),
        "comments": sum(video.comments for video in videos),
        "shares": sum(video.shares for video in videos),
    }


def _lifecycle_score(history: list[ProductSnapshot]) -> float:
    if len(history) < 10:
        return 85
    growth = calculate_growth(history)["sales_growth_7d"]
    if growth > 120:
        return 90
    if growth > 35:
        return 78
    if growth >= 0:
        return 62
    return 35
