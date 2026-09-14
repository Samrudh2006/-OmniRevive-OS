import time
import uuid
import logging
from typing import Dict, Any, Optional
from backend.app.gateways.base import PaymentGateway

logger = logging.getLogger("OmniRevive.Gateway.Cashfree")

class CashfreeAdapter(PaymentGateway):
    """
    Cashfree Payments Gateway Adapter.
    Specialized for B2B Auto-Collect Virtual Account Numbers (VAN),
    Subscription e-Mandate auto-retry orchestration, and high-volume merchant links.
    """

    def __init__(self, app_id: str = "CF_APP_OMNI_TEST", secret_key: str = "cf_sec_mock_key"):
        self.app_id = app_id
        self.secret_key = secret_key

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
        cf_link_id = f"cf_link_{payment_id.split('_')[-1][:10]}"
        virtual_account_no = f"CFVAN{payment_id.split('_')[-1][:8].upper()}"
        expire_by_epoch = int(time.time()) + (expire_by_minutes * 60)

        return {
            "success": True,
            "provider": "CASHFREE",
            "mode": "CASHFREE_PAYMENT_LINKS_API",
            "link_id": cf_link_id,
            "virtual_account_number": virtual_account_no,
            "virtual_vpa": f"{virtual_account_no.lower()}@yesbank",
            "payment_link_id": f"plink_cf_{cf_link_id}",
            "short_url": f"https://payments.cashfree.com/links/{cf_link_id}",
            "upi_qr_url": f"upi://pay?pa={virtual_account_no.lower()}@yesbank&pn=Cashfree+AutoCollect&am={final_amount:.2f}&cu=INR",
            "final_amount": final_amount,
            "discount_applied": discount_amount,
            "expire_by": expire_by_epoch,
            "auto_collect_status": "VIRTUAL_ACCOUNT_ACTIVE"
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
            "provider": "CASHFREE",
            "mode": "CASHFREE_SUBSCRIPTIONS_AUTOPAY",
            "mandate_id": mandate_id,
            "sub_reference_id": f"cf_sub_{mandate_id}",
            "amount": amount,
            "scheduled_epoch": scheduled_epoch,
            "attempt_count": attempt_count,
            "status": "CASHFREE_SUBSCRIPTION_RETRY_ACTIVE"
        }

    def mutate_invoice(
        self,
        invoice_id: str,
        mutations: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "CASHFREE",
            "invoice_id": invoice_id,
            "mutations_applied": mutations,
            "status": "CASHFREE_INVOICE_MUTATED",
            "revised_url": f"https://payments.cashfree.com/invoices/{invoice_id}"
        }
