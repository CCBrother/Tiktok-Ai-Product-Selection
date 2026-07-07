from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class ProductOpportunity(Base):
    __tablename__ = "product_opportunities"
    __table_args__ = (Index("ix_product_opportunities_product_time", "product_id", "decision_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    decision_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    opportunity_level: Mapped[str] = mapped_column(String(8), default="D", nullable=False)
    decision: Mapped[str] = mapped_column(String(16), default="SKIP", nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(64), default="Ignore", nullable=False)

    product: Mapped["Product"] = relationship()
