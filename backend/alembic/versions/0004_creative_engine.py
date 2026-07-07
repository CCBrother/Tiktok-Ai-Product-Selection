"""creative engine tables

Revision ID: 0004_creative_engine
Revises: 0003_product_opportunities
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_creative_engine"
down_revision = "0003_product_opportunities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creative_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("content_angle", sa.Text(), nullable=False),
        sa.Column("target_audience", sa.Text(), nullable=False),
        sa.Column("hook_type", sa.String(length=64), nullable=False),
        sa.Column("script", sa.Text(), nullable=False),
        sa.Column("storyboard", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("hashtags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("shooting_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("test_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ai_reasoning", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_creative_reports_product_id", "creative_reports", ["product_id"])
    op.create_index("ix_creative_reports_product_created", "creative_reports", ["product_id", "created_at"])

    op.create_table(
        "creative_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("template_name", sa.String(length=128), nullable=False),
        sa.Column("template_structure", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("success_rate", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_creative_templates_category", "creative_templates", ["category"])


def downgrade() -> None:
    op.drop_table("creative_templates")
    op.drop_table("creative_reports")
