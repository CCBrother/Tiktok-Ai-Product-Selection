from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    __table_args__ = (Index("ix_supplier_products_product_id", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    supplier_url: Mapped[str | None] = mapped_column(Text)
    factory_type: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    moq: Mapped[int] = mapped_column(nullable=False)
    lead_time: Mapped[int] = mapped_column(nullable=False)
    monthly_capacity: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SupplyAnalysis(Base):
    __tablename__ = "supply_analysis"
    __table_args__ = (Index("ix_supply_analysis_product_time", "product_id", "analysis_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    analysis_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    supply_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    margin_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    copy_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    recommended_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estimated_margin: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    supplier_count: Mapped[int] = mapped_column(nullable=False)
    recommendation: Mapped[str] = mapped_column(String(16), nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False)


class LogisticsCost(Base):
    __tablename__ = "logistics_cost"
    __table_args__ = (Index("ix_logistics_cost_product_id", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    shipping_method: Mapped[str] = mapped_column(String(64), nullable=False)
    origin: Mapped[str] = mapped_column(String(128), nullable=False)
    destination: Mapped[str] = mapped_column(String(128), nullable=False)
    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_days: Mapped[int] = mapped_column(nullable=False)
