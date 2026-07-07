from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.autonomous_radar.notification import format_notification, send_notification
from backend.app.autonomous_radar.report import generate_daily_report
from backend.app.autonomous_radar.scanner import scan_market
from backend.app.models.ai_score import AIScore
from backend.app.models.autonomous_radar import OpportunityReport, WatchlistItem
from backend.app.models.product import Product
from backend.app.services.creative_service import generate_and_save_creative_report, serialize_creative_report
from backend.app.services.product_service import latest_score
from backend.app.services.scoring_service import score_product, top_ranked_products
from backend.app.services.snapshot_service import get_product_history
from backend.app.services.supply_service import analyze_and_save_supply


def run_full_radar(db: Session, limit: int = 20) -> dict:
    candidates = _candidate_products(db, scan_limit=10_000)
    result = scan_market(candidates, limit=limit)
    today = date.today()
    items = []
    for ranked, agent_decision in result.recommendations:
        creative = generate_and_save_creative_report(db, ranked.product, lifecycle=ranked.opportunity.stage)
        supply = analyze_and_save_supply(db, ranked.product)
        item = {
            "product_id": ranked.product.product_id,
            "product_name": ranked.product.title,
            "opportunity_score": ranked.radar_score,
            "lifecycle": ranked.opportunity.stage,
            "decision": agent_decision.decision,
            "reason": agent_decision.reason,
            "risk": agent_decision.risk,
            "action": agent_decision.action,
            "expected_outcome": agent_decision.expected_outcome,
            "supply_score": supply.supply_score,
            "creative_angle": creative.content_angle,
        }
        _save_opportunity_report(db, item, today)
        if ranked.radar_score >= 90:
            send_notification(format_notification(item))
        items.append(item)
    db.commit()
    return {
        "scanned_count": result.scanned_count,
        "filtered_count": result.filtered_count,
        "deep_analysis_count": result.deep_analysis_count,
        "items": sorted(items, key=lambda item: item["opportunity_score"], reverse=True),
    }


def today_opportunities(db: Session, limit: int = 20) -> list[dict]:
    today = date.today()
    reports = list(
        db.scalars(
            select(OpportunityReport)
            .where(OpportunityReport.date == today)
            .order_by(OpportunityReport.score.desc())
            .limit(limit)
        ).all()
    )
    if not reports:
        return run_full_radar(db, limit=limit)["items"]
    return [_serialize_report(report) for report in reports]


def daily_report_text(db: Session, limit: int = 20) -> str:
    return generate_daily_report(today_opportunities(db, limit=limit))


def add_watchlist(db: Session, product: Product, priority: str = "MEDIUM") -> WatchlistItem:
    item = WatchlistItem(product_id=product.product_id, priority=priority)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def history(db: Session, limit: int = 100) -> list[dict]:
    reports = list(db.scalars(select(OpportunityReport).order_by(OpportunityReport.date.desc(), OpportunityReport.score.desc()).limit(limit)).all())
    return [_serialize_report(report) for report in reports]


def _candidate_products(db: Session, scan_limit: int) -> list[tuple[Product, AIScore, list]]:
    rows = top_ranked_products(db, limit=min(scan_limit, 1000))
    candidates = []
    for product, score in rows:
        active_score = score or latest_score(product) or score_product(db, product)
        history = get_product_history(db, product.product_id, days=30)
        candidates.append((product, active_score, history))
    return candidates


def _save_opportunity_report(db: Session, item: dict, report_date: date) -> OpportunityReport:
    db.execute(
        delete(OpportunityReport).where(
            OpportunityReport.product_id == item["product_id"],
            OpportunityReport.date == report_date,
        )
    )
    report = OpportunityReport(
        product_id=item["product_id"],
        date=report_date,
        score=Decimal(str(item["opportunity_score"])),
        decision=item["decision"],
        reason=item["reason"],
        action=item["action"],
    )
    db.add(report)
    return report


def _serialize_report(report: OpportunityReport) -> dict:
    return {
        "id": report.id,
        "product_id": report.product_id,
        "date": report.date.isoformat(),
        "opportunity_score": float(report.score),
        "decision": report.decision,
        "reason": report.reason,
        "action": report.action,
        "lifecycle": "N/A",
        "product_name": report.product_id,
    }
