from __future__ import annotations

from backend.app.utils.math import clamp


def supply_score(supplier_availability: float, moq: float, lead_time_days: float) -> float:
    availability_score = clamp(supplier_availability)
    moq_score = clamp(100 - max(moq - 50, 0) / 4)
    lead_time_score = clamp(100 - max(lead_time_days - 3, 0) * 4)
    return round(clamp(availability_score * 0.45 + moq_score * 0.25 + lead_time_score * 0.3), 2)
