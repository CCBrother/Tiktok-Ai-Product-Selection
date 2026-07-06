from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestThrottle:
    min_ms: int = 900
    max_ms: int = 2_400

    async def wait(self) -> None:
        await asyncio.sleep(random.randint(self.min_ms, self.max_ms) / 1000)

