from ai_product_radar.scheduler.jobs import JOB_REGISTRY, SchedulerContext, run_job


EXPECTED_JOBS = {
    "daily_crawler_job",
    "hourly_update_job",
    "score_recalculation_job",
    "cleanup_job",
    "snapshot_generator",
    "trend_recalculation",
    "alert_trigger",
    "report_generator",
    "system_monitor",
    "failure_recovery_job",
}


def test_h_group_jobs_are_registered():
    assert set(JOB_REGISTRY) == EXPECTED_JOBS


def test_system_monitor_job_runs(tmp_path):
    products = tmp_path / "sample_products.csv"
    products.write_text("product_name,category\n", encoding="utf-8")
    context = SchedulerContext(
        data_dir=tmp_path,
        raw_events_path=tmp_path / "raw.jsonl",
        reports_dir=tmp_path / "reports",
        sample_products_path=products,
    )

    result = run_job("system_monitor", context)

    assert result.job_name == "system_monitor"
    assert result.status == "success"


def test_unknown_job_returns_error():
    try:
        run_job("missing_job")
    except ValueError as exc:
        assert "Unknown job" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing job")
