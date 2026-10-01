from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"


def test_api_overview():
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "nsfr" in data["kpis"]
    assert "lcr" in data["kpis"]
    assert data["kpis"]["nsfr"] > 100.0


def test_api_controls():
    res = client.get("/api/v1/controls")
    assert res.status_code == 200
    data = res.json()
    assert data["total_controls"] == 100
    assert data["control_score"] == 98.0


def test_api_lineage():
    res = client.get("/api/v1/lineage/NSFR")
    assert res.status_code == 200
    data = res.json()
    assert data["metric_name"] == "NSFR"
    assert data["is_acyclic"] is True
    assert data["node_count"] > 0


def test_api_scenarios():
    res = client.post("/api/v1/scenarios/run", json={"corporate_deposit_pct": -8.0})
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert abs(data["metrics"]["NSFR"]["scenario"] - 113.1) < 0.2


def test_api_copilot_verifier():
    # Clean question passes
    res_clean = client.post("/api/v1/copilot/ask", json={"question": "What drove the NSFR movement?"})
    assert res_clean.status_code == 200
    assert res_clean.json()["validation_status"] == "PASSED"

    # Adversarial error gets quarantined
    res_bad = client.post("/api/v1/copilot/ask", json={"question": "What was NSFR?", "force_adversarial_error": "INVENTED_NUMBER"})
    assert res_bad.status_code == 200
    assert res_bad.json()["is_blocked"] is True
