from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class RawEvent:
    event_id: str
    event_type: str
    source: str
    collected_at: str
    url: str
    payload: dict[str, Any]
    meta: dict[str, Any] = field(default_factory=dict)


def make_event(event_type: str, source: str, url: str, payload: dict[str, Any], meta: dict[str, Any] | None = None) -> RawEvent:
    return RawEvent(
        event_id=str(uuid4()),
        event_type=event_type,
        source=source,
        collected_at=datetime.now(timezone.utc).isoformat(),
        url=url,
        payload=payload,
        meta=meta or {},
    )


def append_event(path: Path, event: RawEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")


def read_events(path: Path) -> list[RawEvent]:
    events: list[RawEvent] = []
    if not path.exists():
        return events
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                events.append(RawEvent(**row))
    return events
