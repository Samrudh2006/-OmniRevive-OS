import time
import uuid
from fastapi import APIRouter, Request
from backend.app.audit_store import audit_store

router = APIRouter()

@router.get("/api/v1/audit/verify", tags=["Cryptographic Audit Ledger"], summary="Verify SHA-256 Hash Chain Integrity")
async def verify_audit_chain(request: Request):
    """Cryptographic hash chain verification endpoint."""
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    verification = audit_store.verify_chain_integrity()
    return {
        "success": True,
        "data": verification,
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/api/v1/audit/events", tags=["Cryptographic Audit Ledger"], summary="Fetch Sequenced Audit Blocks")
async def get_audit_ledger(limit: int = 50, request: Request = None):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}") if request else f"tr_{uuid.uuid4().hex[:12]}"
    events = audit_store.get_events(limit=limit)
    return {
        "success": True,
        "data": {
            "total_returned": len(events),
            "events": events
        },
        "trace_id": trace_id,
        "timestamp": time.time()
    }
