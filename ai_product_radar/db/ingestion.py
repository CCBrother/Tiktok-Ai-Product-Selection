from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_product_radar.crawler.events import RawEvent, read_events
from ai_product_radar.decision import build_decision
from ai_product_radar.models import ProductSignal
from ai_product_radar.pipeline.normalize import NormalizedProductFact, normalize_events
from ai_product_radar.pipeline.processing import normalize_product_data
from ai_product_radar.scoring import score_product

from .models import (
    AIProductScore,
    Creator,
    Product,
    ProductCompetition,
    ProductHistory,
    ProductLifecycle,
    ProductSnapshot,
    Shop,
    SupplyChain,
    Video,
)


def ingest_raw_events_file(path: Path, session: Session, observed_date: date | None = None) -> dict[str, int]:
    return ingest_raw_events(read_events(path), session, observed_date=observed_date)


def ingest_raw_events(events: list[RawEvent], session: Session, observed_date: date | None = None) -> dict[str, int]:
    observed = observed_date or date.today()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    facts = normalize_events(events, observed)

    stats = {
        "raw_events": len(events),
        "facts": len(facts),
        "products": 0,
        "snapshots": 0,
        "history_points": 0,
        "scores": 0,
        "shops": 0,
        "creators": 0,
        "videos": 0,
    }
    events_by_id = {event.event_id: event for event in events}

    for event in events:
        stats["shops"] += upsert_shop_from_event(session, event, now)
        stats["creators"] += upsert_creator_from_event(session, event)
        stats["videos"] += upsert_video_from_event(session, event)

    for fact in facts:
        event = events_by_id.get(fact.raw_event_id)
        product = upsert_product(session, fact, event, now)
        stats["products"] += 1
        stats["snapshots"] += insert_snapshot(session, fact, event, now)

        signal = product_signal_from_fact(fact, product, session, observed)
        score = score_product(signal)
        decision = build_decision(signal, score)

        upsert_history(session, product, fact, score, decision, observed)
        insert_ai_score(session, product.product_id, score, decision, now)
        upsert_side_tables(session, product.product_id, fact, score, observed)
        stats["history_points"] += 1
        stats["scores"] += 1

    session.commit()
    return stats


def upsert_product(session: Session, fact: NormalizedProductFact, event: RawEvent | None, now: datetime) -> Product:
    parsed = event.payload.get("parsed", {}) if event else {}
    normalized = normalize_product_data(
        {
            "product_id": parsed.get("product_id") or fact.product_key,
            "title": parsed.get("title") or fact.product_name,
            "description": parsed.get("description") or "",
            "category": parsed.get("category") or fact.category,
            "brand": parsed.get("brand") or "",
            "price": parsed.get("price") or fact.price_usd,
            "currency": parsed.get("currency") or "USD",
            "rating": parsed.get("rating") or fact.rating_avg,
            "review_count": parsed.get("review_count") or fact.rating_count,
            "shop_id": parsed.get("shop_id") or stable_shop_id(fact.shop_name),
        }
    )
    product_id = str(normalized["product_id"])
    shop_id = normalized.get("shop_id")
    if shop_id and get_shop(session, str(shop_id)) is None:
        session.add(Shop(shop_id=str(shop_id), name=fact.shop_name or None, country="US", created_at=now))
    product = session.scalar(select(Product).where(Product.product_id == product_id))
    if product is None:
        product = Product(product_id=product_id, first_seen_at=now)
        session.add(product)

    product.shop_id = shop_id
    product.title = normalized.get("title")
    product.description = normalized.get("description")
    product.category = normalized.get("category")
    product.brand = normalized.get("brand")
    product.price = normalized.get("price")
    product.currency = normalized.get("currency")
    product.rating = normalized.get("rating")
    product.review_count = normalized.get("review_count")
    product.last_seen_at = now
    product.is_active = True
    return product


def insert_snapshot(session: Session, fact: NormalizedProductFact, event: RawEvent | None, now: datetime) -> int:
    session.add(
        ProductSnapshot(
            product_id=fact.product_key,
            snapshot_time=parse_collected_at(event.collected_at) if event else now,
            sales=round_int(fact.sold_count),
            gmv=round_money(fact.sold_count * fact.price_usd),
            order_count=round_int(fact.sold_count),
            price=fact.price_usd,
            video_count=round_int(fact.tiktok_mentions_7d),
            creator_count=round_int(getattr(fact, "creator_count_7d", 0)),
            shop_count=round_int(fact.seller_count),
            engagement_score=fact.interaction_velocity,
            raw_json=asdict(event) if event else asdict(fact),
        )
    )
    return 1


def upsert_history(
    session: Session,
    product: Product,
    fact: NormalizedProductFact,
    score: Any,
    decision: Any,
    observed: date,
) -> None:
    session.flush()
    history = session.scalar(
        select(ProductHistory).where(ProductHistory.product_id == product.id, ProductHistory.observed_date == observed)
    )
    if history is None:
        history = ProductHistory(product_id=product.id, observed_date=observed)
        session.add(history)

    history.price_usd = fact.price_usd
    history.sold_count = round_int(fact.sold_count)
    history.sales_growth_pct_7d = fact.sales_growth_pct_7d
    history.tiktok_mentions_7d = round_int(fact.tiktok_mentions_7d)
    history.mention_growth_pct_7d = fact.sales_growth_pct_7d
    history.creator_count_7d = 0
    history.avg_video_engagement_pct = 0
    history.interaction_velocity = fact.interaction_velocity
    history.rating_avg = fact.rating_avg
    history.rating_count = round_int(fact.rating_count)
    history.review_sentiment_score = fact.review_sentiment_score
    history.growth_score = score.growth_score
    history.trend_score = score.trend_score
    history.competition_score = score.competition_score
    history.profit_score = score.profit_score
    history.review_score = score.review_score
    history.lifecycle_score = score.lifecycle_score
    history.supply_score = score.supply_score
    history.copy_difficulty_score = score.copy_difficulty_score
    history.content_score = score.content_score
    history.viral_score = score.viral_score
    history.ai_score = score.ai_score
    history.weights_json = score.weights
    history.decision_json = {
        "score": asdict(score),
        "decision": asdict(decision),
        "product_signal": asdict(product_signal_from_fact(fact, product, session, observed)),
    }
    history.raw_event_ids = [fact.raw_event_id]


def insert_ai_score(session: Session, product_id: str, score: Any, decision: Any, now: datetime) -> None:
    session.add(
        AIProductScore(
            product_id=product_id,
            score_time=now,
            growth_score=score.growth_score,
            trend_score=score.trend_score,
            competition_score=score.competition_score,
            profit_score=score.profit_score,
            supply_score=score.supply_score,
            copy_score=score.copy_difficulty_score,
            virality_score=score.viral_score,
            final_score=score.ai_score,
            lifecycle_stage=score.lifecycle_stage,
            recommendation_level=decision.recommendation_level,
            explanation=score.explanation,
        )
    )


def upsert_side_tables(session: Session, product_id: str, fact: NormalizedProductFact, score: Any, observed: date) -> None:
    session.add(
        ProductCompetition(
            product_id=product_id,
            shop_count=round_int(fact.seller_count),
            listing_count=round_int(fact.seller_count),
            saturation_score=score.competition_score,
        )
    )
    session.add(
        SupplyChain(
            product_id=product_id,
            supplier_count=round_int(fact.supplier_count),
            avg_moq=round_int(fact.min_order_quantity),
            avg_price=round_money(fact.price_usd * 0.35) if fact.price_usd else 0,
            lead_time_days=round_int(fact.lead_time_days),
            supply_score=score.supply_score,
            risk_level="low" if score.supply_score >= 70 else "medium" if score.supply_score >= 45 else "high",
        )
    )
    session.add(
        ProductLifecycle(
            product_id=product_id,
            stage=score.lifecycle_stage or fact.lifecycle_stage or "新兴",
            confidence=score.lifecycle_confidence / 100 if score.lifecycle_confidence else 0.55,
            updated_at=datetime.combine(observed, datetime.min.time()),
        )
    )


def product_signal_from_fact(
    fact: NormalizedProductFact,
    product: Product | None = None,
    session: Session | None = None,
    observed: date | None = None,
) -> ProductSignal:
    days_since_first_seen = 0.0
    if product and product.first_seen_at and observed:
        days_since_first_seen = max(0.0, (observed - product.first_seen_at.date()).days)

    sales_growth_30d = estimate_growth_30d(fact, product, session, observed)
    unit_cost = round_money(fact.price_usd * 0.35) if fact.price_usd > 0 else 0.0
    interaction_velocity = fact.interaction_velocity or min(100.0, fact.tiktok_mentions_7d * 0.12)

    return ProductSignal(
        product_name=fact.product_name,
        category=fact.category or "TikTok Shop Product",
        signal_source=fact.source,
        tiktok_mentions_7d=fact.tiktok_mentions_7d,
        mention_growth_pct_7d=fact.sales_growth_pct_7d,
        creator_count_7d=max(0.0, min(100.0, fact.tiktok_mentions_7d / 4)),
        avg_video_engagement_pct=min(20.0, interaction_velocity / 8),
        shop_competitor_count=fact.seller_count,
        amazon_review_count=fact.rating_count,
        unit_cost_usd=unit_cost,
        target_price_usd=fact.price_usd,
        shipping_complexity=2,
        copy_difficulty=2,
        problem_intensity=3,
        visual_demo_score=score_one_to_five(fact.content_creation_ease, default=3),
        impulse_buy_score=3,
        compliance_risk=1,
        rating_avg=fact.rating_avg,
        rating_count=fact.rating_count,
        days_since_first_seen=days_since_first_seen,
        supplier_count=fact.supplier_count,
        sales_growth_pct_7d=fact.sales_growth_pct_7d,
        sales_growth_pct_30d=sales_growth_30d,
        creator_growth_pct=fact.sales_growth_pct_7d * 0.4,
        seller_count=fact.seller_count,
        review_sentiment_score=fact.review_sentiment_score,
        lifecycle_stage=fact.lifecycle_stage,
        min_order_quantity=fact.min_order_quantity,
        lead_time_days=fact.lead_time_days,
        avg_price_stability=70,
        moq_feasibility=80 if fact.min_order_quantity <= 100 or fact.min_order_quantity == 0 else 55,
        lead_time_speed=85 if fact.lead_time_days <= 7 or fact.lead_time_days == 0 else 60,
        shipping_cost_estimation=75,
        brand_strength=5,
        patent_risk=5,
        content_complexity=10,
        production_complexity=10,
        influencer_dependency=10,
        content_creation_ease=fact.content_creation_ease,
        interaction_velocity=interaction_velocity,
        notes="Generated from public TikTok Shop snapshot; supply/cost fields are estimates unless enriched.",
        raw=asdict(fact),
    )


def estimate_growth_30d(
    fact: NormalizedProductFact,
    product: Product | None,
    session: Session | None,
    observed: date | None,
) -> float:
    if not product or not session or not observed:
        return fact.sales_growth_pct_7d
    session.flush()
    earliest = session.scalar(
        select(ProductHistory)
        .where(ProductHistory.product_id == product.id, ProductHistory.observed_date < observed)
        .order_by(ProductHistory.observed_date.asc())
    )
    if earliest is None or earliest.sold_count <= 0:
        return fact.sales_growth_pct_7d
    return max(0.0, (fact.sold_count - earliest.sold_count) / earliest.sold_count * 100)


def upsert_shop_from_event(session: Session, event: RawEvent, now: datetime) -> int:
    parsed = event.payload.get("parsed", {}) or {}
    if event.event_type != "shop_page" and not parsed.get("shop_id"):
        shop_name = event.payload.get("shop_name")
        if not shop_name:
            return 0
        parsed = {"shop_id": stable_shop_id(shop_name), "name": shop_name}
    shop_id = parsed.get("shop_id")
    if not shop_id:
        return 0
    shop = get_shop(session, str(shop_id))
    if shop is None:
        shop = Shop(shop_id=str(shop_id), created_at=now)
        session.add(shop)
    shop.name = parsed.get("name") or shop.name
    shop.follower_count = round_int(parsed.get("follower_count"))
    shop.rating = parsed.get("rating") or shop.rating
    shop.product_count = round_int(parsed.get("product_count"))
    shop.country = parsed.get("country") or shop.country or "US"
    return 1


def upsert_creator_from_event(session: Session, event: RawEvent) -> int:
    parsed = event.payload.get("parsed", {}) or {}
    if event.event_type != "creator_page" and not parsed.get("creator_id"):
        return 0
    creator_id = parsed.get("creator_id")
    if not creator_id:
        return 0
    creator = session.get(Creator, str(creator_id))
    if creator is None:
        creator = Creator(creator_id=str(creator_id))
        session.add(creator)
    creator.nickname = parsed.get("nickname") or creator.nickname
    creator.follower_count = round_int(parsed.get("follower_count"))
    creator.total_videos = round_int(parsed.get("total_videos"))
    creator.avg_views = round_int(parsed.get("avg_views"))
    creator.engagement_rate = parsed.get("engagement_rate") or creator.engagement_rate
    creator.country = parsed.get("country") or creator.country
    return 1


def upsert_video_from_event(session: Session, event: RawEvent) -> int:
    parsed = event.payload.get("parsed", {}) or {}
    if event.event_type != "video_page" and not parsed.get("video_id"):
        return 0
    video_id = parsed.get("video_id")
    if not video_id:
        return 0
    video = session.get(Video, str(video_id))
    if video is None:
        video = Video(video_id=str(video_id))
        session.add(video)
    video.product_id = parsed.get("product_id") or video.product_id
    video.creator_id = parsed.get("creator_id") or video.creator_id
    video.likes = round_int(parsed.get("likes"))
    video.comments = round_int(parsed.get("comments"))
    video.shares = round_int(parsed.get("shares"))
    video.views = round_int(parsed.get("views"))
    video.publish_time = parse_timestamp(parsed.get("publish_time"))
    video.engagement_score = parsed.get("engagement_score") or video.engagement_score
    return 1


def parse_collected_at(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def round_int(value: Any) -> int:
    try:
        return int(round(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def round_money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def score_one_to_five(value: float, default: float = 3) -> float:
    return value if 1 <= value <= 5 else default


def stable_shop_id(shop_name: str | None) -> str | None:
    if not shop_name:
        return None
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in shop_name).strip("-")
    return normalized[:128] or None


def get_shop(session: Session, shop_id: str) -> Shop | None:
    for item in session.new:
        if isinstance(item, Shop) and item.shop_id == shop_id:
            return item
    return session.get(Shop, shop_id)
