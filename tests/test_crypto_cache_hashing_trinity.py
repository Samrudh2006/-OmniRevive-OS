"""
OmniRevive-OS :: Test Suite for The 3 Pillars (Caching, Hashing & Encryption)
=============================================================================
Tests L1/L2 multi-tier caching with ETags, RFC 6962 Merkle hashing, constant-time HMACs,
and Authenticated Payload Encryption/Decryption.
"""

import pytest
from backend.app.research.unified_crypto_cache_engine import unified_crypto_cache

def test_pillar_1_caching_lifecycle_and_etag_matching():
    """Verify Caching stores with ETag and responds with 304 NOT_MODIFIED on match."""
    key = "merchant_cache_test_100"
    val = {"merchant_name": "Flipkart", "active_rail": "HDFC", "balance_inr": 850000.0}

    # 1. Put into cache
    put_res = unified_crypto_cache.cache_put(key, val, ttl_seconds=300)
    assert put_res["status"] == "CACHE_STORED"
    etag = put_res["etag"]

    # 2. Get from cache without ETag
    get_res = unified_crypto_cache.cache_get(key)
    assert get_res["cache_status"] == "HIT"
    assert get_res["value"]["merchant_name"] == "Flipkart"
    assert get_res["hits"] == 1

    # 3. Get with matching ETag -> 304 Not Modified
    get_304 = unified_crypto_cache.cache_get(key, client_etag=etag)
    assert get_304["cache_status"] == "HIT_304_NOT_MODIFIED"
    assert get_304["hits"] == 2

def test_pillar_2_hashing_merkle_domain_separation_and_hmac():
    """Verify RFC 6962 leaf (0x00) and interior (0x01) domain separation and constant-time HMAC."""
    leaf_a = unified_crypto_cache.compute_rfc6962_merkle_leaf_hash("tx_data_1")
    leaf_b = unified_crypto_cache.compute_rfc6962_merkle_leaf_hash("tx_data_2")
    assert leaf_a != leaf_b
    assert len(leaf_a) == 64

    # Interior Node Hash
    interior = unified_crypto_cache.compute_rfc6962_interior_node_hash(leaf_a, leaf_b)
    assert len(interior) == 64
    assert interior != leaf_a

    # Constant-time HMAC
    secret = b"webhook_secret_key_123"
    msg = b'{"event":"payment.authorized","amount":2500}'
    import hmac, hashlib
    sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    
    assert unified_crypto_cache.verify_constant_time_hmac(secret, msg, sig) is True
    assert unified_crypto_cache.verify_constant_time_hmac(secret, msg, "bad_signature_hex_123") is False

def test_pillar_3_authenticated_encryption_and_tamper_rejection():
    """Verify Authenticated Encryption encrypts, decrypts, and rejects tampered ciphertexts."""
    sensitive_pan = "4111-2222-3333-4444|EXP:12/28|CVV:999"
    
    # 1. Encrypt
    encrypted_env = unified_crypto_cache.encrypt_sensitive_payload(sensitive_pan, associated_data="Merchant_Zepto_1")
    assert "ciphertext_b64" in encrypted_env
    assert "nonce_hex" in encrypted_env
    assert "auth_tag_hex" in encrypted_env
    assert sensitive_pan not in encrypted_env["ciphertext_b64"]

    # 2. Decrypt
    decrypted = unified_crypto_cache.decrypt_sensitive_payload(encrypted_env)
    assert decrypted["success"] is True
    assert decrypted["decrypted_plaintext"] == sensitive_pan
    assert decrypted["integrity_verified"] is True

    # 3. Tamper with ciphertext -> MUST FAIL
    tampered_env = dict(encrypted_env)
    tampered_env["auth_tag_hex"] = "0" * 32
    tampered_res = unified_crypto_cache.decrypt_sensitive_payload(tampered_env)
    assert tampered_res["success"] is False
    assert "AUTHENTICATION_TAG_MISMATCH" in tampered_res["error"]
