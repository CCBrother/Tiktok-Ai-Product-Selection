from __future__ import annotations

import asyncio
from typing import Iterable

from backend.app.crawler.product_crawler import TikTokProductCrawler
from backend.app.database.session import SessionLocal
from backend.app.services.crawler_log_service import log_crawler_task
from backend.app.services.data_pipeline import ingest_product
from backend.app.services.radar_service import daily_report_text, run_full_radar


async def crawl_trending_products(keywords: Iterable[str] = ("viral kitchen gadget", "beauty tool", "pet gadget")) -> int:
    crawler = TikTokProductCrawler()
    count = 0
    with SessionLocal() as db:
        for keyword in keywords:
            try:
                raws = await crawler.crawl_product_list(keyword)
                for raw in raws:
                    ingest_product(db, raw)
                    count += 1
                log_crawler_task(db, f"daily:crawl:{keyword}", "success")
            except Exception as exc:
                log_crawler_task(db, f"daily:crawl:{keyword}", "failed", str(exc))
    return count


async def update_existing_products(urls: Iterable[str]) -> int:
    crawler = TikTokProductCrawler()
    count = 0
    with SessionLocal() as db:
        for url in urls:
            try:
                raw = await crawler.crawl_product(url)
                ingest_product(db, raw)
                count += 1
            except Exception as exc:
                log_crawler_task(db, f"hourly:update:{url}", "failed", str(exc))
    return count


async def refresh_categories(categories: Iterable[str] = ("beauty", "home", "kitchen", "pet", "electronics")) -> int:
    crawler = TikTokProductCrawler()
    count = 0
    with SessionLocal() as db:
        for category in categories:
            try:
                raws = await crawler.crawl_category(category)
                for raw in raws:
                    ingest_product(db, raw)
                    count += 1
            except Exception as exc:
                log_crawler_task(db, f"weekly:category:{category}", "failed", str(exc))
    return count


def run_daily_trending_job() -> int:
    return asyncio.run(crawl_trending_products())


def run_hourly_update_job(urls: Iterable[str] = ()) -> int:
    return asyncio.run(update_existing_products(urls))


def run_weekly_category_job() -> int:
    return asyncio.run(refresh_categories())


def run_daily_autonomous_radar_job() -> int:
    with SessionLocal() as db:
        result = run_full_radar(db, limit=20)
        return len(result["items"])


def run_hourly_watchlist_monitor_job() -> int:
    with SessionLocal() as db:
        result = run_full_radar(db, limit=5)
        return len(result["items"])


def run_weekly_market_report_job() -> str:
    with SessionLocal() as db:
        return daily_report_text(db, limit=20)
