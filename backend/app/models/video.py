from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (Index("ix_videos_product_publish_time", "product_id", "publish_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), index=True, nullable=False)
    creator_id: Mapped[str | None] = mapped_column(ForeignKey("creators.creator_id", ondelete="SET NULL"), index=True)
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    likes: Mapped[int] = mapped_column(default=0, nullable=False)
    comments: Mapped[int] = mapped_column(default=0, nullable=False)
    shares: Mapped[int] = mapped_column(default=0, nullable=False)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    creator: Mapped["Creator | None"] = relationship(back_populates="videos")
