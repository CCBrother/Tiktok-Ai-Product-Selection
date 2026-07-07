from __future__ import annotations

from datetime import date


def generate_daily_report(items: list[dict], report_date: date | None = None) -> str:
    today = report_date or date.today()
    lines = [
        "================",
        "AI Product Radar Daily Report",
        f"Date: {today.isoformat()}",
        "",
        "TOP S PRODUCTS:",
    ]
    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"{index}.",
                f"Product: {item['product_name']}",
                f"Reason: {item['reason']}",
                f"Score: {item['opportunity_score']}",
                f"Lifecycle: {item['lifecycle']}",
                f"Supply: {item.get('supply_score', 'N/A')}",
                f"Creative Angle: {item.get('creative_angle', 'N/A')}",
                f"Recommended Action: {item['action']}",
                "",
            ]
        )
    lines.append("================")
    return "\n".join(lines)
