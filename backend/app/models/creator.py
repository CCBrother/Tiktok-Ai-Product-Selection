from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(255))
    followers: Mapped[int] = mapped_column(default=0, nullable=False)
    video_count: Mapped[int] = mapped_column(default=0, nullable=False)
    engagement_rate: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, nullable=False)

    videos: Mapped[list["Video"]] = relationship(back_populates="creator")
