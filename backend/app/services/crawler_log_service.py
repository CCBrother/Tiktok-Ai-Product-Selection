from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models.crawler_log import CrawlerLog


def log_crawler_task(db: Session, task: str, status: str, error: str | None = None) -> CrawlerLog:
    row = CrawlerLog(task=task, status=status, error=error)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
