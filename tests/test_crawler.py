import asyncio

from backend.app.crawler.base import JsonResponseCapture, save_raw_json
from backend.app.crawler.product_crawler import _extract_product_hint


class FakeResponse:
    headers = {"content-type": "application/json"}
    url = "https://www.tiktok.com/api/product"
    status = 200

    async def json(self):
        return {"product_id": "abc", "title": "Portable Blender"}


def test_crawler_captures_json_response():
    capture = JsonResponseCapture()
    asyncio.run(capture.capture(FakeResponse()))

    assert capture.as_dicts()[0]["json"]["product_id"] == "abc"


def test_crawler_extracts_product_json_and_saves_raw(tmp_path):
    snapshot = {
        "url": "https://www.tiktok.com/shop/product/123",
        "title": "Portable Mini Blender | TikTok",
        "text": "$29.99 1.2K sold 4.8 stars 300 reviews 44 videos 12 creators",
    }
    product = _extract_product_hint(snapshot, "<meta property='og:image' content='https://img.test/p.png'>")
    path = save_raw_json({"product": product}, "product", product["product_id"], root=tmp_path)

    assert product["product_id"] == "123"
    assert product["price"] == 29.99
    assert product["sales_count"] == 1200
    assert path.exists()
