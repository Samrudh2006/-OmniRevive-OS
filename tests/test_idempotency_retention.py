import time
from backend.app.security import DistributedIdempotencyStore, get_db_connection


def test_purge_only_removes_old_completed_keys(tmp_path):
    db = str(tmp_path / "idem.db")
    store = DistributedIdempotencyStore(db_path=db)
    for k in ("old_done", "new_done", "in_flight"):
        assert store.acquire_lock(k, "h")
    store.mark_completed("old_done", {"ok": 1})
    store.mark_completed("new_done", {"ok": 1})
    conn = get_db_connection(db)
    with conn:
        conn.execute("UPDATE idempotency_keys SET completed_at = ? WHERE idempotency_key = 'old_done'", (time.time() - 100 * 86400,))
    assert store.purge_completed(older_than_seconds=90 * 86400) == 1
    assert store.get_execution_record("old_done") is None
    assert store.get_execution_record("new_done") is not None
    assert store.get_execution_record("in_flight")["status"] == "ACQUIRED"
