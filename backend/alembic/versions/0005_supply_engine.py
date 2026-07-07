"""supply engine tables

Revision ID: 0005_supply_engine
Revises: 0004_creative_engine
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_supply_engine"
down_revision = "0004_creative_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("supplier_url", sa.Text(), nullable=True),
        sa.Column("factory_type", sa.String(length=128), nullable=False),
        sa.Column("location", sa.String(length=128), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("moq", sa.Integer(), nullable=False),
        sa.Column("lead_time", sa.Integer(), nullable=False),
        sa.Column("monthly_capacity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_supplier_products_product_id", "supplier_products", ["product_id"])

    op.create_table(
        "supply_analysis",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("analysis_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("supply_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("margin_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("copy_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("recommended_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("estimated_margin", sa.Numeric(5, 2), nullable=False),
        sa.Column("supplier_count", sa.Integer(), nullable=False),
        sa.Column("recommendation", sa.String(length=16), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=False),
    )
    op.create_index("ix_supply_analysis_product_time", "supply_analysis", ["product_id", "analysis_time"])

    op.create_table(
        "logistics_cost",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("shipping_method", sa.String(length=64), nullable=False),
        sa.Column("origin", sa.String(length=128), nullable=False),
        sa.Column("destination", sa.String(length=128), nullable=False),
        sa.Column("cost_per_unit", sa.Numeric(10, 2), nullable=False),
        sa.Column("shipping_days", sa.Integer(), nullable=False),
    )
    op.create_index("ix_logistics_cost_product_id", "logistics_cost", ["product_id"])


def downgrade() -> None:
    op.drop_table("logistics_cost")
    op.drop_table("supply_analysis")
    op.drop_table("supplier_products")
