import hmac
import hashlib
import time
import json
import sqlite3
import re
import os
import uuid
import threading
import logging
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import constant_time
try:
    import redis
except ImportError:
    redis = None

from backend.app.config import settings

logger = logging.getLogger("OmniRevive.Security")

# Thread-local storage & tracked registry for SQLite connections in WAL mode
_local = threading.local()
_conn_registry_lock = threading.Lock()
_conn_registry: Dict[tuple, sqlite3.Connection] = {}


def _prune_dead_thread_connections() -> None:
    """Closes cached connections belonging to threads that have already exited."""
    active_tids = {t.ident for t in threading.enumerate()}
    with _conn_registry_lock:
        dead_keys = [k for k in _conn_registry if k[0] not in active_tids]
        for k in dead_keys:
            conn = _conn_registry.pop(k, None)
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass


def get_db_connection(db_path: str) -> sqlite3.Connection:
    _prune_dead_thread_connections()
    attr_name = f"conn_{db_path}"
    conn = getattr(_local, attr_name, None)
    if conn is None:
        conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 10000;")  # wait for a competing writer instead of failing with "database is locked"
        conn.execute("PRAGMA foreign_keys = ON;")
        setattr(_local, attr_name, conn)
        with _conn_registry_lock:
            _conn_registry[(threading.get_ident(), db_path)] = conn
    return conn


def close_all_db_connections() -> int:
    """Gracefully closes all tracked SQLite connections on application shutdown or test teardown."""
    closed = 0
    with _conn_registry_lock:
        items = list(_conn_registry.items())
        _conn_registry.clear()
    for (_, db_path), conn in items:
        try:
            conn.close()
            closed += 1
        except Exception:
            pass
        attr_name = f"conn_{db_path}"
        if hasattr(_local, attr_name):
            try:
                delattr(_local, attr_name)
            except Exception:
                pass
    return closed

def mask_pii_string(value: Optional[str]) -> str:
    """
    DPDP Act 2023 & PCI-DSS Compliance: Masks Personally Identifiable Information (PII).
    Masks Phone: +919876543210 -> +9198******10
    Masks Email: customer@example.com -> c******r@example.com
    """
    if not value:
        return "N/A"
    
    # Check if Email
    if "@" in value:
        parts = value.split("@")
        name, domain = parts[0], parts[1]
        if len(name) <= 2:
            masked_name = name[0] + "*"
        else:
            masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
        return f"{masked_name}@{domain}"
    
    # Check if Phone (10-13 digits)
    clean_digits = re.sub(r"[^\d+]", "", value)
    if len(clean_digits) >= 10:
        return clean_digits[:4] + "*" * (len(clean_digits) - 6) + clean_digits[-2:]
    
    return value[:2] + "****"

def verify_razorpay_signature(
    raw_payload: bytes,
    signature: Optional[str],
    secret: Optional[str] = None,
    timestamp: Optional[int] = None,
    max_drift_seconds: int = 300,
    previous_secret: Optional[str] = None,
    require_timestamp: bool = False,
) -> bool:
    """
    Timing-Attack Resistant HMAC SHA-256 Webhook Signature Verification.
    Supports active + previous secret rotation ring, strict replay timestamp validation,
    and constant-time comparison.
    """
    if not signature:
        logger.warning("[SECURITY] Missing X-Razorpay-Signature header.")
        return False

    if require_timestamp and timestamp is None:
        logger.warning("[SECURITY] Missing required X-Razorpay-Event-Time header.")
        return False

    # Replay attack protection (explicit None check so timestamp=0 cannot bypass drift validation)
    if timestamp is not None:
        current_time = int(time.time())
        if abs(current_time - timestamp) > max_drift_seconds:
            logger.warning(f"[SECURITY] Webhook timestamp drifted by {abs(current_time - timestamp)}s > {max_drift_seconds}s. Rejecting replay.")
            return False

    candidate_secrets = []
    primary = secret if secret is not None else settings.RAZORPAY_WEBHOOK_SECRET
    if primary:
        candidate_secrets.append(primary)
    prev = previous_secret if previous_secret is not None else settings.RAZORPAY_WEBHOOK_SECRET_PREVIOUS
    if prev:
        candidate_secrets.append(prev)

    if not candidate_secrets:
        logger.error("[SECURITY] RAZORPAY_WEBHOOK_SECRET is not configured.")
        return False

    sig_bytes = signature.encode("utf-8")
    matched = False
    for sec in candidate_secrets:
        expected_signature = hmac.new(
            key=sec.encode("utf-8"),
            msg=raw_payload,
            digestmod=hashlib.sha256,
        ).hexdigest()
        if constant_time.bytes_eq(expected_signature.encode("utf-8"), sig_bytes):
            matched = True

    if not matched:
        logger.warning("[SECURITY] Cryptographic signature mismatch.")
    return matched

class DistributedIdempotencyStore:
    """
    Atomic Distributed Mutex Lock & Durable Execution Store.
    Supports Redis distributed lock with SQLite WAL-backed local fallback.
    Guarantees strict once-and-only-once execution per (merchant_id + payment_id).
    Features multi-tenant isolation with merchant_api_key_id.
    """

    _REDIS_CAS_RELEASE_LUA = (
        "local v = redis.call('get', KEYS[1]) "
        "if v == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
    )

    def __init__(self, db_path: Optional[str] = None, redis_url: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.redis_client = None
        self._owners_lock = threading.Lock()
        self._active_owners: Dict[tuple, str] = {}

        target_redis = redis_url or os.getenv("REDIS_URL") or settings.REDIS_URL
        if target_redis and redis:
            try:
                # Fast 0.15s socket timeout prevents startup/turn latency spikes on unreachable Redis
                self.redis_client = redis.Redis.from_url(target_redis, decode_responses=True, socket_timeout=0.15, socket_connect_timeout=0.15)
                self.redis_client.ping()
                logger.info("[SECURITY] Connected to distributed Redis lock manager.")
            except Exception as e:
                logger.warning(f"[SECURITY] Redis not reachable ({e}). Falling back to local SQLite WAL mutex.")
                self.redis_client = None

        self._init_db()

    _TABLE_DDL = """
        CREATE TABLE IF NOT EXISTS {name} (
            idempotency_key TEXT NOT NULL,
            merchant_api_key_id TEXT NOT NULL DEFAULT 'default_merchant',
            payload_hash TEXT NOT NULL,
            created_at REAL NOT NULL,
            status TEXT NOT NULL,
            owner_token TEXT,
            result_payload TEXT,
            completed_at REAL,
            PRIMARY KEY (merchant_api_key_id, idempotency_key)
        )
    """

    @staticmethod
    def _is_legacy_schema(conn) -> bool:
        """Legacy shape: idempotency_key alone was the PRIMARY KEY (one global namespace across merchants)."""
        info = conn.execute("PRAGMA table_info(idempotency_keys)").fetchall()
        pk = {c[1]: c[5] for c in info}
        return bool(info) and pk.get("idempotency_key") == 1 and pk.get("merchant_api_key_id", 0) == 0

    def _init_db(self):
        conn = get_db_connection(self.db_path)
        exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='idempotency_keys'").fetchone()
        if not exists:
            with conn:
                conn.execute(self._TABLE_DDL.format(name="idempotency_keys"))
        else:
            # Backward-compatible column adds for very old databases
            columns = [c[1] for c in conn.execute("PRAGMA table_info(idempotency_keys)").fetchall()]
            with conn:
                if "merchant_api_key_id" not in columns:
                    conn.execute("ALTER TABLE idempotency_keys ADD COLUMN merchant_api_key_id TEXT DEFAULT 'default_merchant'")
                if "owner_token" not in columns:
                    conn.execute("ALTER TABLE idempotency_keys ADD COLUMN owner_token TEXT")
                if "result_payload" not in columns:
                    conn.execute("ALTER TABLE idempotency_keys ADD COLUMN result_payload TEXT")
                if "completed_at" not in columns:
                    conn.execute("ALTER TABLE idempotency_keys ADD COLUMN completed_at REAL")
            if self._is_legacy_schema(conn):
                self._migrate_to_per_merchant(conn)
        with conn:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_idem_time ON idempotency_keys (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_idem_key ON idempotency_keys (idempotency_key)")

    def _migrate_to_per_merchant(self, conn) -> None:
        """One-shot, transactional table rebuild: PRIMARY KEY becomes (merchant_api_key_id, idempotency_key).
        All existing rows are preserved (NULL merchant -> 'default_merchant'). Safe if two workers race: the
        second one re-checks the shape after taking the write lock and does nothing."""
        conn.execute("BEGIN IMMEDIATE")
        try:
            if not self._is_legacy_schema(conn):
                conn.execute("COMMIT")
                return
            conn.execute("DROP TABLE IF EXISTS idempotency_keys_v2")
            conn.execute(self._TABLE_DDL.format(name="idempotency_keys_v2"))
            conn.execute(
                "INSERT INTO idempotency_keys_v2 (idempotency_key, merchant_api_key_id, payload_hash, created_at, status, result_payload, completed_at) "
                "SELECT idempotency_key, COALESCE(merchant_api_key_id, 'default_merchant'), payload_hash, created_at, status, result_payload, completed_at FROM idempotency_keys"
            )
            old = conn.execute("SELECT count(*) FROM idempotency_keys").fetchone()[0]
            new = conn.execute("SELECT count(*) FROM idempotency_keys_v2").fetchone()[0]
            if old != new:
                raise RuntimeError(f"idempotency migration row mismatch {old}!={new}")
            conn.execute("DROP TABLE idempotency_keys")
            conn.execute("ALTER TABLE idempotency_keys_v2 RENAME TO idempotency_keys")
            conn.execute("COMMIT")
            logger.info(f"[SECURITY] Migrated idempotency_keys to per-merchant primary key ({new} rows preserved).")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    def _resolve_merchant(self, conn, key: str, merchant_id: Optional[str]) -> str:
        """Explicit merchant wins. Without one, use the only merchant that owns this key, else the default tenant."""
        if merchant_id is not None:
            return merchant_id
        rows = conn.execute("SELECT merchant_api_key_id FROM idempotency_keys WHERE idempotency_key = ?", (key,)).fetchall()
        return rows[0][0] if len(rows) == 1 else "default_merchant"

    def acquire_lock_with_token(
        self,
        key: str,
        payload_hash: str = "",
        ttl_seconds: int = 86400,
        merchant_id: str = "default_merchant",
    ) -> tuple[bool, Optional[str]]:
        """
        Atomic CAS lock acquisition returning `(acquired, owner_token)` scoped per (merchant_id, key).
        Provides lock ownership fencing via unique `owner_token` across both Redis (`SET NX EX`) and SQLite WAL.
        """
        owner_token = f"own_{uuid.uuid4().hex[:16]}"
        redis_key = f"idempotency:{merchant_id}:{key}"
        redis_val = f"ACQUIRED:{owner_token}"
        if self.redis_client:
            try:
                redis_acquired = self.redis_client.set(redis_key, redis_val, nx=True, ex=ttl_seconds)
                if not redis_acquired:
                    return False, None
            except Exception as e:
                logger.warning(f"[SECURITY] Redis acquire_lock error ({e}). Falling back to SQLite WAL.")

        conn = get_db_connection(self.db_path)
        now = time.time()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO idempotency_keys (idempotency_key, merchant_api_key_id, payload_hash, created_at, status, owner_token) VALUES (?, ?, ?, ?, ?, ?)",
                    (key, merchant_id, payload_hash, now, "ACQUIRED", owner_token)
                )
            with self._owners_lock:
                self._active_owners[(merchant_id, key)] = owner_token
            return True, owner_token
        except sqlite3.IntegrityError:
            with conn:
                cur = conn.execute(
                    "UPDATE idempotency_keys SET created_at = ?, payload_hash = ?, status = 'RENEWED', owner_token = ? "
                    "WHERE idempotency_key = ? AND merchant_api_key_id = ? AND status != 'COMPLETED' AND (? - created_at) > ?",
                    (now, payload_hash, owner_token, key, merchant_id, now, ttl_seconds)
                )
                if cur.rowcount == 1:
                    with self._owners_lock:
                        self._active_owners[(merchant_id, key)] = owner_token
                    return True, owner_token
                # Release Redis key if we acquired it transiently before SQLite conflict
                if self.redis_client:
                    try:
                        self.redis_client.eval(self._REDIS_CAS_RELEASE_LUA, 1, redis_key, redis_val)
                    except Exception:
                        pass
                return False, None

    def acquire_lock(self, key: str, payload_hash: str = "", ttl_seconds: int = 86400, merchant_id: str = "default_merchant") -> bool:
        """Atomic CAS lock acquisition, scoped per (merchant_id, key)."""
        acquired, _ = self.acquire_lock_with_token(
            key=key,
            payload_hash=payload_hash,
            ttl_seconds=ttl_seconds,
            merchant_id=merchant_id,
        )
        return acquired

    def release_lock(self, key: str, merchant_id: Optional[str] = None, owner_token: Optional[str] = None) -> bool:
        """Owner-verified Compare-And-Swap lock release (Lua atomic check-and-del in Redis + SQLite cleanup)."""
        conn = get_db_connection(self.db_path)
        mid = self._resolve_merchant(conn, key, merchant_id)
        if owner_token is None:
            with self._owners_lock:
                owner_token = self._active_owners.get((mid, key))
        if not owner_token:
            return False

        redis_released = True
        if self.redis_client:
            try:
                redis_key = f"idempotency:{mid}:{key}"
                res = self.redis_client.eval(self._REDIS_CAS_RELEASE_LUA, 1, redis_key, f"ACQUIRED:{owner_token}")
                redis_released = bool(res)
            except Exception as e:
                logger.warning(f"[SECURITY] Redis release_lock error ({e}).")
                redis_released = False

        with conn:
            cur = conn.execute(
                "DELETE FROM idempotency_keys WHERE idempotency_key = ? AND merchant_api_key_id = ? AND owner_token = ? AND status != 'COMPLETED'",
                (key, mid, owner_token),
            )
        if cur.rowcount == 1:
            with self._owners_lock:
                self._active_owners.pop((mid, key), None)
            return True and redis_released
        return False

    def mark_completed(
        self,
        key: str,
        result_payload: Optional[dict] = None,
        merchant_id: Optional[str] = None,
        owner_token: Optional[str] = None,
    ) -> bool:
        """Marks an execution as durably completed for this merchant's key (verifying ownership if token provided)."""
        conn = get_db_connection(self.db_path)
        now = time.time()
        result_json = json.dumps(result_payload) if result_payload else None
        mid = self._resolve_merchant(conn, key, merchant_id)

        if owner_token is not None:
            with conn:
                cur = conn.execute(
                    "UPDATE idempotency_keys SET status = 'COMPLETED', result_payload = ?, completed_at = ? "
                    "WHERE idempotency_key = ? AND merchant_api_key_id = ? AND owner_token = ?",
                    (result_json, now, key, mid, owner_token),
                )
            if cur.rowcount == 0:
                return False
        else:
            with conn:
                conn.execute(
                    "UPDATE idempotency_keys SET status = 'COMPLETED', result_payload = ?, completed_at = ? "
                    "WHERE idempotency_key = ? AND merchant_api_key_id = ?",
                    (result_json, now, key, mid),
                )

        if self.redis_client:
            try:
                redis_key = f"idempotency:{mid}:{key}"
                self.redis_client.set(redis_key, "COMPLETED", ex=86400 * 7)
            except Exception as e:
                logger.warning(f"[SECURITY] Redis mark_completed error ({e}).")
        with self._owners_lock:
            self._active_owners.pop((mid, key), None)
        return True

    def get_execution_record(self, key: str, merchant_id: Optional[str] = None) -> Optional[dict]:
        """Retrieves the durable execution record for this merchant's key."""
        conn = get_db_connection(self.db_path)
        mid = self._resolve_merchant(conn, key, merchant_id)
        cursor = conn.cursor()
        cursor.execute("SELECT idempotency_key, payload_hash, created_at, status, result_payload, completed_at, merchant_api_key_id FROM idempotency_keys WHERE idempotency_key = ? AND merchant_api_key_id = ?", (key, mid))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "idempotency_key": row[0],
            "payload_hash": row[1],
            "created_at": row[2],
            "status": row[3],
            "result_payload": json.loads(row[4]) if row[4] else None,
            "completed_at": row[5],
            "merchant_api_key_id": row[6]
        }

    def purge_completed(self, older_than_seconds: float = 90 * 86400) -> int:
        """
        Retention: delete COMPLETED keys older than the retention window (default 90 days) so the table does not grow
        forever. Never touches ACQUIRED/RENEWED rows (in-flight work). Returns the number of rows removed.
        Not scheduled automatically: callers choose when, because a purged key can be executed again.
        """
        conn = get_db_connection(self.db_path)
        cutoff = time.time() - older_than_seconds
        with conn:
            cur = conn.execute(
                "DELETE FROM idempotency_keys WHERE status = 'COMPLETED' AND completed_at IS NOT NULL AND completed_at < ?",
                (cutoff,),
            )
        return cur.rowcount

    def is_execution_completed(self, key: str, merchant_id: Optional[str] = None) -> bool:
        """
        Checks if the action for this merchant's idempotency key was already completed.
        """
        rec = self.get_execution_record(key, merchant_id)
        return rec is not None and rec.get("status") == "COMPLETED"

idempotency_store = DistributedIdempotencyStore()

