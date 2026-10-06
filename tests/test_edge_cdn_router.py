"""
OmniRevive-OS :: Test Suite for Multi-Region Edge CDN & Geo-Proximity Routing
=============================================================================
Tests Edge PoP resolution, L1 edge cache hits/misses, and autonomous regional failover.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.research.edge_cdn_router import edge_cdn_router

client = TestClient(app)

def test_edge_pop_geo_resolution_hyderabad():
    """Verify client in Hyderabad resolves to hyd-edge-02 with sub-5ms latency."""
    res = edge_cdn_router.resolve_optimal_edge_pop(client_lat=17.3850, client_lon=78.4867)
    assert res["status"] == "EDGE_ROUTE_RESOLVED"
    assert res["selected_edge_pop"] == "hyd-edge-02"
    assert res["city"] == "Hyderabad"
    assert res["effective_latency_ms"] < 5.0

def test_edge_pop_geo_resolution_delhi():
    """Verify client in Delhi resolves to del-edge-04."""
    res = edge_cdn_router.resolve_optimal_edge_pop(client_lat=28.7041, client_lon=77.1025)
    assert res["selected_edge_pop"] == "del-edge-04"
    assert res["city"] == "Delhi-NCR"

def test_edge_l1_cache_hit_and_miss_lifecycle():
    """Verify first fetch is MISS and subsequent fetch is instant HIT (<0.5ms)."""
    uri = "/assets/wasm_simd_core.wasm"
    pop = "hyd-edge-02"

    # 1. First fetch -> Cache Miss
    res_miss = edge_cdn_router.fetch_edge_cached_asset(uri, pop)
    assert res_miss["cache_status"] == "MISS_FETCHED_FROM_ORIGIN"
    assert res_miss["http_headers"]["X-Cache"] == "MISS"

    # 2. Second fetch -> Cache Hit
    res_hit = edge_cdn_router.fetch_edge_cached_asset(uri, pop)
    assert res_hit["cache_status"] == "HIT_L1_EDGE_POP"
    assert res_hit["http_headers"]["X-Cache"] == "HIT"
    assert res_hit["response_latency_ms"] < 0.5

def test_autonomous_regional_edge_failover():
    """Verify when Mumbai goes down, traffic seamlessly fails over to Hyderabad/Bengaluru in <5ms."""
    res = edge_cdn_router.simulate_edge_failover("mum-edge-01")
    assert res["status"] == "FAILOVER_SUCCESS"
    assert res["degraded_pop"] == "mum-edge-01"
    assert res["failover_target_pop"] in ["hyd-edge-02", "blr-edge-03"]

def test_edge_cdn_fastapi_endpoints():
    """Verify Edge CDN REST endpoints return structured envelopes."""
    # 1. Resolve PoP
    resp = client.post("/api/v1/edge/resolve-pop", json={"latitude": 12.9716, "longitude": 77.5946})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["selected_edge_pop"] == "blr-edge-03"

    # 2. Fetch Cached Asset
    resp_cache = client.get("/api/v1/edge/cache-asset?asset_uri=/test.js&pop_id=mum-edge-01")
    assert resp_cache.status_code == 200
    assert resp_cache.json()["success"] is True
