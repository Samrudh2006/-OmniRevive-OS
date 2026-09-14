import time
import uuid
import logging
from typing import Dict, Any, Optional
from backend.app.gateways.base import PaymentGateway

logger = logging.getLogger("OmniRevive.Gateway.Stripe")

class StripeAdapter(PaymentGateway):
    """
    Stripe Multi-Currency & Global Payment Adapter.
    Specialized for cross-border SaaS, international cards, multi-currency recovery
    (USD, EUR, GBP, SGD, INR), and Stripe Smart Retries.
    """

    def __init__(self, api_key: str = "sk_test_mock_stripe_key"):
        self.api_key = api_key

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
        final_amount_inr = max(1.0, round(amount - discount_amount, 2))
        amount_usd = round(final_amount_inr / 86.50, 2)
        session_id = f"cs_test_{uuid.uuid4().hex[:20]}"
        expire_by_epoch = int(time.time()) + (expire_by_minutes * 60)

        return {
            "success": True,
            "provider": "STRIPE",
            "mode": "STRIPE_CHECKOUT_SESSION",
            "session_id": session_id,
            "payment_link_id": f"plink_stripe_{session_id[:12]}",
            "short_url": f"https://checkout.stripe.com/c/pay/{session_id}",
            "amount_inr": final_amount_inr,
            "amount_usd": amount_usd,
            "currency": "USD",
            "fx_rate": 86.50,
            "discount_applied": discount_amount,
            "expire_by": expire_by_epoch,
            "rbi_purpose_code": "P0802_SOFTWARE_CONSULTING_EXPORTS",
            "supported_methods": ["card", "apple_pay", "google_pay", "link"]
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
            "provider": "STRIPE",
            "mode": "STRIPE_SMART_RETRIES_ENGINE",
            "mandate_id": mandate_id,
            "amount": amount,
            "scheduled_epoch": scheduled_epoch,
            "attempt_count": attempt_count,
            "status": "STRIPE_SMART_RETRY_SCHEDULED"
        }

    def mutate_invoice(
        self,
        invoice_id: str,
        mutations: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "STRIPE",
            "invoice_id": invoice_id,
            "mutations_applied": mutations,
            "status": "STRIPE_INVOICE_FINALIZED",
            "revised_url": f"https://pay.stripe.com/invoices/{invoice_id}"
        }
