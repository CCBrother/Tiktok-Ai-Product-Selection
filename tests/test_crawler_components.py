import asyncio

from ai_product_radar.crawler.parsers import CreatorParser, ProductParser, ShopParser, VideoParser, parse_count
from ai_product_radar.crawler.proxy import ProxyManager
from ai_product_radar.crawler.retry import anti_block_retry
from ai_product_radar.crawler.tiktok_shop import write_dry_run


def test_parse_count_suffixes():
    assert parse_count("1.2K sold") == 1200
    assert parse_count("3M views") == 3_000_000


def test_product_parser_extracts_json_ld():
    payload = {
        "title": "Fallback",
        "jsonLd": [
            '{"@type":"Product","name":"Mini Sealer","category":"Kitchen","offers":{"price":"18.99","priceCurrency":"USD"},"aggregateRating":{"ratingValue":"4.6","reviewCount":"900"}}'
        ],
    }

    parsed = ProductParser().parse(payload)

    assert parsed["title"] == "Mini Sealer"
    assert parsed["price"] == 18.99
    assert parsed["rating"] == 4.6
    assert parsed["review_count"] == 900


def test_shop_creator_video_parsers():
    shop = ShopParser().parse({"title": "Home Fix Lab", "followers": "12K", "productCount": "88", "country": "US"})
    creator = CreatorParser().parse({"title": "Creator A", "followers": "2.5K", "videoCount": "44"})
    video = VideoParser().parse({"video_id": "v1", "views": "10K", "likes": "1K", "comments": "100", "shares": "50"})

    assert shop["follower_count"] == 12_000
    assert creator["follower_count"] == 2_500
    assert video["engagement_score"] == 11.5


def test_proxy_manager_builds_playwright_proxy():
    proxy = ProxyManager("http://127.0.0.1:8080", "u", "p").playwright_proxy()

    assert proxy == {"server": "http://127.0.0.1:8080", "username": "u", "password": "p"}


def test_anti_block_retry_retries_until_success():
    attempts = {"count": 0}

    async def flaky():
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("blocked")
        return "ok"

    assert asyncio.run(anti_block_retry(flaky, attempts=2, base_delay_s=0)) == "ok"


def test_dry_run_writes_events(tmp_path):
    output = tmp_path / "events.jsonl"

    assert write_dry_run(output) == 2
    assert output.read_text(encoding="utf-8").count("\n") == 2
