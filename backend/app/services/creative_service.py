from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.creative_engine.engine import CreativeReport, generate_creative_report
from backend.app.models.creative_report import CreativeReportModel
from backend.app.models.product import Product
from backend.app.models.video import Video
from backend.app.services.decision_service import decide_product


def generate_and_save_creative_report(db: Session, product: Product, lifecycle: str | None = None) -> CreativeReportModel:
    videos = list(db.scalars(select(Video).where(Video.product_id == product.product_id)).all())
    if lifecycle is None:
        decision = decide_product(db, product)
        lifecycle = decision.lifecycle.stage
    report = generate_creative_report(product, lifecycle=lifecycle, videos=videos)
    model = _save_report(db, report)
    db.commit()
    db.refresh(model)
    return model


def list_creative_reports(db: Session, product_id: str, limit: int = 10) -> list[CreativeReportModel]:
    stmt = (
        select(CreativeReportModel)
        .where(CreativeReportModel.product_id == product_id)
        .order_by(CreativeReportModel.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def serialize_creative_report(report: CreativeReportModel) -> dict:
    return {
        "id": report.id,
        "product_id": report.product_id,
        "created_at": report.created_at.isoformat(),
        "recommended_angle": report.content_angle,
        "target_audience": report.target_audience,
        "hook_type": report.hook_type,
        "script": json.loads(report.script),
        "storyboard": report.storyboard,
        "hashtags": report.hashtags,
        "shooting_plan": report.shooting_plan,
        "testing_plan": report.test_plan,
        "ai_reasoning": report.ai_reasoning,
    }


def _save_report(db: Session, report: CreativeReport) -> CreativeReportModel:
    primary_hook = report.hooks[0] if report.hooks else {"type": "problem"}
    model = CreativeReportModel(
        product_id=report.product_id,
        content_angle=report.recommended_angle,
        target_audience=report.target_audience,
        hook_type=primary_hook["type"],
        script=json.dumps(report.scripts[0], ensure_ascii=False),
        storyboard=report.storyboard,
        hashtags=report.hashtags,
        shooting_plan={
            **report.shooting_plan,
            "hooks": report.hooks,
            "competitor_analysis": report.competitor_analysis,
        },
        test_plan=report.testing_plan,
        ai_reasoning=report.ai_reasoning,
    )
    db.add(model)
    return model
