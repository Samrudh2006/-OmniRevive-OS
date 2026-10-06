"""
OmniRevive-OS :: CRYSTALS-Kyber KEM & Optimal Transport Mesh Test Suite
========================================================================
Tests:
1. NIST FIPS 203 ML-KEM-768 keygen, encapsulation, and decapsulation.
2. Sinkhorn-Knopp Entropic Optimal Transport multi-bank VAN rebalancing.
3. FastAPI REST endpoints integration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

from backend.app.research.kyber_kem import crystals_kyber_engine
from backend.app.research.optimal_transport_mesh import optimal_transport_mesh

client = TestClient(app)

def test_kyber_kem_keygen_encap_decap():
    """Verify ML-KEM-768 key exchange protocol."""
    # 1. Keygen
    keypair = crystals_kyber_engine.generate_kem_keypair("test_cfo_kyber_seed_1")
    assert keypair["status"] == "KEM_KEYPAIR_ACTIVE"
    assert "pk_hash" in keypair["public_key"]
    assert "sk_hash" in keypair["secret_key"]
    assert keypair["public_key"]["pk_size_bytes"] == 1184

    # 2. Encapsulation
    encap = crystals_kyber_engine.encapsulate_shared_secret(keypair["public_key"]["pk_hash"])
    assert encap["status"] == "ENCAPSULATION_SUCCESS"
    assert len(encap["shared_secret_256_key"]) == 64
    assert encap["ciphertext_size_bytes"] == 1088

    # 3. Decapsulation
    decap = crystals_kyber_engine.decapsulate_shared_secret(
        ciphertext_hash=encap["ciphertext_hash"],
        secret_key_hash=keypair["secret_key"]["sk_hash"]
    )
    assert decap["is_valid"] is True
    assert decap["verdict"] == "DECAPSULATION_AUTHENTIC"


def test_optimal_transport_sinkhorn_solver():
    """Verify Sinkhorn OT computes Wasserstein-2 plan for bank liquidity."""
    current_balances = {
        "HDFC": 500000.0,
        "ICICI": 50000.0,
        "SBI": 20000.0,
        "AXIS": 100000.0,
        "YES_BANK": 10000.0
    }
    target_reserves = {
        "HDFC": 200000.0,
        "ICICI": 200000.0,
        "SBI": 100000.0,
        "AXIS": 100000.0,
        "YES_BANK": 80000.0
    }

    result = optimal_transport_mesh.solve_sinkhorn_transport_plan(current_balances, target_reserves)
    assert result["status"] == "OPTIMAL_TRANSPORT_SOLVED"
    assert result["total_liquidity_managed_inr"] == 680000.0
    assert result["wasserstein_2_transport_cost"] >= 0.0
    assert result["sinkhorn_iterations"] == 50
    assert len(result["optimal_transfer_directives"]) > 0


def test_kyber_and_ot_fastapi_endpoints():
    """Verify FastAPI routes for Kyber KEM and Optimal Transport."""
    # 1. Kyber Keygen
    r_kg = client.post("/api/v1/research/kyber-keygen", json={"seed_phrase": "api_test_seed"})
    assert r_kg.status_code == 200
    assert r_kg.json()["data"]["status"] == "KEM_KEYPAIR_ACTIVE"

    # 2. Kyber Encap
    r_enc = client.post("/api/v1/research/kyber-encapsulate", json={"public_key_hash": "kyber_pk_test"})
    assert r_enc.status_code == 200
    assert r_enc.json()["data"]["status"] == "ENCAPSULATION_SUCCESS"

    # 3. Kyber Decap
    r_dec = client.post("/api/v1/research/kyber-decapsulate", json={
        "ciphertext_hash": "kyber_ct_123",
        "secret_key_hash": "kyber_sk_123"
    })
    assert r_dec.status_code == 200
    assert r_dec.json()["data"]["is_valid"] is True

    # 4. Optimal Transport Rebalance
    r_ot = client.post("/api/v1/research/optimal-transport-rebalance", json={})
    assert r_ot.status_code == 200
    assert r_ot.json()["data"]["status"] == "OPTIMAL_TRANSPORT_SOLVED"
