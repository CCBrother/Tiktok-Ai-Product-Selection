from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(primary_key=True)
    shop_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    shop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    followers: Mapped[int] = mapped_column(default=0, nullable=False)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    country: Mapped[str] = mapped_column(String(64), default="US", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
