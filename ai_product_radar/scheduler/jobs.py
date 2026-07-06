from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

@dataclass(frozen=True)
class SchedulerContext:
    data_dir: Path = Path("data")
    raw_events_path: Path = Path("raw_events/tiktok_shop.jsonl")
    reports_dir: Path = Path("reports")
    sample_products_path: Path = Path("data/sample_products.csv")


@dataclass(frozen=True)
class JobResult:
    job_name: str
    status: str
    detail: str = ""


def _success(job_name: str, detail: str = "") -> JobResult:
    return JobResult(job_name=job_name, status="success", detail=detail)


def daily_crawler_job(context: SchedulerContext) -> JobResult:
    context.raw_events_path.parent.mkdir(parents=True, exist_ok=True)
    return _success("daily_crawler_job", str(context.raw_events_path))


def hourly_update_job(context: SchedulerContext) -> JobResult:
    return _success("hourly_update_job", str(context.data_dir))


def score_recalculation_job(context: SchedulerContext) -> JobResult:
    return _success("score_recalculation_job", str(context.sample_products_path))


def cleanup_job(context: SchedulerContext) -> JobResult:
    context.reports_dir.mkdir(parents=True, exist_ok=True)
    return _success("cleanup_job", str(context.reports_dir))


def snapshot_generator(context: SchedulerContext) -> JobResult:
    return _success("snapshot_generator", str(context.data_dir))


def trend_recalculation(context: SchedulerContext) -> JobResult:
    return _success("trend_recalculation", str(context.data_dir))


def alert_trigger(context: SchedulerContext) -> JobResult:
    return _success("alert_trigger", "no alerts")


def report_generator(context: SchedulerContext) -> JobResult:
    generate_report_task.delay(str(context.sample_products_path))
    return _success("report_generator", str(context.sample_products_path))


def system_monitor(context: SchedulerContext) -> JobResult:
    context.data_dir.mkdir(parents=True, exist_ok=True)
    return _success("system_monitor", "ok")


def failure_recovery_job(context: SchedulerContext) -> JobResult:
    return _success("failure_recovery_job", "ok")


JOB_REGISTRY: dict[str, Callable[[SchedulerContext], JobResult]] = {
    "daily_crawler_job": daily_crawler_job,
    "hourly_update_job": hourly_update_job,
    "score_recalculation_job": score_recalculation_job,
    "cleanup_job": cleanup_job,
    "snapshot_generator": snapshot_generator,
    "trend_recalculation": trend_recalculation,
    "alert_trigger": alert_trigger,
    "report_generator": report_generator,
    "system_monitor": system_monitor,
    "failure_recovery_job": failure_recovery_job,
}


def run_job(job_name: str, context: SchedulerContext | None = None) -> JobResult:
    if job_name not in JOB_REGISTRY:
        raise ValueError(f"Unknown job: {job_name}")
    return JOB_REGISTRY[job_name](context or SchedulerContext())


def run_all_jobs(context: SchedulerContext | None = None) -> list[JobResult]:
    run_context = context or SchedulerContext()
    return [job(run_context) for job in JOB_REGISTRY.values()]


def enqueue_daily_report() -> str:
    result = generate_report_task.delay()
    return str(result.id)
