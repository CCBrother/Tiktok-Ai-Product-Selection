"""autonomous radar tables

Revision ID: 0006_autonomous_radar
Revises: 0005_supply_engine
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006_autonomous_radar"
down_revision = "0005_supply_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "opportunity_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
    )
    op.create_index("ix_opportunity_reports_product_id", "opportunity_reports", ["product_id"])
    op.create_index("ix_opportunity_reports_date_score", "opportunity_reports", ["date", "score"])

    op.create_table(
        "ai_predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("prediction", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("actual_result", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("accuracy", sa.Numeric(5, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_ai_predictions_product_id", "ai_predictions", ["product_id"])

    op.create_table(
        "watchlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_watchlist_product_id", "watchlist", ["product_id"])


def downgrade() -> None:
    op.drop_table("watchlist")
    op.drop_table("ai_predictions")
    op.drop_table("opportunity_reports")
