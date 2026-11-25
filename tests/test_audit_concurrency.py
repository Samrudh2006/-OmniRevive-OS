import threading
from backend.app.audit_store import CryptographicAuditLedger


def test_concurrent_writers_keep_hash_chain_valid(tmp_path):
    ledger = CryptographicAuditLedger(db_path=str(tmp_path / "audit.db"))
    errors = []

    def worker(n):
        try:
            for i in range(25):
                ledger.record_event(f"tr_{n}_{i}", "m1", f"pay_{n}_{i}", "TEST", "NONE", {"i": i}, "ALLOW", "NOOP")
        except Exception as exc:  # surfaced in the assertion below
            errors.append(repr(exc))

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]

    assert errors == []
    result = ledger.verify_chain_integrity()
    assert result["valid"] is True, result
    assert result["total_events"] == 200
