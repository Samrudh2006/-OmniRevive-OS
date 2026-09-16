import time
import uuid
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

from backend.app.b2b.invoice_store import invoice_store
from backend.app.communication.dispatch_engine import dispatch_engine
from backend.app.audit_store import audit_store

router = APIRouter()

class EmailDispatchRequest(BaseModel):
    invoice_id: str = "inv_enterprise_998"
    recipient_email: Optional[str] = None
    subject: Optional[str] = None
    custom_note: Optional[str] = None

@router.post("/api/v1/communication/email/send", tags=["Communication Dispatch"], summary="Dispatch Authentic Corporate Tax Invoice Email")
async def send_invoice_email_endpoint(req: EmailDispatchRequest, request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    inv = invoice_store.get_invoice(req.invoice_id)
    if not inv:
        inv = invoice_store.get_invoice("inv_enterprise_998")

    dispatch = dispatch_engine.dispatch_email(
        to_email=req.recipient_email or (inv.customer_email if inv else "finance@acmepvt.com"),
        invoice_id=req.invoice_id,
        subject=req.subject or "",
        custom_note=req.custom_note or ""
    )

    audit_store.record_event(
        trace_id=trace_id,
        merchant_id="merchant_123",
        payment_id=req.invoice_id,
        event_type="communication.email.dispatched",
        failure_class="DISPATCH",
        decision={"recipient": dispatch.recipient, "subject": dispatch.subject},
        policy_verdict="ALLOWED",
        action_taken="DISPATCH_EMAIL",
        gateway_result={"dispatch_id": dispatch.dispatch_id}
    )

    return {
        "success": True,
        "data": dispatch.model_dump(),
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/api/v1/communication/recent", tags=["Communication Dispatch"], summary="List Recent Sent Communications")
async def list_recent_communications(request: Request, limit: int = 20):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}") if request else f"tr_{uuid.uuid4().hex[:12]}"
    items = dispatch_engine.list_recent(limit=limit)
    return {
        "success": True,
        "data": {
            "total": len(items),
            "dispatches": [item.model_dump() for item in items]
        },
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/api/v1/communication/{dispatch_id}", tags=["Communication Dispatch"], summary="Get Single Dispatch Details")
async def get_dispatch_details(dispatch_id: str, request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    item = dispatch_engine.get_dispatch(dispatch_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Dispatch {dispatch_id} not found.")
    return {
        "success": True,
        "data": item.model_dump(),
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/api/v1/communication/{dispatch_id}/html", tags=["Communication Dispatch"], summary="Render Raw HTML Email for In-Browser Preview")
async def render_dispatch_html(dispatch_id: str):
    item = dispatch_engine.get_dispatch(dispatch_id)
    if not item or not item.rendered_html:
        inv = invoice_store.get_invoice("inv_enterprise_998")
        if inv:
            html = dispatch_engine.generate_html_invoice_email(inv, custom_note="Live rendered tax invoice advice.")
            return HTMLResponse(content=html, status_code=200)
        raise HTTPException(status_code=404, detail="Email body not found.")
    return HTMLResponse(content=item.rendered_html, status_code=200)
