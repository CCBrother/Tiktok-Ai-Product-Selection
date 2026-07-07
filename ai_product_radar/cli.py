from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .io import load_products
from .report import write_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai-product-radar",
        description="Generate a daily TikTok Shop AI product radar report.",
    )
    subparsers = parser.add_subparsers(dest="command")

    report = subparsers.add_parser("report", help="Generate daily Markdown and JSON reports.")
    report.add_argument("--input", "-i", type=Path, default=Path("data/sample_products.csv"))
    report.add_argument("--output-dir", "-o", type=Path, default=Path("reports"))
    report.add_argument("--date", type=date.fromisoformat, default=date.today())

    crawl = subparsers.add_parser("crawl", help="Collect TikTok Shop raw JSON events.")
    crawl.add_argument("--term", action="append", default=[])
    crawl.add_argument("--product-url", action="append", default=[])
    crawl.add_argument("--shop-url", action="append", default=[])
    crawl.add_argument("--creator-url", action="append", default=[])
    crawl.add_argument("--video-url", action="append", default=[])
    crawl.add_argument("--trending", action="store_true")
    crawl.add_argument("--output", type=Path, default=Path("raw_events/tiktok_shop.jsonl"))
    crawl.add_argument("--headed", action="store_true")
    crawl.add_argument("--limit", type=int, default=30)
    crawl.add_argument("--dry-run", action="store_true")

    normalize = subparsers.add_parser("normalize", help="Normalize raw events into product facts.")
    normalize.add_argument("--input", type=Path, default=Path("raw_events/tiktok_shop.jsonl"))
    normalize.add_argument("--output", type=Path, default=Path("data/normalized_product_facts.csv"))
    normalize.add_argument("--date", type=date.fromisoformat, default=date.today())

    timeline = subparsers.add_parser("timeline", help="Build product history timeline.")
    timeline.add_argument("--facts", type=Path, default=Path("data/normalized_product_facts.csv"))
    timeline.add_argument("--output", type=Path, default=Path("data/product_history.csv"))
    timeline.add_argument("--date", type=date.fromisoformat, default=date.today())

    ingest = subparsers.add_parser("ingest", help="Load raw JSONL events into the configured SQL database.")
    ingest.add_argument("--input", type=Path, default=Path("raw_events/tiktok_shop.jsonl"))
    ingest.add_argument("--date", type=date.fromisoformat, default=date.today())
    ingest.add_argument("--init-db", action="store_true", help="Create database tables before ingesting.")

    subparsers.add_parser("jobs", help="List scheduler jobs.")
    subparsers.add_parser("system", help="Show integrated A-H system overview.")

    job = subparsers.add_parser("job", help="Run a scheduler job.")
    job.add_argument("job_name", help="Job name, or 'all'.")
    job.add_argument("--live", action="store_true", help="Run live crawler jobs instead of dry-run mode.")
    job.add_argument("--json", action="store_true", help="Print structured JSON result.")

    parser.add_argument("--input", "-i", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--output-dir", "-o", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--date", type=date.fromisoformat, default=None, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    command = args.command or "report"

    if command == "crawl":
        from .crawler.tiktok_shop import crawl_pages, crawl_search_terms, crawl_trending_products, write_dry_run
        import asyncio

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
        return

    if command == "normalize":
        from .crawler.events import read_events
        from .pipeline.normalize import normalize_events, write_facts_csv

        facts = normalize_events(read_events(args.input), args.date)
        write_facts_csv(facts, args.output)
        print(f"Wrote {len(facts)} normalized product facts to {args.output}")
        return

    if command == "timeline":
        from .pipeline.timeline import build_timeline

        points = build_timeline(args.facts, args.output, args.date)
        print(f"Wrote {len(points)} product history points to {args.output}")
        return

    if command == "ingest":
        from .db.ingestion import ingest_raw_events_file
        from .db.init_db import init_db
        from .db.session import SessionLocal

        if args.init_db:
            init_db()
        with SessionLocal() as session:
            stats = ingest_raw_events_file(args.input, session, observed_date=args.date)
        print(
            "Ingested "
            f"{stats['raw_events']} raw events, {stats['facts']} facts, "
            f"{stats['products']} products, {stats['history_points']} history points, "
            f"{stats['scores']} scores."
        )
        return

    if command == "jobs":
        from .scheduler import JOB_REGISTRY

        for job_name in JOB_REGISTRY:
            print(job_name)
        return

    if command == "system":
        import json
        from .integrated_system import system_overview

        print(json.dumps(system_overview(), ensure_ascii=False, indent=2))
        return

    if command == "job":
        from .scheduler.jobs import SchedulerContext, result_to_json, run_all_jobs, run_job

        context = SchedulerContext(dry_run=not args.live)
        result = run_all_jobs(context) if args.job_name == "all" else run_job(args.job_name, context)
        if args.json:
            print(result_to_json(result))
        elif isinstance(result, list):
            for item in result:
                print(f"{item.status}\t{item.job_name}\t{item.message}")
        else:
            print(f"{result.status}\t{result.job_name}\t{result.message}")
        return

    input_path = args.input or Path("data/sample_products.csv")
    output_dir = args.output_dir or Path("reports")
    report_date = args.date or date.today()
    products = load_products(input_path)
    if not products:
        raise SystemExit("No products found in input file.")

    md_path, json_path = write_reports(products, output_dir, report_date)
    print(f"Generated {md_path}")
    print(f"Generated {json_path}")


if __name__ == "__main__":
    main()
