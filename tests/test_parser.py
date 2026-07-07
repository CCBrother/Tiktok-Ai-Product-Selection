from backend.app.parser.parser import parse_product, parse_shop, parse_snapshot, parse_video


RAW_PRODUCT = {
    "collected_at": "2026-07-07T00:00:00+00:00",
    "product": {
        "product_id": "p-1",
        "title": "Portable Mini Blender",
        "description": "Blend anywhere.",
        "price": 24.99,
        "currency": "USD",
        "rating": 4.7,
        "review_count": 120,
        "sales_count": 950,
        "estimated_gmv": 23740.5,
        "video_count": 42,
        "creator_count": 18,
        "shop": {"id": "s-1", "shop_name": "Viral Kitchen", "followers": 12000},
    },
    "video": {"video_id": "v-1", "product_id": "p-1", "creator_id": "c-1", "views": 1000},
}


def test_parser_creates_product_shop_snapshot_video_objects():
    product = parse_product(RAW_PRODUCT)
    shop = parse_shop(RAW_PRODUCT)
    snapshot = parse_snapshot(RAW_PRODUCT)
    video = parse_video(RAW_PRODUCT)

    assert product["product_id"] == "p-1"
    assert shop["shop_id"] == "s-1"
    assert snapshot["sales_count"] == 950
    assert video["video_id"] == "v-1"
