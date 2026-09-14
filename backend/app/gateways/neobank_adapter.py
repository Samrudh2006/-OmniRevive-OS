import time
import datetime
import logging
from typing import Dict, Any, Optional
from backend.app.gateways.base import PaymentGateway

logger = logging.getLogger("OmniRevive.Gateway.Neobank")

class NeobankMandateAdapter(PaymentGateway):
    """
    Neobank & Wealthtech Mandate Recovery Adapter.
    Tailored for Groww (SIP investments), Jupiter, and Fi Money (automated savings & salary accounts).
    Features Salary-Cycle Heuristic Mandate Scheduling (detects monthly salary credit window
    between 1st-5th of the month to maximize auto-debit success rates).
    """

    def __init__(self, platform_name: str = "GROWW_JUPITER_RECOVERY", client_id: str = "neo_client_omni"):
        self.platform_name = platform_name
        self.client_id = client_id

    def calculate_salary_credit_epoch(self, current_epoch: Optional[float] = None) -> float:
        """
        Heuristic: Computes the timestamp for the 1st of the upcoming month at 10:30 AM IST,
        which corresponds to maximum liquidity in customer bank accounts.
        """
        now = datetime.datetime.fromtimestamp(current_epoch or time.time(), tz=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        
        # If today is between 1st and 5th, retry tomorrow morning at 10:30 AM
        if 1 <= now.day <= 5:
            target_date = now + datetime.timedelta(days=1)
            target_dt = target_date.replace(hour=10, minute=30, second=0, microsecond=0)
        else:
            # Advance to 1st of next month
            year = now.year + (1 if now.month == 12 else 0)
            month = 1 if now.month == 12 else now.month + 1
            target_dt = datetime.datetime(year, month, 1, 10, 30, 0, tzinfo=now.tzinfo)

        return target_dt.timestamp()

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
        sip_ref_id = f"sip_{payment_id.split('_')[-1][:8]}"
        expire_by_epoch = int(time.time()) + (expire_by_minutes * 60)

        return {
            "success": True,
            "provider": "GROWW_JUPITER_FI",
            "mode": "NEOBANK_SMART_MANDATE_LINK",
            "sip_reference_id": sip_ref_id,
            "payment_link_id": f"plink_neo_{sip_ref_id}",
            "short_url": f"https://invest.groww.in/pay/sip/{sip_ref_id}",
            "upi_intent_url": f"upi://pay?pa=sip.{sip_ref_id}@axisbank&pn=Groww+Wealth+Recovery&am={final_amount:.2f}&cu=INR",
            "final_amount": final_amount,
            "discount_applied": discount_amount,
            "expire_by": expire_by_epoch,
            "feature": "1_CLICK_SIP_RETRY"
        }

    def schedule_mandate_retry(
        self,
        mandate_id: str,
        amount: float,
        scheduled_epoch: float,
        attempt_count: int = 1
    ) -> Dict[str, Any]:
        # Optimize scheduled_epoch with Salary-Credit Heuristic
        optimal_salary_epoch = self.calculate_salary_credit_epoch(scheduled_epoch)
        optimal_dt_str = time.strftime("%d %b %Y, %I:%M %p IST", time.gmtime(optimal_salary_epoch + 5.5 * 3600))

        return {
            "success": True,
            "provider": "GROWW_JUPITER_FI",
            "mode": "SALARY_CYCLE_HEURISTIC_AUTOPAY",
            "mandate_id": mandate_id,
            "amount": amount,
            "original_scheduled_epoch": scheduled_epoch,
            "optimized_salary_cycle_epoch": optimal_salary_epoch,
            "optimized_time_formatted": optimal_dt_str,
            "attempt_count": attempt_count,
            "recovery_heuristic": "SALARY_CREDIT_WINDOW_SURPLUS (1st-5th of month)",
            "status": "NEOBANK_SMART_MANDATE_SCHEDULED"
        }

    def mutate_invoice(
        self,
        invoice_id: str,
        mutations: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "GROWW_JUPITER_FI",
            "invoice_id": invoice_id,
            "mutations_applied": mutations,
            "status": "NEOBANK_INVOICE_MUTATED",
            "revised_url": f"https://invest.groww.in/invoices/{invoice_id}"
        }
