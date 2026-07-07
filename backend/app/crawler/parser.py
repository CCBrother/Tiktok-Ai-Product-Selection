from __future__ import annotations

from bs4 import BeautifulSoup


def extract_page_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    return soup.get_text(" ", strip=True)


def extract_meta_image(html: str) -> str | None:
    soup = BeautifulSoup(html or "", "lxml")
    node = soup.select_one("meta[property='og:image'], meta[name='twitter:image']")
    return node.get("content") if node else None
