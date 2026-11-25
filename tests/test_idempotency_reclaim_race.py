import threading
import time
from backend.app.security import DistributedIdempotencyStore, get_db_connection


def test_expired_lease_reclaimed_by_exactly_one(tmp_path):
    store = DistributedIdempotencyStore(db_path=str(tmp_path / "i.db"))
    assert store.acquire_lock("k1", "h")
    conn = get_db_connection(store.db_path)
    with conn:
        conn.execute("UPDATE idempotency_keys SET created_at = ? WHERE idempotency_key='k1'", (time.time() - 1000,))
    results, barrier = [], threading.Barrier(16)

    def worker():
        barrier.wait()
        results.append(store.acquire_lock("k1", "h", ttl_seconds=10))

    ts = [threading.Thread(target=worker) for _ in range(16)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert results.count(True) == 1


def test_completed_never_reclaimed(tmp_path):
    store = DistributedIdempotencyStore(db_path=str(tmp_path / "i.db"))
    assert store.acquire_lock("k2", "h")
    store.mark_completed("k2", {"ok": 1})
    conn = get_db_connection(store.db_path)
    with conn:
        conn.execute("UPDATE idempotency_keys SET created_at = ? WHERE idempotency_key='k2'", (time.time() - 1000,))
    assert store.acquire_lock("k2", "h", ttl_seconds=10) is False
