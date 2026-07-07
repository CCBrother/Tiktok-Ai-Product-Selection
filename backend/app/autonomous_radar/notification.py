from __future__ import annotations


def format_notification(item: dict) -> str:
    return (
        "🔥 New Opportunity Found\n\n"
        f"Product: {item['product_name']}\n"
        f"Score: {item['opportunity_score']}\n"
        f"Stage: {item['lifecycle']}\n"
        f"Action: {item['action']}"
    )


def send_notification(message: str, channel: str = "console") -> dict:
    return {"channel": channel, "status": "queued", "message": message}
