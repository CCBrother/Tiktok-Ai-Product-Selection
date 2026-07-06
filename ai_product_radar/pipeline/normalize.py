from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ai_product_radar.crawler.events import RawEvent, read_events


@dataclass(frozen=True)
class NormalizedProductFact:
    observed_date: str
    product_key: str
    product_name: str
    category: str
    source: str
    shop_name: str
    product_url: str
    price_usd: float
    tiktok_mentions_7d: float
    sold_count: float
    rating_avg: float
    rating_count: float
    seller_count: float
    sales_growth_pct_7d: float
    review_sentiment_score: float
    lifecycle_stage: str
    supplier_count: float
    min_order_quantity: float
    lead_time_days: float
    content_creation_ease: float
    interaction_velocity: float
    raw_event_id: str


def normalize_events(events: list[RawEvent], observed_date: date | None = None) -> list[NormalizedProductFact]:
    observed = (observed_date or date.today()).isoformat()
    facts: list[NormalizedProductFact] = []
    for event in events:
        if event.event_type == "product_snapshot":
            facts.append(product_snapshot_to_fact(event, observed))
        elif event.event_type == "product_page":
            facts.append(product_page_to_fact(event, observed))
        elif event.event_type == "search_page":
            facts.extend(search_page_to_facts(event, observed))
    return dedupe_facts(facts)


def product_snapshot_to_fact(event: RawEvent, observed: str) -> NormalizedProductFact:
    payload = event.payload
    name = str(payload.get("product_name") or payload.get("title") or "Unknown Product").strip()
    return NormalizedProductFact(
        observed_date=observed,
        product_key=product_key(name),
        product_name=name,
        category=str(payload.get("category") or payload.get("term") or "Unknown"),
        source=event.source,
        shop_name=str(payload.get("shop_name") or ""),
        product_url=str(payload.get("product_url") or event.url),
        price_usd=parse_money(payload.get("price_usd") or payload.get("price")),
        tiktok_mentions_7d=float(payload.get("video_mentions") or payload.get("tiktok_mentions_7d") or 0),
        sold_count=float(payload.get("sold_count") or 0),
        rating_avg=float(payload.get("rating_avg") or 0),
        rating_count=float(payload.get("rating_count") or 0),
        seller_count=float(payload.get("seller_count") or payload.get("shop_competitor_count") or 0),
        sales_growth_pct_7d=float(payload.get("sales_growth_pct_7d") or payload.get("mention_growth_pct_7d") or 0),
        review_sentiment_score=float(payload.get("review_sentiment_score") or 0),
        lifecycle_stage=str(payload.get("lifecycle_stage") or ""),
        supplier_count=float(payload.get("supplier_count") or 0),
        min_order_quantity=float(payload.get("min_order_quantity") or 0),
        lead_time_days=float(payload.get("lead_time_days") or 0),
        content_creation_ease=float(payload.get("content_creation_ease") or 0),
        interaction_velocity=float(payload.get("interaction_velocity") or 0),
        raw_event_id=event.event_id,
    )


def product_page_to_fact(event: RawEvent, observed: str) -> NormalizedProductFact:
    payload = event.payload
    structured = extract_structured_product(payload)
    text = compact_text(str(payload.get("text") or ""))
    name = str(structured.get("name") or payload.get("title") or first_nonempty_line(text) or "Unknown Product").strip()
    price = structured.get("price") or parse_money(text)
    rating = structured.get("rating_avg") or parse_rating(text)
    rating_count = structured.get("rating_count") or parse_rating_count(text)
    sold_count = structured.get("sold_count") or parse_sold_count(text)

    return NormalizedProductFact(
        observed_date=observed,
        product_key=product_key(name),
        product_name=name,
        category=str(structured.get("category") or "TikTok Shop Product"),
        source=event.source,
        shop_name=str(structured.get("shop_name") or ""),
        product_url=str(payload.get("url") or event.url),
        price_usd=float(price or 0),
        tiktok_mentions_7d=0,
        sold_count=float(sold_count or 0),
        rating_avg=float(rating or 0),
        rating_count=float(rating_count or 0),
        seller_count=0,
        sales_growth_pct_7d=0,
        review_sentiment_score=0,
        lifecycle_stage="",
        supplier_count=0,
        min_order_quantity=0,
        lead_time_days=0,
        content_creation_ease=0,
        interaction_velocity=0,
        raw_event_id=event.event_id,
    )


def search_page_to_facts(event: RawEvent, observed: str) -> list[NormalizedProductFact]:
    facts: list[NormalizedProductFact] = []
    term = str(event.payload.get("term") or "Unknown")
    for card in event.payload.get("cards", []):
        text = compact_text(str(card.get("text") or ""))
        if not text:
            continue
        name = text.split("\n", 1)[0][:140]
        facts.append(
            NormalizedProductFact(
                observed_date=observed,
                product_key=product_key(name),
                product_name=name,
                category=term,
                source=event.source,
                shop_name="",
                product_url=str(card.get("href") or event.url),
                price_usd=parse_money(text),
                tiktok_mentions_7d=0,
                sold_count=parse_sold_count(text),
                rating_avg=0,
                rating_count=0,
                seller_count=0,
                sales_growth_pct_7d=0,
                review_sentiment_score=0,
                lifecycle_stage="",
                supplier_count=0,
                min_order_quantity=0,
                lead_time_days=0,
                content_creation_ease=0,
                interaction_velocity=0,
                raw_event_id=event.event_id,
            )
        )
    return facts


def dedupe_facts(facts: list[NormalizedProductFact]) -> list[NormalizedProductFact]:
    deduped: dict[tuple[str, str], NormalizedProductFact] = {}
    for fact in facts:
        key = (fact.observed_date, fact.product_key)
        existing = deduped.get(key)
        if existing is None or fact.sold_count + fact.rating_count > existing.sold_count + existing.rating_count:
            deduped[key] = fact
    return list(deduped.values())


def product_key(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return normalized[:120] or "unknown-product"


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def first_nonempty_line(value: str) -> str:
    for line in value.splitlines():
        if line.strip():
            return line.strip()
    return ""


def extract_structured_product(payload: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for raw_json in payload.get("jsonLd", []) or []:
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            candidates.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            candidates.append(parsed)

    next_data = str(payload.get("nextData") or "")
    if next_data:
        try:
            parsed = json.loads(next_data)
            candidates.append(parsed)
        except json.JSONDecodeError:
            pass

    for candidate in candidates:
        found = find_product_object(candidate)
        if found:
            offers = found.get("offers") if isinstance(found.get("offers"), dict) else {}
            aggregate_rating = found.get("aggregateRating") if isinstance(found.get("aggregateRating"), dict) else {}
            return {
                "name": found.get("name") or found.get("title"),
                "category": found.get("category"),
                "shop_name": found.get("brand", {}).get("name") if isinstance(found.get("brand"), dict) else found.get("brand"),
                "price": parse_money(offers.get("price") or found.get("price")),
                "rating_avg": float(aggregate_rating.get("ratingValue") or 0),
                "rating_count": float(aggregate_rating.get("reviewCount") or aggregate_rating.get("ratingCount") or 0),
                "sold_count": float(found.get("sold_count") or found.get("soldCount") or 0),
            }
    return {}


def find_product_object(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        object_type = value.get("@type") or value.get("type")
        if object_type == "Product" or (isinstance(object_type, list) and "Product" in object_type):
            return value
        for child in value.values():
            found = find_product_object(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_product_object(child)
            if found:
                return found
    return None


def parse_money(value: Any) -> float:
    if value is None:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", str(value).replace(",", ""))
    return float(match.group(1)) if match else 0.0


def parse_sold_count(value: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)([kKmM]?)\s*(?:sold|sales)", value)
    if not match:
        return 0.0
    amount = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix == "k":
        amount *= 1000
    elif suffix == "m":
        amount *= 1_000_000
    return amount


def parse_rating(value: str) -> float:
    match = re.search(r"(\d(?:\.\d)?)\s*(?:/ 5|out of 5|stars?)", value, re.IGNORECASE)
    return float(match.group(1)) if match else 0.0


def parse_rating_count(value: str) -> float:
    match = re.search(r"(\d+(?:,\d{3})*)\s*(?:reviews?|ratings?)", value, re.IGNORECASE)
    return float(match.group(1).replace(",", "")) if match else 0.0


def write_facts_csv(facts: list[NormalizedProductFact], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(facts[0]).keys()) if facts else list(NormalizedProductFact.__dataclass_fields__.keys()))
        writer.writeheader()
        for fact in facts:
            writer.writerow(asdict(fact))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize raw JSON events into product facts.")
    parser.add_argument("--input", type=Path, default=Path("raw_events/tiktok_shop.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/normalized_product_facts.csv"))
    parser.add_argument("--date", type=lambda value: datetime.fromisoformat(value).date(), default=date.today())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    facts = normalize_events(read_events(args.input), args.date)
    write_facts_csv(facts, args.output)
    print(f"Wrote {len(facts)} normalized product facts to {args.output}")


if __name__ == "__main__":
    main()
