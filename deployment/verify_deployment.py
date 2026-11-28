"""
OmniRevive-OS Deployment & SRE Verification Smoke Suite.

Usage:
    python deployment/verify_deployment.py
    python deployment/verify_deployment.py --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _make_inprocess_fetcher() -> Callable[[str], Tuple[int, str, Optional[Dict[str, Any]]]]:
    """Build an in-process FastAPI TestClient requester with background daemons disabled."""
    os.environ.setdefault("OMNIREVIVE_DISABLE_DAEMONS", "1")
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    def _fetch(path: str) -> Tuple[int, str, Optional[Dict[str, Any]]]:
        resp = client.get(path)
        parsed = None
        try:
            parsed = resp.json()
        except Exception:
            parsed = None
        return resp.status_code, resp.text, parsed

    return _fetch


def _make_http_fetcher(base_url: str) -> Callable[[str], Tuple[int, str, Optional[Dict[str, Any]]]]:
    """Build a live HTTP requester using standard library urllib."""
    root = base_url.rstrip("/")

    def _fetch(path: str) -> Tuple[int, str, Optional[Dict[str, Any]]]:
        url = f"{root}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json, text/html"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = exc.read().decode("utf-8", errors="replace")
        parsed = None
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = None
        return status, body, parsed

    return _fetch


def run_verification(base_url: Optional[str] = None) -> Dict[str, Any]:
    """Execute read-only SRE smoke checks and return structured verification results."""
    fetch = _make_http_fetcher(base_url) if base_url else _make_inprocess_fetcher()
    checks = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})

    # 1. /health
    st, _, data = fetch("/health")
    ok = st == 200 and isinstance(data, dict) and data.get("data", {}).get("status") == "healthy"
    record("health", ok, f"status={st}, version={data.get('data', {}).get('version') if data else None}")

    # 2. /health/live
    st, _, data = fetch("/health/live")
    ok = st == 200 and isinstance(data, dict) and data.get("data", {}).get("status") == "alive"
    record("liveness_probe", ok, f"status={st}")

    # 3. /health/ready
    st, _, data = fetch("/health/ready")
    ready_checks = data.get("data", {}).get("checks", {}) if isinstance(data, dict) else {}
    ok = (
        st == 200
        and ready_checks.get("database", {}).get("status") == "up"
        and ready_checks.get("audit_chain", {}).get("status") == "up"
    )
    record("readiness_probe", ok, f"status={st}, checks={ready_checks}")

    # 4. /metrics
    st, text, _ = fetch("/metrics")
    ok = st == 200 and ("# HELP" in text or "omnirevive_" in text or "process_" in text)
    record("prometheus_metrics", ok, f"status={st}, bytes={len(text)}")

    # 5. /docs
    st, text, _ = fetch("/docs")
    ok = st == 200 and "SwaggerUIBundle" in text
    record("swagger_docs", ok, f"status={st}")

    # 6. /openapi.json
    st, _, data = fetch("/openapi.json")
    path_count = len(data.get("paths", {})) if isinstance(data, dict) else 0
    ok = st == 200 and path_count >= 140
    record("openapi_schema", ok, f"status={st}, paths={path_count}")

    # 7. /api/v1/audit/verify
    st, _, data = fetch("/api/v1/audit/verify")
    audit_valid = data.get("data", {}).get("valid") if isinstance(data, dict) else None
    ok = st == 200 and audit_valid is True
    record("merkle_audit_verify", ok, f"status={st}, valid={audit_valid}")

    # 8. /aws/cedar/policies
    st, _, data = fetch("/aws/cedar/policies")
    rule_count = data.get("data", {}).get("rule_count", 0) if isinstance(data, dict) else 0
    ok = st == 200 and rule_count >= 5
    record("cedar_policies", ok, f"status={st}, rule_count={rule_count}")

    all_passed = all(c["passed"] for c in checks)
    return {
        "target": base_url or "inprocess://backend.app.main:app",
        "all_passed": all_passed,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OmniRevive-OS deployment health and safety endpoints.")
    parser.add_argument("--base-url", default=None, help="Optional remote/local HTTP base URL to test.")
    args = parser.parse_args()

    result = run_verification(base_url=args.base_url)
    print(json.dumps(result, indent=2))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
