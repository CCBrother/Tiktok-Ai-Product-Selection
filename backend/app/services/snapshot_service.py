from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.schemas.product import ProductSnapshotCreate
from backend.app.utils.math import pct_growth


def create_snapshot(db: Session, payload: ProductSnapshotCreate) -> ProductSnapshot:
    snapshot = ProductSnapshot(**payload.model_dump())
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_product_history(db: Session, product_id: str, days: int = 30) -> list[ProductSnapshot]:
    stmt = (
        select(ProductSnapshot)
        .where(ProductSnapshot.product_id == product_id)
        .order_by(ProductSnapshot.snapshot_time.desc())
        .limit(days)
    )
    return list(db.scalars(stmt).all())[::-1]


def calculate_growth(history: list[ProductSnapshot]) -> dict[str, float]:
    if not history:
        return {"sales_growth_7d": 0, "sales_growth_30d": 0, "creator_growth": 0, "video_growth": 0, "engagement_growth": 0}
    latest = history[-1]
    by_time = sorted(history, key=lambda item: item.snapshot_time)

    def nearest(days_back: int) -> ProductSnapshot:
        target = latest.snapshot_time - timedelta(days=days_back)
        return min(by_time, key=lambda item: abs(item.snapshot_time - target))

    snap_7 = nearest(7)
    snap_30 = by_time[0] if len(by_time) < 30 else nearest(30)
    return {
        "sales_growth_7d": pct_growth(latest.sales_count, snap_7.sales_count),
        "sales_growth_30d": pct_growth(latest.sales_count, snap_30.sales_count),
        "creator_growth": pct_growth(latest.creator_count, snap_7.creator_count),
        "video_growth": pct_growth(latest.video_count, snap_7.video_count),
        "engagement_growth": pct_growth(float(latest.engagement_score), float(snap_7.engagement_score)),
    }
