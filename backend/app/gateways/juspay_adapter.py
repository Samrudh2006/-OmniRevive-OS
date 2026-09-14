import time
import uuid
import logging
from typing import Dict, Any, Optional
from backend.app.gateways.base import PaymentGateway

logger = logging.getLogger("OmniRevive.Gateway.Juspay")

class JuspayHyperSDKAdapter(PaymentGateway):
    """
    Juspay HyperSDK & Multi-Switch Routing Adapter.
    Specialized for ultra-low latency UPI switches, smart routing across bank gateways
    (HDFC, SBI, ICICI, Axis), and mobile HyperSDK Express Checkout sessions.
    """

    def __init__(self, merchant_id: str = "juspay_enterprise_omni", api_key: str = "jus_live_sec_mock"):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.supported_switches = ["HDFC_SWITCH", "SBI_SWITCH", "ICICI_SWITCH", "AXIS_SWITCH"]

    def create_recovery_link(
        self,
        payment_id: str,
        amount: float,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        discount_amount: float = 0.0,
        expire_by_minutes: int = 1440
    ) -> Dict[str, Any]:
        final_amount = max(1.0, round(amount - discount_amount, 2))
        order_id = f"jus_ord_{payment_id.split('_')[-1][:10]}"
        hyper_session_id = f"hyp_sess_{uuid.uuid4().hex[:12]}"
        expire_by_epoch = int(time.time()) + (expire_by_minutes * 60)

        # Smart Switch Selection based on hypothetical NPCI telemetry
        selected_switch = "ICICI_SWITCH" if amount > 25000 else "HDFC_SWITCH"

        return {
            "success": True,
            "provider": "JUSPAY",
            "mode": "JUSPAY_HYPERSDK_ORCHESTRATION",
            "order_id": order_id,
            "hyper_session_id": hyper_session_id,
            "selected_switch": selected_switch,
            "switch_routing_weights": {
                "HDFC_SWITCH": 0.40,
                "ICICI_SWITCH": 0.35,
                "AXIS_SWITCH": 0.20,
                "SBI_SWITCH": 0.05
            },
            "payment_link_id": f"plink_jus_{order_id}",
            "short_url": f"https://api.juspay.in/orders/{order_id}/exec",
            "upi_intent_url": f"upi://pay?pa=juspay.{self.merchant_id}@icici&pn=Juspay+Merchant&am={final_amount:.2f}&tr={order_id}&cu=INR",
            "final_amount": final_amount,
            "discount_applied": discount_amount,
            "expire_by": expire_by_epoch,
            "sdk_payload": {
                "action": "paymentPage",
                "hyperSdkVersion": "2.1.18",
                "clientId": self.merchant_id,
                "amount": str(final_amount),
                "currency": "INR",
                "environment": "production_sandbox"
            }
        }

    def schedule_mandate_retry(
        self,
        mandate_id: str,
        amount: float,
        scheduled_epoch: float,
        attempt_count: int = 1
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "JUSPAY",
            "mode": "JUSPAY_AUTOPAY_SWITCH",
            "mandate_id": mandate_id,
            "amount": amount,
            "scheduled_epoch": scheduled_epoch,
            "attempt_count": attempt_count,
            "recommended_switch": "ICICI_MANDATE_ENGINE",
            "status": "JUSPAY_MANDATE_RETRY_SCHEDULED"
        }

    def mutate_invoice(
        self,
        invoice_id: str,
        mutations: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "JUSPAY",
            "invoice_id": invoice_id,
            "mutations_applied": mutations,
            "status": "MUTATED_VIA_JUSPAY_ORDERS",
            "revised_order_url": f"https://api.juspay.in/orders/{invoice_id}/review"
        }
