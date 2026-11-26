import sqlite3
import time
from backend.app.security import DistributedIdempotencyStore


def _make_legacy(path, with_merchant=True):
    conn = sqlite3.connect(path)
    cols = "merchant_api_key_id TEXT DEFAULT 'default_merchant'," if with_merchant else ""
    conn.execute(f"""CREATE TABLE idempotency_keys (
        idempotency_key TEXT PRIMARY KEY, {cols}
        payload_hash TEXT NOT NULL, created_at REAL NOT NULL, status TEXT NOT NULL,
        result_payload TEXT, completed_at REAL)""")
    now = time.time()
    rows = [("wh_1", "default_merchant", "h1", now, "COMPLETED", '{"ok": 1}', now),
            ("wh_2", "merchant_alpha", "h2", now, "ACQUIRED", None, None),
            ("wh_3", None, "h3", now, "RENEWED", None, None)] if with_merchant else \
           [("wh_1", "h1", now, "COMPLETED", '{"ok": 1}', now)]
    if with_merchant:
        conn.executemany("INSERT INTO idempotency_keys VALUES (?,?,?,?,?,?,?)", rows)
    else:
        conn.executemany("INSERT INTO idempotency_keys (idempotency_key,payload_hash,created_at,status,result_payload,completed_at) VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def test_migration_preserves_rows_and_scopes_per_merchant(tmp_path):
    db = str(tmp_path / "legacy.db")
    _make_legacy(db)
    store = DistributedIdempotencyStore(db_path=db)
    info = {c[1]: c[5] for c in sqlite3.connect(db).execute("PRAGMA table_info(idempotency_keys)").fetchall()}
    assert info["merchant_api_key_id"] >= 1 and info["idempotency_key"] >= 1  # composite PK
    assert store.get_execution_record("wh_1", "default_merchant")["status"] == "COMPLETED"
    assert store.get_execution_record("wh_1")["result_payload"] == {"ok": 1}
    assert store.get_execution_record("wh_2", "merchant_alpha")["status"] == "ACQUIRED"
    assert store.get_execution_record("wh_3", "default_merchant")["status"] == "RENEWED"  # NULL merchant backfilled
    # Old duplicate protection still holds for existing rows
    assert store.acquire_lock("wh_1", "h1") is False
    assert store.acquire_lock("wh_2", "h2", merchant_id="merchant_alpha") is False
    # The fix: a different merchant may now use the same key
    assert store.acquire_lock("wh_1", "hX", merchant_id="merchant_beta") is True
    assert store.acquire_lock("wh_1", "hX", merchant_id="merchant_beta") is False
    assert store.get_execution_record("wh_1", "default_merchant")["status"] == "COMPLETED"  # untouched
    store.mark_completed("wh_1", {"b": 1}, merchant_id="merchant_beta")
    assert store.get_execution_record("wh_1", "merchant_beta")["result_payload"] == {"b": 1}
    assert store.get_execution_record("wh_1", "default_merchant")["result_payload"] == {"ok": 1}


def test_migration_is_idempotent_and_handles_very_old_schema(tmp_path):
    db = str(tmp_path / "old.db")
    _make_legacy(db, with_merchant=False)
    DistributedIdempotencyStore(db_path=db)
    s2 = DistributedIdempotencyStore(db_path=db)  # second init: no re-migration, no error
    assert s2.get_execution_record("wh_1", "default_merchant")["status"] == "COMPLETED"
    n = sqlite3.connect(db).execute("SELECT count(*) FROM idempotency_keys").fetchone()[0]
    assert n == 1


def test_cross_merchant_same_key_independent_on_fresh_db(tmp_path):
    s = DistributedIdempotencyStore(db_path=str(tmp_path / "n.db"))
    assert s.acquire_lock("k", "h", merchant_id="a") and s.acquire_lock("k", "h", merchant_id="b")
    assert not s.acquire_lock("k", "h", merchant_id="a")
