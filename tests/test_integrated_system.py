from fastapi.testclient import TestClient

from ai_product_radar.api import app
from ai_product_radar.integrated_system import MODULES, system_overview, verify_local_artifacts


def test_a_to_h_modules_are_integrated():
    overview = system_overview()
    groups = {module["group"] for module in overview["modules"]}

    assert groups == set("ABCDEFGH")
    assert overview["status"] == "integrated"
    assert overview["scoring_weights"]["normalized_total"] == 1
    assert len(MODULES) == 8


def test_system_endpoint_returns_a_to_h_overview():
    client = TestClient(app)
    response = client.get("/system")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["module_count"] == 8
    assert {module["group"] for module in payload["modules"]} == set("ABCDEFGH")


def test_required_local_artifacts_exist():
    artifacts = verify_local_artifacts()

    assert all(artifacts.values())
