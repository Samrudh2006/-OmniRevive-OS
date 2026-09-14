import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.app.gateways import multi_rail_router

router = APIRouter(prefix="/api/v1/gateways", tags=["Multi-Rail Gateways"])

class SelectRailRequest(BaseModel):
    rail_id: str = Field(..., description="ID of rail to activate: universal_auto, juspay, phonepe, cred, cashfree, neobank, stripe, razorpay")

class SimulateRecoveryRequest(BaseModel):
    rail_id: Optional[str] = Field(default="universal_auto", description="Target rail or universal_auto")
    amount: float = Field(default=85000.0, description="Payment amount in INR")
    payment_id: Optional[str] = Field(default=None, description="Optional payment ID")
    customer_name: Optional[str] = Field(default="Vikram Sharma", description="Customer full name")
    customer_email: Optional[str] = Field(default="vikram.sharma@fintechcorp.in", description="Customer email")
    customer_phone: Optional[str] = Field(default="+91 98765 43210", description="Customer phone")
    discount_amount: Optional[float] = Field(default=500.0, description="Incentive discount")
    is_mandate: Optional[bool] = Field(default=False, description="Whether this is a recurring mandate")

@router.get("/rails")
def get_supported_rails():
    """
    Returns comprehensive metadata for all Indian and Global fintech rails supported
    by OmniRevive-OS, including Juspay, PhonePe, CRED, Cashfree, Groww/Jupiter, and Stripe.
    """
    return {
        "success": True,
        "data": multi_rail_router.get_supported_rails_meta(),
        "timestamp": time.time()
    }

@router.post("/select")
def select_active_rail(req: SelectRailRequest):
    """
    Switches the active payment rail or sets to 'universal_auto' for autonomous routing.
    """
    success = multi_rail_router.set_active_rail(req.rail_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rail ID '{req.rail_id}'. Supported: universal_auto, juspay, phonepe, cred, cashfree, neobank, stripe, razorpay"
        )
    return {
        "success": True,
        "message": f"Active recovery rail successfully switched to: {req.rail_id.upper()}",
        "active_rail": multi_rail_router.active_rail,
        "timestamp": time.time()
    }

@router.post("/simulate")
def simulate_multi_rail_recovery(req: SimulateRecoveryRequest):
    """
    Executes a high-fidelity simulation of an autonomous recovery through any specific
    fintech rail (Juspay HyperSDK, PhonePe Switch, CRED Pay, Cashfree, Neobanks, etc.).
    """
    pid = req.payment_id or f"pay_sim_{uuid.uuid4().hex[:8]}"
    
    # Temporarily set rail if requested
    original_rail = multi_rail_router.active_rail
    if req.rail_id:
        multi_rail_router.set_active_rail(req.rail_id)

    try:
        if req.is_mandate:
            recovery_result = multi_rail_router.schedule_mandate_retry(
                mandate_id=f"man_{pid}",
                amount=req.amount,
                scheduled_epoch=time.time() + 3600
            )
        else:
            recovery_result = multi_rail_router.create_recovery_link(
                payment_id=pid,
                amount=req.amount,
                customer_name=req.customer_name or "Valued Client",
                customer_email=req.customer_email or "client@example.com",
                customer_phone=req.customer_phone or "+919876543210",
                discount_amount=req.discount_amount or 0.0
            )
    finally:
        # Restore original rail if changed
        if req.rail_id:
            multi_rail_router.set_active_rail(original_rail)

    return {
        "success": True,
        "simulated_rail": req.rail_id,
        "data": recovery_result,
        "timestamp": time.time()
    }
