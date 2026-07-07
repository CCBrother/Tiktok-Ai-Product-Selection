"""product opportunities

Revision ID: 0003_product_opportunities
Revises: 0002_crawler_logs
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_product_opportunities"
down_revision = "0002_crawler_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("opportunity_level", sa.String(length=8), nullable=False, server_default="D"),
        sa.Column("decision", sa.String(length=16), nullable=False, server_default="SKIP"),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("recommended_action", sa.String(length=64), nullable=False, server_default="Ignore"),
    )
    op.create_index("ix_product_opportunities_product_id", "product_opportunities", ["product_id"])
    op.create_index("ix_product_opportunities_product_time", "product_opportunities", ["product_id", "decision_time"])


def downgrade() -> None:
    op.drop_table("product_opportunities")
