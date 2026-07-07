from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.creative_service import generate_and_save_creative_report, list_creative_reports, serialize_creative_report
from backend.app.services.product_service import get_product


router = APIRouter(prefix="/api/creative", tags=["creative"])


@router.post("/generate/{product_id}")
def api_generate_creative(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    report = generate_and_save_creative_report(db, product)
    payload = serialize_creative_report(report)
    return {
        "product": product.title,
        "recommended_angle": payload["recommended_angle"],
        "hooks": _extract_hooks(payload),
        "scripts": [payload["script"]],
        "storyboard": payload["storyboard"],
        "hashtags": payload["hashtags"],
        "testing_plan": payload["testing_plan"],
        "report": payload,
    }


@router.get("/{product_id}")
def api_creative_reports(product_id: str, limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    reports = [serialize_creative_report(report) for report in list_creative_reports(db, product.product_id, limit=limit)]
    return {"product": product.title, "count": len(reports), "reports": reports}


def _extract_hooks(payload: dict) -> list[str]:
    stored_hooks = payload.get("shooting_plan", {}).get("hooks")
    if stored_hooks:
        return stored_hooks
    first_day = payload["testing_plan"]["days"][0]["action"]
    return list(first_day)
