from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


JsonColumn = JSON().with_variant(JSONB, "postgresql")


class CreativeReportModel(Base):
    __tablename__ = "creative_reports"
    __table_args__ = (Index("ix_creative_reports_product_created", "product_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    content_angle: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    hook_type: Mapped[str] = mapped_column(String(64), nullable=False)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    storyboard: Mapped[dict[str, Any] | list[Any]] = mapped_column(JsonColumn, default=list, nullable=False)
    hashtags: Mapped[dict[str, Any] | list[Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    shooting_plan: Mapped[dict[str, Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    test_plan: Mapped[dict[str, Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    ai_reasoning: Mapped[str] = mapped_column(Text, default="", nullable=False)


class CreativeTemplate(Base):
    __tablename__ = "creative_templates"
    __table_args__ = (Index("ix_creative_templates_category", "category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    template_name: Mapped[str] = mapped_column(String(128), nullable=False)
    template_structure: Mapped[dict[str, Any]] = mapped_column(JsonColumn, default=dict, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
