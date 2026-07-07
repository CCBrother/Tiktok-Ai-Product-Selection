from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.creator import Creator
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.models.shop import Shop
from backend.app.models.video import Video
from backend.app.parser.parser import parse_product, parse_shop, parse_snapshot, parse_video
from backend.app.services.crawler_log_service import log_crawler_task
from backend.app.services.scoring_service import score_product


def ingest_product(db: Session, raw_json: dict) -> dict:
    try:
        product_data = parse_product(raw_json)
        product = update_product(db, product_data)
        shop_data = parse_shop(raw_json)
        if shop_data:
            upsert_shop(db, shop_data)
        video_data = parse_video(raw_json)
        if video_data:
            upsert_video(db, video_data)
        snapshot = create_snapshot(db, raw_json)
        score = score_product(db, product)
        log_crawler_task(db, task=f"ingest_product:{product.product_id}", status="success")
        return {"product": product, "snapshot": snapshot, "score": score}
    except Exception as exc:
        db.rollback()
        log_crawler_task(db, task="ingest_product", status="failed", error=str(exc))
        raise


def update_product(db: Session, product_data: dict) -> Product:
    product = db.scalar(select(Product).where(Product.product_id == product_data["product_id"]))
    if product is None:
        product = Product(**product_data)
        db.add(product)
    else:
        for key, value in product_data.items():
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def create_snapshot(db: Session, raw_json: dict) -> ProductSnapshot:
    snapshot_data = parse_snapshot(raw_json)
    snapshot = ProductSnapshot(**snapshot_data)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def upsert_shop(db: Session, shop_data: dict) -> Shop:
    shop = db.scalar(select(Shop).where(Shop.shop_id == shop_data["shop_id"]))
    if shop is None:
        shop = Shop(**shop_data)
        db.add(shop)
    else:
        for key, value in shop_data.items():
            setattr(shop, key, value)
    db.commit()
    db.refresh(shop)
    return shop


def upsert_video(db: Session, video_data: dict) -> Video:
    creator_id = video_data.get("creator_id")
    if creator_id:
        creator = db.scalar(select(Creator).where(Creator.creator_id == creator_id))
        if creator is None:
            db.add(Creator(creator_id=creator_id, nickname=creator_id))
            db.commit()
    video = db.scalar(select(Video).where(Video.video_id == video_data["video_id"]))
    if video is None:
        video = Video(**video_data)
        db.add(video)
    else:
        for key, value in video_data.items():
            setattr(video, key, value)
    db.commit()
    db.refresh(video)
    return video
