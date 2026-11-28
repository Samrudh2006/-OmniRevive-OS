"""Pytest global fixtures to ensure clean SQLite connection and daemon lifecycle teardown."""

import os
import pytest

os.environ.setdefault("OMNIREVIVE_DISABLE_DAEMONS", "1")


@pytest.fixture(autouse=True, scope="session")
def cleanup_db_connections_after_session():
    yield
    try:
        from backend.app.security import close_all_db_connections, idempotency_store
        if getattr(idempotency_store, "redis_client", None):
            try:
                idempotency_store.redis_client.close()
            except Exception:
                pass
        close_all_db_connections()
    except Exception:
        pass
