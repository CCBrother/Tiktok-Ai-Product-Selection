"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-06
"""

from __future__ import annotations

from pathlib import Path

from alembic import op


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    schema_sql = Path("sql/schema.sql").read_text(encoding="utf-8")
    op.execute(schema_sql)


def downgrade() -> None:
    for table in [
        "product_lifecycle",
        "supply_chain",
        "product_competition",
        "ai_product_scores",
        "product_history",
        "videos",
        "product_snapshots",
        "products",
        "creators",
        "shops",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
