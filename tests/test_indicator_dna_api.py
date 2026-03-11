from __future__ import annotations

from fastapi.testclient import TestClient

from app.api_indicator_dna import app


def test_api_indicator_dna_returns_json():
    client = TestClient(app)
    resp = client.get("/api/indicator_dna")
    # In this repo the cards file should exist; expect 200 and a JSON list
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        assert "indicator_name" in data[0]

