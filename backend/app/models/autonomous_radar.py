from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Index, JSON, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


JsonColumn = JSON().with_variant(JSONB, "postgresql")


class OpportunityReport(Base):
    __tablename__ = "opportunity_reports"
    __table_args__ = (Index("ix_opportunity_reports_date_score", "date", "score"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (Index("ix_ai_predictions_product_id", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    prediction: Mapped[dict[str, Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    actual_result: Mapped[dict[str, Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    accuracy: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)


class WatchlistItem(Base):
    __tablename__ = "watchlist"
    __table_args__ = (Index("ix_watchlist_product_id", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
