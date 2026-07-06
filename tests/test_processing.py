from ai_product_radar.pipeline.processing import (
    brand_extraction,
    build_time_series,
    category_mapping,
    compute_gmv,
    compute_sales_delta,
    deduplicate_products,
    detect_anomalies,
    embedding_generation,
    filter_invalid_data,
    image_hash_dedup,
    keyword_extraction,
    lifecycle_detection,
    merge_product_variants,
    normalize_product_data,
    product_clustering,
    review_sentiment,
    similarity_matching,
    supplier_inference,
    text_normalization,
    trend_detection,
)


def test_normalize_filter_dedupe_and_variant_merge():
    raw = [
        {"product_id": "p1", "title": "Pet Hair Remover Glove - Blue", "price": "12.99", "rating": "4.6"},
        {"product_id": "p1", "title": "Pet Hair Remover Glove Blue", "price": "12.99", "description": "better record"},
        {"product_id": "p2", "title": "Pet Hair Remover Glove - Red", "price": "13.99"},
        {"product_id": "bad", "title": "", "price": "9.99"},
        {"product_id": "bad2", "title": "Broken", "price": "-1"},
    ]

    valid = filter_invalid_data(raw)
    deduped = deduplicate_products(valid)
    merged = merge_product_variants(deduped)

    assert len(valid) == 3
    assert len(deduped) == 2
    assert len(merged) == 1
    assert merged[0]["variant_count"] == 2


def test_sales_gmv_time_series_and_anomalies():
    snapshots = [
        {"product_id": "p1", "snapshot_time": "2026-07-01T00:00:00", "sales": 10, "price": 20},
        {"product_id": "p1", "snapshot_time": "2026-07-02T00:00:00", "sales": 30, "price": 20},
        {"product_id": "p1", "snapshot_time": "2026-07-03T00:00:00", "sales": -5, "price": 20},
    ]

    series = build_time_series(snapshots)["p1"]
    anomalies = detect_anomalies(series, z_threshold=1.0)

    assert compute_sales_delta(30, 10) == 20
    assert compute_gmv(sales=3, price=9.99) == 29.97
    assert series[1]["sales_delta"] == 20
    assert series[1]["gmv"] == 600
    assert anomalies[-1]["is_anomaly"] is True


def test_text_category_brand_sentiment_keywords_and_embeddings():
    text = "Amazing Samsung pet hair remover glove by FurLab works great"

    normalized = normalize_product_data({"title": text, "price": 19.99})
    embedding = embedding_generation(text)

    assert text_normalization("  Pet-Hair!! ") == "pet hair"
    assert normalized["category"] == "Pet Supplies"
    assert category_mapping("air fryer silicone basket") == "Kitchen"
    assert brand_extraction(text) == "Samsung"
    assert review_sentiment(["love it works great", "bad refund"]) > 50
    assert "hair" in keyword_extraction(text)
    assert len(embedding) == 64


def test_supplier_similarity_clustering_lifecycle_and_trend():
    suppliers = supplier_inference(
        [
            {"product_id": "p1", "avg_moq": 100, "avg_price": 3.5, "lead_time_days": 8},
            {"product_id": "p1", "avg_moq": 200, "avg_price": 4.5, "lead_time_days": 10},
        ]
    )
    products = [
        {"product_id": "p1", "title": "Magnetic phone cooling grip", "description": "gaming phone cooler"},
        {"product_id": "p2", "title": "Phone cooling magnetic handle", "description": "mobile gaming cooler"},
        {"product_id": "p3", "title": "Ceramic coffee dripper", "description": "slow coffee filter"},
    ]
    series = [
        {"sales": 10, "sales_delta": 0},
        {"sales": 28, "sales_delta": 18},
        {"sales": 50, "sales_delta": 22},
    ]

    assert suppliers["p1"]["supplier_count"] == 2
    assert image_hash_dedup([{"image_hash": "a"}, {"image_hash": "a"}, {"image_hash": "b"}]) == [{"image_hash": "a"}, {"image_hash": "b"}]
    assert similarity_matching(products, threshold=0.2)
    assert any(len(cluster) >= 2 for cluster in product_clustering(products, threshold=0.2))
    assert lifecycle_detection(series)["stage"] == "上升"
    assert trend_detection(series)["trend"] == "fast_growth"
