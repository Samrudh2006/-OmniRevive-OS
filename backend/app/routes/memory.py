import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from backend.app.semantic_memory import semantic_memory_engine

logger = logging.getLogger("RazorRevive.MemoryRouter")
router = APIRouter(prefix="/api/v1/memory", tags=["Semantic Memory & Qdrant Engine"])

class PrecedentSearchRequest(BaseModel):
    error_code: str = Field(...)
    bank: str = Field(default="SBI")
    rail: str = Field(default="UPI")
    amount: float = Field(default=1000.0, ge=1.0)
    attempt_count: int = Field(default=1, ge=1, le=5)
    top_k: int = Field(default=3, ge=1, le=10)
    tenant_id: Optional[str] = None

class PrecedentFeedbackRequest(BaseModel):
    case_id: str
    error_code: str
    bank: str
    rail: str
    amount: float
    strategy_applied: str
    recovered: bool
    recovery_latency_sec: int = 300
    tenant_id: str = "default"

@router.get("/telemetry")
@router.get("/stats")
def get_memory_telemetry() -> Dict[str, Any]:
    """Retrieve operational telemetry and health metrics of the Qdrant Semantic Memory Layer."""
    return semantic_memory_engine.get_memory_telemetry()

@router.get("/precedents")
def search_precedents(
    error_code: str = Query(..., description="Error description or failure code"),
    bank: str = Query(default="SBI", description="Issuing bank (SBI, HDFC, ICICI, etc.)"),
    rail: str = Query(default="UPI", description="Payment rail (UPI, CARD, NACH, etc.)"),
    amount: float = Query(default=2500.0, description="Transaction amount in INR"),
    attempt_count: int = Query(default=1, ge=1, le=5),
    top_k: int = Query(default=3, ge=1, le=10),
    tenant_id: Optional[str] = Query(default=None)
) -> Dict[str, Any]:
    """
    Search Qdrant Vector Memory for historical failure recovery precedents.
    Returns nearest cosine vector matches with empirical success rates and recommended workflows.
    """
    matches = semantic_memory_engine.search_precedents(
        error_code=error_code,
        bank=bank,
        rail=rail,
        amount=amount,
        attempt_count=attempt_count,
        top_k=top_k,
        tenant_id=tenant_id
    )
    return {
        "status": "SUCCESS",
        "query": {
            "error_code": error_code,
            "bank": bank,
            "rail": rail,
            "amount": amount,
            "attempt_count": attempt_count
        },
        "matches_count": len(matches),
        "precedents": matches
    }

@router.post("/feedback")
@router.post("/precedents")
def record_recovery_precedent(feedback: PrecedentFeedbackRequest) -> Dict[str, Any]:
    """
    Closed-loop feedback ingestion.
    Records successful or failed recovery resolutions into Qdrant Vector Memory.
    """
    success = semantic_memory_engine.record_recovery_feedback(
        case_id=feedback.case_id,
        error_code=feedback.error_code,
        bank=feedback.bank,
        rail=feedback.rail,
        amount=feedback.amount,
        strategy_applied=feedback.strategy_applied,
        recovered=feedback.recovered,
        recovery_latency_sec=feedback.recovery_latency_sec,
        tenant_id=feedback.tenant_id
    )
    return {
        "status": "RECORDED" if success else "FAILED",
        "case_id": feedback.case_id,
        "recovered": feedback.recovered,
        "strategy": feedback.strategy_applied,
        "vector_memory_updated": success
    }
