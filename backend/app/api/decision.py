from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.products import serialize_dashboard_row
from backend.app.database.session import get_db
from backend.app.services.creative_service import generate_and_save_creative_report, serialize_creative_report
from backend.app.services.decision_service import decide_product, top_opportunities
from backend.app.services.product_service import get_product


router = APIRouter(prefix="/api", tags=["decision"])


@router.get("/decision/{product_id}")
def api_decision(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    result = decide_product(db, product)
    creative_report = None
    if result.decision == "LAUNCH":
        creative_report = serialize_creative_report(generate_and_save_creative_report(db, product, lifecycle=result.lifecycle.stage))
    return {
        "product": {
            "id": product.id,
            "product_id": product.product_id,
            "title": product.title,
            "category": product.category,
            "price": float(product.price or 0),
            "image_url": product.image_url,
        },
        **result.to_dict(),
        "creative_report": creative_report,
    }


@router.get("/opportunities")
def api_opportunities(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    rows = top_opportunities(db, limit=limit)
    return {
        "count": len(rows),
        "items": [
            {
                **serialize_dashboard_row(index + 1, product, score, decision),
                "opportunity": decision.to_dict(),
            }
            for index, (product, score, decision) in enumerate(rows)
        ],
    }
