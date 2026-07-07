from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.decision_service import decide_product
from backend.app.services.product_service import get_product, latest_score, list_products
from backend.app.services.scoring_service import score_product, top_ranked_products
from backend.app.services.snapshot_service import get_product_history


router = APIRouter(prefix="/api", tags=["products"])


@router.get("/products")
def api_products(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)) -> list[dict]:
    products = list_products(db, limit=limit, offset=offset)
    return [_serialize_product(product, latest_score(product)) for product in products]


@router.get("/products/{product_id}")
def api_product_detail(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    history = get_product_history(db, product.product_id, days=30)
    scores = sorted(product.ai_scores, key=lambda item: item.score_time, reverse=True)
    latest = scores[0] if scores else None
    payload = _serialize_product(product, latest)
    payload["description"] = product.description
    payload["history"] = [_serialize_snapshot(item) for item in history]
    payload["ai_scores"] = [_serialize_score(item) for item in scores[:10]]
    payload["recommendation"] = latest.recommendation_level if latest else None
    return payload


@router.get("/ranking")
def api_ranking(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> list[dict]:
    rows = []
    for index, (product, score) in enumerate(top_ranked_products(db, limit)):
        decision = decide_product(db, product, score)
        rows.append(serialize_dashboard_row(index + 1, product, score, decision))
    return rows


@router.post("/score/{product_id}")
def api_recalculate_score(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    score = score_product(db, product)
    return _serialize_score(score)


def _serialize_product(product, score) -> dict:
    return {
        "id": product.id,
        "product_id": product.product_id,
        "title": product.title,
        "category": product.category,
        "brand": product.brand,
        "price": float(product.price or 0),
        "currency": product.currency,
        "rating": float(product.rating or 0),
        "review_count": product.review_count,
        "image_url": product.image_url,
        "score": _serialize_score(score) if score else None,
    }


def _serialize_snapshot(snapshot) -> dict:
    return {
        "id": snapshot.id,
        "product_id": snapshot.product_id,
        "snapshot_time": snapshot.snapshot_time.isoformat(),
        "sales_count": snapshot.sales_count,
        "gmv_estimate": float(snapshot.gmv_estimate),
        "price": float(snapshot.price or 0),
        "video_count": snapshot.video_count,
        "creator_count": snapshot.creator_count,
        "shop_count": snapshot.shop_count,
        "engagement_score": float(snapshot.engagement_score),
        "raw_json": snapshot.raw_json,
    }


def _serialize_score(score) -> dict:
    if score is None:
        return {}
    return {
        "id": score.id,
        "product_id": score.product_id,
        "score_time": score.score_time.isoformat(),
        "growth_score": float(score.growth_score),
        "trend_score": float(score.trend_score),
        "competition_score": float(score.competition_score),
        "profit_score": float(score.profit_score),
        "supply_score": float(score.supply_score),
        "copy_score": float(score.copy_score),
        "virality_score": float(score.virality_score),
        "lifecycle_score": float(score.lifecycle_score),
        "final_score": float(score.final_score),
        "recommendation_level": score.recommendation_level,
        "ai_explanation": score.ai_explanation,
    }


def serialize_dashboard_row(index: int, product, score, opportunity=None) -> dict:
    final = float(score.final_score)
    decision_level = opportunity.opportunity_level if opportunity else score.recommendation_level
    decision_text = opportunity.decision if opportunity else None
    lifecycle = opportunity.lifecycle.stage if opportunity else None
    lifecycle_confidence = opportunity.lifecycle.confidence if opportunity else None
    explanation = opportunity.explanation if opportunity else score.ai_explanation
    return {
        "id": product.id,
        "product_key": product.product_id,
        "product_name": product.title,
        "category": product.category or "Unknown",
        "gross_margin_pct": round(((float(product.price or 0) - float(product.price or 0) * 0.35) / max(float(product.price or 1), 1)) * 100, 2),
        "landed_profit_usd": round(float(product.price or 0) * 0.65, 2),
        "score": {
            "ai_score": round(final),
            "growth_score": round(float(score.growth_score)),
            "trend_score": round(float(score.trend_score)),
            "competition_score": round(float(score.competition_score)),
            "profit_score": round(float(score.profit_score)),
            "review_score": round(float(product.rating or 0) * 20),
            "lifecycle_score": round(float(score.lifecycle_score)),
            "supply_score": round(float(score.supply_score)),
            "copy_difficulty_score": round(float(score.copy_score)),
            "content_score": round((float(score.trend_score) + float(score.virality_score)) / 2),
            "viral_score": round(float(score.virality_score)),
            "risk_score": max(0, 100 - round(float(score.copy_score))),
            "explanation": explanation,
        },
        "decision": {
            "recommendation_level": decision_level,
            "business_decision": decision_text,
            "lifecycle": lifecycle,
            "lifecycle_confidence": lifecycle_confidence,
            "reasoning": explanation,
            "risk_analysis": "上线前检查侵权、认证、履约成本和真实供应商交期。",
            "suggested_price_min_usd": round(float(product.price or 0) * 0.9, 2),
            "suggested_price_max_usd": round(float(product.price or 0) * 1.15, 2),
            "suggested_procurement_cost_usd": round(float(product.price or 0) * 0.35, 2),
            "explanation_bundle": {
                "summary": score.ai_explanation,
                "gpt_explanation": score.ai_explanation,
                "risk_explanation": "上线前检查侵权、认证、履约成本和真实供应商交期。",
                "recommendation_text": "按7-30天窗口进行小预算快测。",
                "pricing_suggestion": "以主推价为中心做低价引流和套装锚点。",
                "sourcing_suggestion": "询价3-5家供应商，确认MOQ和交期。",
                "competition_explanation": "竞争得分越高代表销量信号和低卖家密度更好。",
                "lifecycle_explanation": "生命周期以30天历史趋势估算。",
                "virality_explanation": "病毒分由播放、点赞、评论和分享合成。",
                "alerts": [],
            },
        },
        "image_url": product.image_url,
        "rank": index,
    }


_serialize_dashboard_row = serialize_dashboard_row
