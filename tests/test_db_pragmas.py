from backend.app.security import get_db_connection


def test_connection_pragmas(tmp_path):
    conn = get_db_connection(str(tmp_path / "p.db"))
    assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 10000
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
