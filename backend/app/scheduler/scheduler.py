from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from backend.app.scheduler.jobs import (
    run_daily_autonomous_radar_job,
    run_daily_trending_job,
    run_hourly_update_job,
    run_hourly_watchlist_monitor_job,
    run_weekly_category_job,
    run_weekly_market_report_job,
)


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_daily_trending_job, "cron", hour=8, id="daily_crawl_trending_products", replace_existing=True)
    scheduler.add_job(run_daily_autonomous_radar_job, "cron", hour=8, id="daily_autonomous_radar", replace_existing=True)
    scheduler.add_job(run_hourly_update_job, "interval", hours=1, id="hourly_update_product_snapshot", replace_existing=True)
    scheduler.add_job(run_hourly_watchlist_monitor_job, "interval", hours=1, id="hourly_watchlist_monitor", replace_existing=True)
    scheduler.add_job(run_weekly_category_job, "cron", day_of_week="mon", hour=9, id="weekly_refresh_categories", replace_existing=True)
    scheduler.add_job(run_weekly_market_report_job, "cron", day_of_week="mon", hour=10, id="weekly_market_report", replace_existing=True)
    return scheduler
