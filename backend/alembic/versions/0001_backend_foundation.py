"""backend foundation schema

Revision ID: 0001_backend_foundation
Revises:
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_backend_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("brand", sa.String(length=128), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_products_product_id", "products", ["product_id"], unique=True)
    op.create_index("ix_products_category", "products", ["category"])

    op.create_table(
        "shops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("shop_id", sa.String(length=128), nullable=False),
        sa.Column("shop_name", sa.String(length=255), nullable=False),
        sa.Column("followers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=False, server_default="US"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_shops_shop_id", "shops", ["shop_id"], unique=True)

    op.create_table(
        "creators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("creator_id", sa.String(length=128), nullable=False),
        sa.Column("nickname", sa.String(length=255), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("video_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement_rate", sa.Numeric(6, 2), nullable=False, server_default="0"),
    )
    op.create_index("ix_creators_creator_id", "creators", ["creator_id"], unique=True)

    op.create_table(
        "product_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sales_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gmv_estimate", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("video_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("creator_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shop_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement_score", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_product_snapshots_product_id", "product_snapshots", ["product_id"])
    op.create_index("ix_product_snapshots_snapshot_time", "product_snapshots", ["snapshot_time"])
    op.create_index("ix_product_snapshots_product_time", "product_snapshots", ["product_id", "snapshot_time"])

    op.create_table(
        "videos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("video_id", sa.String(length=128), nullable=False),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("creator_id", sa.String(length=128), sa.ForeignKey("creators.creator_id", ondelete="SET NULL"), nullable=True),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("publish_time", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_videos_video_id", "videos", ["video_id"], unique=True)
    op.create_index("ix_videos_product_id", "videos", ["product_id"])
    op.create_index("ix_videos_creator_id", "videos", ["creator_id"])
    op.create_index("ix_videos_product_publish_time", "videos", ["product_id", "publish_time"])

    op.create_table(
        "ai_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=128), sa.ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
        sa.Column("score_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("growth_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("trend_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("competition_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("profit_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("supply_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("copy_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("virality_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("lifecycle_score", sa.Numeric(5, 2), nullable=False, server_default="60"),
        sa.Column("final_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("recommendation_level", sa.String(length=8), nullable=False, server_default="C"),
        sa.Column("ai_explanation", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_ai_scores_product_id", "ai_scores", ["product_id"])
    op.create_index("ix_ai_scores_product_time", "ai_scores", ["product_id", "score_time"])


def downgrade() -> None:
    op.drop_table("ai_scores")
    op.drop_table("videos")
    op.drop_table("product_snapshots")
    op.drop_table("creators")
    op.drop_table("shops")
    op.drop_table("products")
