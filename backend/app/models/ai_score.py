from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class AIScore(Base):
    __tablename__ = "ai_scores"
    __table_args__ = (Index("ix_ai_scores_product_time", "product_id", "score_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    score_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    growth_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    trend_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    competition_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    profit_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    supply_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    copy_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    virality_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    lifecycle_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=60, nullable=False)
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    recommendation_level: Mapped[str] = mapped_column(String(8), default="C", nullable=False)
    ai_explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)

    product: Mapped["Product"] = relationship(back_populates="ai_scores")
