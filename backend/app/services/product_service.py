from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: str, payload: ProductUpdate) -> Product | None:
    product = get_product(db, product_id)
    if product is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: str) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.product_id == product_id if not product_id.isdigit() else (Product.id == int(product_id)) | (Product.product_id == product_id))
        .options(selectinload(Product.snapshots), selectinload(Product.ai_scores))
    )
    return db.scalar(stmt)


def list_products(db: Session, limit: int = 100, offset: int = 0) -> list[Product]:
    stmt = (
        select(Product)
        .order_by(Product.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Product.ai_scores))
    )
    return list(db.scalars(stmt).all())


def latest_score(product: Product) -> AIScore | None:
    if not product.ai_scores:
        return None
    return max(product.ai_scores, key=lambda score: score.score_time)
