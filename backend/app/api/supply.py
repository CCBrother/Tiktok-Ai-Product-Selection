from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.product_service import get_product
from backend.app.services.supply_service import analyze_and_save_supply, serialize_supply_result, supplier_match


router = APIRouter(prefix="/api", tags=["supply"])


@router.get("/supply/{product_id}")
def api_supply(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    result = analyze_and_save_supply(db, product)
    return serialize_supply_result(result)


@router.get("/supplier-match/{product_id}")
def api_supplier_match(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return supplier_match(product)
