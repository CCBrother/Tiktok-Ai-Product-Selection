from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Shop(Base):
    __tablename__ = "shops"

    shop_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str | None] = mapped_column(Text)
    follower_count: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    product_count: Mapped[int | None] = mapped_column(Integer)
    country: Mapped[str | None] = mapped_column(String(32))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class Creator(Base):
    __tablename__ = "creators"

    creator_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    nickname: Mapped[str | None] = mapped_column(Text)
    follower_count: Mapped[int | None] = mapped_column(Integer)
    total_videos: Mapped[int | None] = mapped_column(Integer)
    avg_views: Mapped[int | None] = mapped_column(Integer)
    engagement_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    country: Mapped[str | None] = mapped_column(String(32))


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    shop_id: Mapped[str | None] = mapped_column(ForeignKey("shops.shop_id"))
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64))
    brand: Mapped[str | None] = mapped_column(String(64))
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str | None] = mapped_column(String(8))
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    review_count: Mapped[int | None] = mapped_column(Integer)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    history: Mapped[list["ProductHistory"]] = relationship(back_populates="product")


class Video(Base):
    __tablename__ = "videos"

    video_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.product_id"))
    creator_id: Mapped[str | None] = mapped_column(ForeignKey("creators.creator_id"))
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime)
    engagement_score: Mapped[float | None] = mapped_column(Numeric(10, 2))


class ProductSnapshot(Base):
    __tablename__ = "product_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str | None] = mapped_column(String(128), index=True)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime)
    sales: Mapped[int | None] = mapped_column(Integer)
    gmv: Mapped[float | None] = mapped_column(Numeric(14, 2))
    order_count: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    video_count: Mapped[int | None] = mapped_column(Integer)
    creator_count: Mapped[int | None] = mapped_column(Integer)
    shop_count: Mapped[int | None] = mapped_column(Integer)
    engagement_score: Mapped[float | None] = mapped_column(Numeric(10, 2))
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class ProductHistory(Base):
    __tablename__ = "product_history"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    observed_date: Mapped[date] = mapped_column(Date)
    price_usd: Mapped[float | None] = mapped_column(Numeric(10, 2))
    sold_count: Mapped[int] = mapped_column(Integer, default=0)
    sales_growth_pct_7d: Mapped[float | None] = mapped_column(Numeric(8, 2))
    tiktok_mentions_7d: Mapped[int] = mapped_column(Integer, default=0)
    mention_growth_pct_7d: Mapped[float | None] = mapped_column(Numeric(8, 2))
    creator_count_7d: Mapped[int] = mapped_column(Integer, default=0)
    avg_video_engagement_pct: Mapped[float | None] = mapped_column(Numeric(8, 2))
    interaction_velocity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    rating_avg: Mapped[float | None] = mapped_column(Numeric(3, 2))
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    review_sentiment_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    growth_score: Mapped[int] = mapped_column(Integer, default=0)
    trend_score: Mapped[int] = mapped_column(Integer, default=0)
    competition_score: Mapped[int] = mapped_column(Integer, default=0)
    profit_score: Mapped[int] = mapped_column(Integer, default=0)
    review_score: Mapped[int] = mapped_column(Integer, default=0)
    lifecycle_score: Mapped[int] = mapped_column(Integer, default=0)
    supply_score: Mapped[int] = mapped_column(Integer, default=0)
    copy_difficulty_score: Mapped[int] = mapped_column(Integer, default=0)
    content_score: Mapped[int] = mapped_column(Integer, default=0)
    viral_score: Mapped[int] = mapped_column(Integer, default=0)
    ai_score: Mapped[int] = mapped_column(Integer, default=0)
    weights_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    decision_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw_event_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product: Mapped[Product] = relationship(back_populates="history")


class AIProductScore(Base):
    __tablename__ = "ai_product_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    score_time: Mapped[datetime | None] = mapped_column(DateTime)
    growth_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    trend_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    competition_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    profit_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    supply_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    copy_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    virality_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    final_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    lifecycle_stage: Mapped[str | None] = mapped_column(String(32))
    recommendation_level: Mapped[str | None] = mapped_column(String(8))
    explanation: Mapped[str | None] = mapped_column(Text)


class ProductCompetition(Base):
    __tablename__ = "product_competition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    shop_count: Mapped[int | None] = mapped_column(Integer)
    listing_count: Mapped[int | None] = mapped_column(Integer)
    saturation_score: Mapped[float | None] = mapped_column(Numeric(5, 2))


class SupplyChain(Base):
    __tablename__ = "supply_chain"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    supplier_count: Mapped[int | None] = mapped_column(Integer)
    avg_moq: Mapped[int | None] = mapped_column(Integer)
    avg_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    lead_time_days: Mapped[int | None] = mapped_column(Integer)
    supply_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    risk_level: Mapped[str | None] = mapped_column(String(16))


class ProductLifecycle(Base):
    __tablename__ = "product_lifecycle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    stage: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
