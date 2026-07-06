import json

from fastapi.testclient import TestClient

from ai_product_radar.aggregation import aggregate_final_score
from ai_product_radar.api import app
from ai_product_radar.crawler.events import make_event
from ai_product_radar.growth import calculate_growth_score
from ai_product_radar.models import ProductSignal
from ai_product_radar.pipeline.normalize import normalize_events
from ai_product_radar.core.retry import retry_call
from ai_product_radar.validation.json_schema import validate_json_schema


def make_product(**overrides):
    base = dict(
        product_name="Test Product",
        category="Test",
        signal_source="Unit Test",
        tiktok_mentions_7d=100,
        mention_growth_pct_7d=100,
        creator_count_7d=10,
        avg_video_engagement_pct=5,
        shop_competitor_count=40,
        amazon_review_count=500,
        unit_cost_usd=5,
        target_price_usd=20,
        shipping_complexity=2,
        copy_difficulty=2,
        problem_intensity=3,
        visual_demo_score=3,
        impulse_buy_score=3,
        compliance_risk=1,
    )
    base.update(overrides)
    return ProductSignal(**base)


def test_growth_module_uses_sales_growth():
    assert calculate_growth_score(make_product(sales_growth_pct_7d=150, mention_growth_pct_7d=10)) == 50


def test_aggregation_engine_returns_weighted_score():
    component_scores = {
        "growth_score": 100,
        "trend_score": 80,
        "competition_score": 70,
        "profit_score": 60,
        "review_score": 50,
        "lifecycle_score": 40,
        "supply_score": 30,
        "copy_difficulty_score": 20,
        "content_score": 10,
        "viral_score": 0,
    }

    assert aggregate_final_score(component_scores) == 58


def test_product_page_json_normalizes_to_fact():
    event = make_event(
        event_type="product_page",
        source="unit",
        url="https://www.tiktok.com/shop/p/example",
        payload={
            "title": "Fallback Title",
            "url": "https://www.tiktok.com/shop/p/example",
            "text": "Example Product $19.99 1.2K sold 4.7 stars 320 reviews",
            "jsonLd": [
                json.dumps(
                    {
                        "@type": "Product",
                        "name": "Example Product",
                        "category": "Home",
                        "offers": {"price": "19.99"},
                        "aggregateRating": {"ratingValue": "4.7", "reviewCount": "320"},
                    }
                )
            ],
        },
    )

    facts = normalize_events([event])

    assert len(facts) == 1
    assert facts[0].product_name == "Example Product"
    assert facts[0].price_usd == 19.99
    assert facts[0].rating_avg == 4.7
    assert facts[0].rating_count == 320


def test_products_endpoint_returns_items():
    client = TestClient(app)
    response = client.get("/products?limit=2")

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert response.json()["ok"] is True


def test_e_group_api_endpoints():
    client = TestClient(app)
    endpoints = [
        "/products?limit=2",
        "/product/1",
        "/top-products?limit=2",
        "/ai-scores?limit=2",
        "/trending?limit=2",
        "/blue-ocean?limit=2",
        "/opportunity?limit=2",
        "/dashboard-summary",
        "/lifecycle?limit=2",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint

    recompute = client.post("/recompute-score")
    assert recompute.status_code == 200
    assert recompute.json()["data"]["status"] == "ok"


def test_json_schema_validator_accepts_raw_event():
    event = make_event(event_type="product_snapshot", source="unit", url="https://example.com", payload={})

    validate_json_schema(event.__dict__)


def test_retry_call_retries_until_success():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("not yet")
        return "ok"

    assert retry_call(flaky, attempts=2, base_delay_seconds=0) == "ok"
