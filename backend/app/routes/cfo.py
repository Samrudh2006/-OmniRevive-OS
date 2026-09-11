import time
import uuid
from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from backend.app.schemas import CFOApprovalItem
from backend.app.services.cfo_service import cfo_service
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/cfo", tags=["Executive CFO Governance & Approval Gating"])

class CFOActionPayload(BaseModel):
    approval_id: str = Field(..., description="CFO approval item ID to decide")
    notes: Optional[str] = Field(default="Approved after manual risk review", description="Executive notes")

@router.get("/queue", summary="Fetch Pending & Historical CFO Approval Requests")
async def list_cfo_queue(request: Request, status: Optional[str] = None, limit: int = 50):
    """
    Returns high-value transactions and statutory invoice disputes requiring executive CFO review.
    Enforces Zero-Trust boundary rules and audit trail visibility.
    """
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    items = cfo_service.list_queue(status=status, limit=limit)
    return {
        "success": True,
        "data": {
            "total_items": len(items),
            "queue": [it.model_dump() for it in items]
        },
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/{approval_id}", summary="Get Specific CFO Approval Record Details")
async def get_cfo_approval_item(approval_id: str, request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    item = cfo_service.get_approval(approval_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CFO Approval {approval_id} not found.")
    return {
        "success": True,
        "data": item.model_dump(),
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.post("/approve", summary="Authorize & Execute High-Value Recovery via Cedar CFO Policy")
async def approve_cfo_escalation(payload: CFOActionPayload, request: Request):
    """
    Approve an escalated item. Enforces AWS Cedar `Role::CFO` policy validation,
    transitions state: PENDING_APPROVAL -> APPROVED -> EXECUTED, and commits to SHA-256 ledger.
    """
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    _, actor, _ = auth_service.verify_request_auth(request, required_role="Role::CFO")
    
    # If in demo mode, treat operator as CFO
    if actor == "Role::Demo_Operator":
        actor = "Role::CFO"

    try:
        updated = cfo_service.process_decision(
            approval_id=payload.approval_id,
            action="APPROVE",
            actor=actor,
            notes=payload.notes or "Executive approved",
            trace_id=trace_id
        )
        return {
            "success": True,
            "data": updated.model_dump(),
            "message": f"Approval {payload.approval_id} authorized and transitioned to EXECUTED.",
            "trace_id": trace_id,
            "timestamp": time.time()
        }
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.post("/reject", summary="Reject High-Value Recovery Proposal")
async def reject_cfo_escalation(payload: CFOActionPayload, request: Request):
    """
    Rejects an escalated recovery proposal. Transitions state to REJECTED and commits audit log.
    """
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    _, actor, _ = auth_service.verify_request_auth(request, required_role="Role::CFO")
    
    if actor == "Role::Demo_Operator":
        actor = "Role::CFO"

    try:
        updated = cfo_service.process_decision(
            approval_id=payload.approval_id,
            action="REJECT",
            actor=actor,
            notes=payload.notes or "Executive rejected",
            trace_id=trace_id
        )
        return {
            "success": True,
            "data": updated.model_dump(),
            "message": f"Approval {payload.approval_id} rejected.",
            "trace_id": trace_id,
            "timestamp": time.time()
        }
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
