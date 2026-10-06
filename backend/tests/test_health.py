"""Tests for health check and readiness probe endpoints."""
from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_readiness_probe_endpoint(client: TestClient):
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] is True
    assert data["checks"]["configs"] is True
