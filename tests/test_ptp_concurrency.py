import threading
import time
from backend.app.b2b.ptp_engine import PTPStore


def test_concurrent_register_and_read_no_errors(tmp_path):
    store = PTPStore(db_path=str(tmp_path / "p.db"))
    errors = []
    barrier = threading.Barrier(24)

    def writer(i):
        try:
            barrier.wait()
            for j in range(10):
                store.register_promise(f"INV-{i % 6}", "+910000000000", time.time() + 3600, "tomorrow", 100.0 + j)
                store.has_active_ptp_lock(f"INV-{i % 6}")
        except Exception as exc:  # pragma: no cover
            errors.append(repr(exc))

    ts = [threading.Thread(target=writer, args=(i,)) for i in range(24)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert errors == []
    recs = store.get_all_ptp_records()
    assert sorted(r["invoice_id"] for r in recs) == [f"INV-{i}" for i in range(6)]
    assert all(store.has_active_ptp_lock(r["invoice_id"]) for r in recs)


def test_list_is_bounded(tmp_path):
    store = PTPStore(db_path=str(tmp_path / "q.db"))
    for i in range(12):
        store.register_promise(f"I{i}", "+910000000000", time.time() + 3600, "w", 1.0)
    assert len(store.get_all_ptp_records(limit=5)) == 5
    assert len(store.get_all_ptp_records()) == 12
