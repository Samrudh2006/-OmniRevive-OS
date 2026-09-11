import json
import sqlite3
import pytest
from backend.app.audit_store import CryptographicAuditLedger, GENESIS_HASH

def _seed_ledger(db_path, num_blocks=4):
    ledger = CryptographicAuditLedger(db_path=db_path)
    for i in range(1, num_blocks + 1):
        ledger.record_event(
            trace_id=f"tr_seq_{i}",
            merchant_id="merchant_test_01",
            payment_id=f"pay_seq_{i}",
            event_type="payment.failed",
            failure_class="TRANSIENT_GATEWAY",
            decision={"retry_step": i, "strategy": "DELAYED_RETRY"},
            policy_verdict="ALLOWED",
            action_taken="SCHEDULE_MANDATE_RETRY",
            gateway_result={"attempt": i}
        )
    return ledger

def test_tamper_1_modified_transaction_payload(tmp_path):
    db_file = str(tmp_path / "tamper1.db")
    ledger = _seed_ledger(db_file)
    assert ledger.verify_chain_integrity()["valid"] is True

    # Mutate payload in block 2
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("UPDATE audit_chain_ledger SET decision_json = ? WHERE sequence_id = 2", (json.dumps({"malicious": True}),))
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True
    assert res["broken_at_sequence"] == 2

def test_tamper_2_modified_timestamp(tmp_path):
    db_file = str(tmp_path / "tamper2.db")
    ledger = _seed_ledger(db_file)

    # Mutate timestamp in block 3
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("UPDATE audit_chain_ledger SET timestamp = timestamp + 1000 WHERE sequence_id = 3")
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True
    assert res["broken_at_sequence"] == 3

def test_tamper_3_modified_hash(tmp_path):
    db_file = str(tmp_path / "tamper3.db")
    ledger = _seed_ledger(db_file)

    # Mutate current_hash in block 2
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("UPDATE audit_chain_ledger SET current_hash = ? WHERE sequence_id = 2", ("f" * 64,))
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True
    assert res["broken_at_sequence"] == 2

def test_tamper_4_deleted_block(tmp_path):
    db_file = str(tmp_path / "tamper4.db")
    ledger = _seed_ledger(db_file, num_blocks=4)

    # Delete block 2 -> chain link between 1 and 3 is broken
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("DELETE FROM audit_chain_ledger WHERE sequence_id = 2")
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True
    assert res["broken_at_sequence"] == 3

def test_tamper_5_reordered_blocks(tmp_path):
    db_file = str(tmp_path / "tamper5.db")
    ledger = _seed_ledger(db_file, num_blocks=3)

    # Swap sequence_ids of block 2 and 3
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("UPDATE audit_chain_ledger SET sequence_id = 99 WHERE sequence_id = 2")
        conn.execute("UPDATE audit_chain_ledger SET sequence_id = 2 WHERE sequence_id = 3")
        conn.execute("UPDATE audit_chain_ledger SET sequence_id = 3 WHERE sequence_id = 99")
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True

def test_tamper_6_inserted_block(tmp_path):
    db_file = str(tmp_path / "tamper6.db")
    ledger = _seed_ledger(db_file, num_blocks=3)

    # Insert malicious unchained block at high sequence
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("""
            INSERT INTO audit_chain_ledger (
                event_id, trace_id, timestamp, merchant_id, payment_id,
                event_type, failure_class, decision_json, policy_verdict,
                action_taken, gateway_result_json, prev_hash, current_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "evt_malicious_insert", "tr_hack", 1000.0, "m_hack", "p_hack",
            "fraud.injection", "NONE", "{}", "ALLOWED", "ATTACK", "{}",
            "0" * 64, "a" * 64
        ))
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True

def test_tamper_7_changed_prev_hash(tmp_path):
    db_file = str(tmp_path / "tamper7.db")
    ledger = _seed_ledger(db_file, num_blocks=3)

    # Mutate prev_hash in block 3
    conn = sqlite3.connect(db_file)
    with conn:
        conn.execute("UPDATE audit_chain_ledger SET prev_hash = ? WHERE sequence_id = 3", ("e" * 64,))
    conn.close()

    res = ledger.verify_chain_integrity()
    assert res["valid"] is False
    assert res["tampering_detected"] is True
    assert res["broken_at_sequence"] == 3
