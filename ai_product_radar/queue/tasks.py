from __future__ import annotations

from pathlib import Path

from ai_product_radar.queue.celery_app import celery_app


@celery_app.task(name="ai_product_radar.generate_report")
def generate_report_task(input_path: str = "data/sample_products.csv") -> dict[str, str]:
    from datetime import date

    from ai_product_radar.io import load_products
    from ai_product_radar.report import write_reports

    md_path, json_path = write_reports(load_products(Path(input_path)), Path("reports"), date.today())
    return {"markdown": str(md_path), "json": str(json_path)}
