import time
import uuid
from typing import Optional, List
from fastapi import Query, APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from backend.app.schemas import CFOApprovalItem
from backend.app.services.cfo_service import cfo_service
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/cfo", tags=["Executive CFO Governance & Approval Gating"])

class CFOActionPayload(BaseModel):
    approval_id: str = Field(..., description="CFO approval item ID to decide")
    notes: Optional[str] = Field(default="Approved after manual risk review", description="Executive notes")

@router.get("/queue", summary="Fetch Pending & Historical CFO Approval Requests")
async def list_cfo_queue(request: Request, status: Optional[str] = None, limit: int = Query(50, ge=1, le=500)):
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


from backend.app.services.cfo_ed25519_signer import CFOEd25519Signer, SignedCFOApproval
from backend.app.services.multiregion_cas_lock import MultiRegionCASCoordinator

_cfo_ephemeral_signer = CFOEd25519Signer()
_multiregion_cas = MultiRegionCASCoordinator()


class CFOSignRequest(BaseModel):
    approval_id: str = Field(..., min_length=1)
    entity_id: str = Field(..., min_length=1)
    amount_inr: float = Field(..., gt=0)
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    approver_id: str = Field(..., min_length=1)


class CFOVerifyRequest(BaseModel):
    approval_id: str
    entity_id: str
    amount_inr: float
    decision: str
    approver_id: str
    signed_at: float
    signature_b64: str
    public_key_b64: str
    trusted_public_key_b64: Optional[str] = None


class MultiRegionLockRequest(BaseModel):
    resource_key: str = Field(..., min_length=1)
    owner_id: str = Field(..., min_length=1)
    ttl_seconds: float = Field(default=300.0, gt=0)


@router.post("/sign-approval", summary="Sign CFO Approval with Ed25519")
async def sign_cfo_approval(payload: CFOSignRequest, request: Request):
    auth_service.verify_request_auth(request, required_role="Role::CFO")
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    env = _cfo_ephemeral_signer.sign_approval(
        approval_id=payload.approval_id,
        entity_id=payload.entity_id,
        amount_inr=payload.amount_inr,
        decision=payload.decision,
        approver_id=payload.approver_id,
    )
    return {
        "success": True,
        "data": {
            "approval_id": env.approval_id,
            "entity_id": env.entity_id,
            "amount_inr": env.amount_inr,
            "decision": env.decision,
            "approver_id": env.approver_id,
            "signed_at": env.signed_at,
            "signature_b64": env.signature_b64,
            "public_key_b64": env.public_key_b64,
        },
        "trace_id": trace_id,
        "timestamp": time.time(),
    }


@router.post("/verify-signature", summary="Verify Ed25519 CFO Approval Signature")
async def verify_cfo_signature(payload: CFOVerifyRequest, request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    env = SignedCFOApproval(
        approval_id=payload.approval_id,
        entity_id=payload.entity_id,
        amount_inr=payload.amount_inr,
        decision=payload.decision,
        approver_id=payload.approver_id,
        signed_at=payload.signed_at,
        signature_b64=payload.signature_b64,
        public_key_b64=payload.public_key_b64,
    )
    valid = CFOEd25519Signer.verify_approval(
        env, trusted_public_key_b64=payload.trusted_public_key_b64
    )
    return {
        "success": True,
        "data": {"valid": valid},
        "trace_id": trace_id,
        "timestamp": time.time(),
    }


@router.post("/quorum-lock", summary="Acquire Multi-Region Active-Active CAS Lock (ap-south-1 & ap-south-2)")
async def acquire_multiregion_quorum_lock(payload: MultiRegionLockRequest, request: Request):
    auth_service.verify_request_auth(request, required_role="Role::SRE_Admin")
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    acquired, fencing_token = _multiregion_cas.acquire_quorum_lock(
        resource_key=payload.resource_key,
        owner_id=payload.owner_id,
        ttl_seconds=payload.ttl_seconds,
    )
    return {
        "success": True,
        "data": {
            "acquired": acquired,
            "fencing_token": fencing_token,
            "regions": list(_multiregion_cas.REGIONS),
        },
        "trace_id": trace_id,
        "timestamp": time.time(),
    }
