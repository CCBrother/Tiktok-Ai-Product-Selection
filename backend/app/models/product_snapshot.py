from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, JSON, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class ProductSnapshot(Base):
    __tablename__ = "product_snapshots"
    __table_args__ = (
        Index("ix_product_snapshots_product_time", "product_id", "snapshot_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    sales_count: Mapped[int] = mapped_column(default=0, nullable=False)
    gmv_estimate: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    video_count: Mapped[int] = mapped_column(default=0, nullable=False)
    creator_count: Mapped[int] = mapped_column(default=0, nullable=False)
    shop_count: Mapped[int] = mapped_column(default=0, nullable=False)
    engagement_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="snapshots")
