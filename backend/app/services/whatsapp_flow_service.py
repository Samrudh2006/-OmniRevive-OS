"""
OmniRevive-OS | WhatsApp Flow 2.0 In-Chat UPI Payment Builder
Constructs Meta WhatsApp Cloud API interactive Flow 2.0 payloads with
NPCI UPI 2.0 deep-links and AWS Cedar discount clamping.
"""

from __future__ import annotations

import math
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class WhatsAppFlowPayload:
    """Structured WhatsApp Flow 2.0 interactive payment message."""

    recipient_phone: str
    invoice_id: str
    original_amount_inr: float
    discount_applied_inr: float
    payable_amount_inr: float
    upi_intent_uri: str
    flow_message: Dict[str, Any]


def clamp_cedar_discount(amount_inr: float, proposed_discount_pct: float) -> float:
    """Enforce AWS Cedar discount guardrail: min(10%, INR 500), non-negative."""
    if not (math.isfinite(amount_inr) and math.isfinite(proposed_discount_pct)):
        raise ValueError("amount_inr and proposed_discount_pct must be finite")
    if amount_inr <= 0 or proposed_discount_pct <= 0:
        return 0.0
    pct_capped = min(proposed_discount_pct, 10.0)
    raw_discount = round(amount_inr * (pct_capped / 100.0), 2)
    return min(raw_discount, 500.0)


def build_whatsapp_flow_upi_payload(
    recipient_phone: str,
    invoice_id: str,
    amount_inr: float,
    merchant_vpa: str = "omnirevive@icici",
    merchant_name: str = "OmniRevive Enterprise",
    proposed_discount_pct: float = 0.0,
    flow_id: str = "flow_omnirevive_upi_v2",
    flow_token: Optional[str] = None,
) -> WhatsAppFlowPayload:
    """Build a WhatsApp Flow 2.0 in-chat UPI payment payload with Cedar bounds."""
    if not math.isfinite(amount_inr) or amount_inr <= 0:
        raise ValueError("amount_inr must be a finite positive number")
    if not recipient_phone or not invoice_id:
        raise ValueError("recipient_phone and invoice_id are required")

    discount = clamp_cedar_discount(amount_inr, proposed_discount_pct)
    payable = round(max(0.01, amount_inr - discount), 2)
    token = flow_token or f"wa_flow_{invoice_id}"

    upi_params = urllib.parse.urlencode(
        {
            "pa": merchant_vpa,
            "pn": merchant_name,
            "tr": invoice_id,
            "tn": f"Invoice {invoice_id} Recovery",
            "am": f"{payable:.2f}",
            "cu": "INR",
        }
    )
    upi_uri = f"upi://pay?{upi_params}"

    flow_message: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {"type": "text", "text": "Instant UPI Recovery"},
            "body": {
                "text": (
                    f"Complete payment for {invoice_id}: "
                    f"INR {payable:,.2f}"
                    + (f" (includes INR {discount:,.2f} fee waiver)" if discount > 0 else "")
                )
            },
            "footer": {"text": "Secured by OmniRevive-OS • NPCI UPI 2.0"},
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": token,
                    "flow_id": flow_id,
                    "flow_cta": "Pay via UPI",
                    "flow_action": "navigate",
                    "flow_action_payload": {
                        "screen": "UPI_INTENT_CHECKOUT",
                        "data": {
                            "invoice_id": invoice_id,
                            "payable_inr": payable,
                            "discount_inr": discount,
                            "upi_intent_uri": upi_uri,
                        },
                    },
                },
            },
        },
    }

    return WhatsAppFlowPayload(
        recipient_phone=recipient_phone,
        invoice_id=invoice_id,
        original_amount_inr=round(amount_inr, 2),
        discount_applied_inr=discount,
        payable_amount_inr=payable,
        upi_intent_uri=upi_uri,
        flow_message=flow_message,
    )
