from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .browser import PlaywrightBrowser
from .config import CrawlerConfig
from .events import append_event, make_event
from .list_crawlers import ProductListCrawler, TrendingProductCrawler
from .page_fetchers import TikTokPageFetcher


async def crawl_search_terms(terms: list[str], output: Path, headless: bool = True, limit: int = 30) -> int:
    config = CrawlerConfig(headless=headless)
    async with PlaywrightBrowser(config) as browser:
        return await ProductListCrawler(browser, config).crawl_search_terms(terms, output, limit=limit)


async def crawl_pages(urls: list[str], output: Path, page_type: str, headless: bool = True) -> int:
    config = CrawlerConfig(headless=headless)
    async with PlaywrightBrowser(config) as browser:
        return await TikTokPageFetcher(browser, config).fetch_many(urls, page_type, output)


async def crawl_product_pages(urls: list[str], output: Path, headless: bool = True) -> int:
    return await crawl_pages(urls, output, "product", headless=headless)


async def crawl_trending_products(output: Path, headless: bool = True, limit: int = 40) -> int:
    config = CrawlerConfig(headless=headless)
    async with PlaywrightBrowser(config) as browser:
        return await TrendingProductCrawler(browser, config).crawl(output, limit=limit)


def write_dry_run(output: Path) -> int:
    samples = [
        {
            "term": "pet hair remover",
            "product_name": "Pet Hair Detailer Glove",
            "shop_name": "Daily Pet Finds",
            "price_usd": 17.99,
            "sold_count": 8300,
            "rating_avg": 4.6,
            "rating_count": 1240,
            "video_mentions": 310,
        },
        {
            "term": "laundry gadget",
            "product_name": "Reusable Lint Trap Bags",
            "shop_name": "Home Fix Lab",
            "price_usd": 14.99,
            "sold_count": 4200,
            "rating_avg": 4.4,
            "rating_count": 760,
            "video_mentions": 95,
        },
    ]
    for sample in samples:
        append_event(
            output,
            make_event(
                event_type="product_snapshot",
                source="dry_run_tiktok_shop_us",
                url=f"https://www.tiktok.com/shop/search?q={sample['term']}",
                payload=sample,
                meta={"dry_run": True},
            ),
        )
    return len(samples)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect TikTok Shop US raw JSON events with Playwright.")
    parser.add_argument("--term", action="append", default=[], help="Search term. Can be repeated.")
    parser.add_argument("--product-url", action="append", default=[], help="TikTok Shop product page URL. Can be repeated.")
    parser.add_argument("--shop-url", action="append", default=[], help="TikTok Shop shop page URL. Can be repeated.")
    parser.add_argument("--creator-url", action="append", default=[], help="TikTok creator page URL. Can be repeated.")
    parser.add_argument("--video-url", action="append", default=[], help="TikTok video page URL. Can be repeated.")
    parser.add_argument("--trending", action="store_true", help="Collect trending TikTok Shop product list.")
    parser.add_argument("--output", type=Path, default=Path("raw_events/tiktok_shop.jsonl"))
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        count = write_dry_run(args.output)
    elif args.product_url:
        count = asyncio.run(crawl_pages(args.product_url, args.output, "product", headless=not args.headed))
    elif args.shop_url:
        count = asyncio.run(crawl_pages(args.shop_url, args.output, "shop", headless=not args.headed))
    elif args.creator_url:
        count = asyncio.run(crawl_pages(args.creator_url, args.output, "creator", headless=not args.headed))
    elif args.video_url:
        count = asyncio.run(crawl_pages(args.video_url, args.output, "video", headless=not args.headed))
    elif args.trending:
        count = asyncio.run(crawl_trending_products(args.output, headless=not args.headed, limit=args.limit))
    else:
        terms = args.term or ["viral kitchen gadget", "pet hair remover", "beauty tool"]
        count = asyncio.run(crawl_search_terms(terms, args.output, headless=not args.headed, limit=args.limit))
    print(f"Wrote {count} raw events to {args.output}")


if __name__ == "__main__":
    main()
