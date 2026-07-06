from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseCrawler(ABC):
    def __init__(self, output: Path, headless: bool = True) -> None:
        self.output = output
        self.headless = headless

    @abstractmethod
    async def run(self) -> int:
        """Run crawler and return number of raw events written."""
