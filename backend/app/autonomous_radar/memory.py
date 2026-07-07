from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MemoryItem:
    product_id: str
    decision: str
    date: date
    result: dict | None = None
