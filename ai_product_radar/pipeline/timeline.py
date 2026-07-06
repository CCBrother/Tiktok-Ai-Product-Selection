from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

from ai_product_radar.pipeline.processing import compute_gmv, compute_sales_delta


@dataclass(frozen=True)
class ProductHistoryPoint:
    product_key: str
    observed_date: str
    price_usd: float
    sold_count: float
    tiktok_mentions_7d: float
    rating_avg: float
    rating_count: float
    sold_count_delta: float
    gmv: float
    mention_growth_pct_7d: float
    days_since_first_seen: int


def build_timeline(facts_path: Path, output: Path, today: date | None = None) -> list[ProductHistoryPoint]:
    today = today or date.today()
    with facts_path.open("r", newline="", encoding="utf-8-sig") as f:
        facts = list(csv.DictReader(f))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for fact in facts:
        grouped[fact["product_key"]].append(fact)

    points: list[ProductHistoryPoint] = []
    for product_key, rows in grouped.items():
        rows = sorted(rows, key=lambda row: row["observed_date"])
        first_date = datetime.fromisoformat(rows[0]["observed_date"]).date()
        previous_sold = 0.0
        previous_mentions = 0.0
        for row in rows:
            observed = datetime.fromisoformat(row["observed_date"]).date()
            sold = as_float(row.get("sold_count"))
            mentions = as_float(row.get("tiktok_mentions_7d"))
            mention_growth = 0.0 if previous_mentions <= 0 else (mentions - previous_mentions) / previous_mentions * 100
            points.append(
                ProductHistoryPoint(
                    product_key=product_key,
                    observed_date=observed.isoformat(),
                    price_usd=as_float(row.get("price_usd")),
                    sold_count=sold,
                    tiktok_mentions_7d=mentions,
                    rating_avg=as_float(row.get("rating_avg")),
                    rating_count=as_float(row.get("rating_count")),
                    sold_count_delta=max(0.0, compute_sales_delta(sold, previous_sold)),
                    gmv=as_float(row.get("gmv")) or compute_gmv(sales=sold, price=as_float(row.get("price_usd"))),
                    mention_growth_pct_7d=mention_growth,
                    days_since_first_seen=(today - first_date).days,
                )
            )
            previous_sold = sold
            previous_mentions = mentions

    write_history_csv(points, output)
    return points


def write_history_csv(points: list[ProductHistoryPoint], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ProductHistoryPoint.__dataclass_fields__.keys()))
        writer.writeheader()
        for point in points:
            writer.writerow(asdict(point))


def as_float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build product history timeline from normalized facts.")
    parser.add_argument("--facts", type=Path, default=Path("data/normalized_product_facts.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/product_history.csv"))
    parser.add_argument("--date", type=lambda value: datetime.fromisoformat(value).date(), default=date.today())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    points = build_timeline(args.facts, args.output, args.date)
    print(f"Wrote {len(points)} product history points to {args.output}")


if __name__ == "__main__":
    main()
