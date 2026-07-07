from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.product_service import get_product
from backend.app.services.radar_service import add_watchlist, daily_report_text, history, run_full_radar, today_opportunities


router = APIRouter(prefix="/api/radar", tags=["radar"])


@router.get("/today")
def api_radar_today(limit: int = Query(20, ge=1, le=100), refresh: bool = False, db: Session = Depends(get_db)) -> dict:
    if refresh:
        return run_full_radar(db, limit=limit)
    return {"items": today_opportunities(db, limit=limit)}


@router.get("/report")
def api_radar_report(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    return {"report": daily_report_text(db, limit=limit)}


@router.post("/watch/{product_id}")
def api_radar_watch(product_id: str, priority: str = "MEDIUM", db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    item = add_watchlist(db, product, priority=priority)
    return {"id": item.id, "product_id": item.product_id, "priority": item.priority, "created_at": item.created_at.isoformat()}


@router.get("/history")
def api_radar_history(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)) -> dict:
    return {"items": history(db, limit=limit)}
