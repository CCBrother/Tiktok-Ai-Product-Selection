"""crawler logs

Revision ID: 0002_crawler_logs
Revises: 0001_backend_foundation
Create Date: 2026-07-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_crawler_logs"
down_revision = "0001_backend_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crawler_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("crawler_logs")
