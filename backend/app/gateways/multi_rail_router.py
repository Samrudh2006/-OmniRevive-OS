import logging
from typing import Dict, Any, Optional
from backend.app.gateways.base import PaymentGateway
from backend.app.gateways.razorpay_adapter import RazorpayTestAdapter
from backend.app.gateways.juspay_adapter import JuspayHyperSDKAdapter
from backend.app.gateways.phonepe_adapter import PhonePeSwitchAdapter
from backend.app.gateways.cred_adapter import CredPayAdapter
from backend.app.gateways.cashfree_adapter import CashfreeAdapter
from backend.app.gateways.neobank_adapter import NeobankMandateAdapter
from backend.app.gateways.stripe_adapter import StripeAdapter

logger = logging.getLogger("OmniRevive.Gateway.MultiRailRouter")

class MultiRailRouter(PaymentGateway):
    """
    Universal Multi-Rail Gateway Orchestrator.
    Routes revenue recovery intents across India's premier fintech rails:
    Juspay, PhonePe, CRED, Cashfree, Groww/Jupiter Neobanks, Stripe, and Razorpay.
    """

    def __init__(self, default_mode: str = "universal_auto"):
        self.active_rail: str = default_mode  # 'universal_auto' or specific rail id
        self.adapters: Dict[str, PaymentGateway] = {
            "razorpay": RazorpayTestAdapter(),
            "juspay": JuspayHyperSDKAdapter(),
            "phonepe": PhonePeSwitchAdapter(),
            "cred": CredPayAdapter(),
            "cashfree": CashfreeAdapter(),
            "neobank": NeobankMandateAdapter(),
            "stripe": StripeAdapter()
        }

    def set_active_rail(self, rail_name: str) -> bool:
        normalized = rail_name.lower().strip()
        if normalized == "universal_auto" or normalized in self.adapters:
            self.active_rail = normalized
            logger.info(f"[MULTI_RAIL_ROUTER] Switched active recovery rail to: {self.active_rail.upper()}")
            return True
        return False

    def select_optimal_adapter(
        self,
        amount: float = 0.0,
        customer_email: str = "",
        customer_phone: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentGateway:
        """
        Omnitrix Adaptive Signal Routing:
        Selects the optimal gateway adapter based on transaction context.
        """
        if self.active_rail != "universal_auto" and self.active_rail in self.adapters:
            return self.adapters[self.active_rail]

        meta = metadata or {}
        # 1. International customer (foreign phone, .io/.global domain, or USD/EUR currency) -> Stripe Multi-Currency
        if (
            customer_phone.startswith(("+1", "+44", "+65", "+971")) or 
            customer_email.endswith((".io", ".global", ".co.uk", ".us")) or 
            meta.get("currency", "INR") not in ["INR", "₹"]
        ):
            return self.adapters["stripe"]

        # 2. Ultra High-Ticket (>₹50,000) -> CRED Pay (Guaranteed CAS Mutex & 0 Double Debits)
        if amount >= 50000:
            return self.adapters["cred"]

        # 3. Recurring SIP / Mandate -> Neobank Salary-Cycle Scheduler (Groww / Jupiter)
        if meta.get("is_mandate") or meta.get("payment_type") == "recurring_sip":
            return self.adapters["neobank"]

        # 4. Bank Outage / High-Latency Switch -> PhonePe or Juspay Switch
        if meta.get("outage_detected") or "504" in str(meta.get("error_code", "")):
            return self.adapters["phonepe"]

        # 5. Default high-volume B2C -> Juspay HyperSDK
        return self.adapters["juspay"]

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
        adapter = self.select_optimal_adapter(
            amount=amount,
            customer_email=customer_email,
            customer_phone=customer_phone
        )
        result = adapter.create_recovery_link(
            payment_id=payment_id,
            amount=amount,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            discount_amount=discount_amount,
            expire_by_minutes=expire_by_minutes
        )
        result["routed_via_rail"] = self.active_rail
        return result

    def schedule_mandate_retry(
        self,
        mandate_id: str,
        amount: float,
        scheduled_epoch: float,
        attempt_count: int = 1
    ) -> Dict[str, Any]:
        # For mandates, default to Neobank or Cashfree
        adapter = self.adapters["neobank"] if self.active_rail == "universal_auto" else self.select_optimal_adapter(amount=amount)
        result = adapter.schedule_mandate_retry(
            mandate_id=mandate_id,
            amount=amount,
            scheduled_epoch=scheduled_epoch,
            attempt_count=attempt_count
        )
        result["routed_via_rail"] = self.active_rail
        return result

    def mutate_invoice(
        self,
        invoice_id: str,
        mutations: Dict[str, Any]
    ) -> Dict[str, Any]:
        adapter = self.select_optimal_adapter()
        result = adapter.mutate_invoice(invoice_id=invoice_id, mutations=mutations)
        result["routed_via_rail"] = self.active_rail
        return result

    def get_supported_rails_meta(self) -> Dict[str, Any]:
        """Returns metadata and live capabilities for all supported fintech rails."""
        return {
            "active_rail": self.active_rail,
            "total_supported_rails": len(self.adapters),
            "rails": [
                {
                    "id": "universal_auto",
                    "name": "Omnitrix Auto-Switch",
                    "tagline": "Context-Aware Dynamic Rail Selection",
                    "tier": "Tier-1 Autonomous",
                    "stipend_bracket": "₹75,000 – ₹1,20,000/mo",
                    "core_feature": "Dynamic switch routing based on ticket size, bank health & customer channel",
                    "status": "ONLINE"
                },
                {
                    "id": "juspay",
                    "name": "Juspay HyperSDK",
                    "tagline": "India's Low-Latency Payments Switch",
                    "tier": "Payment Infrastructure",
                    "stipend_bracket": "₹40,000 – ₹60,000/mo",
                    "core_feature": "Switch Uptime Telemetry, Express Checkout & Multi-Bank Routing (HDFC/SBI/ICICI/Axis)",
                    "status": "ONLINE"
                },
                {
                    "id": "phonepe",
                    "name": "PhonePe Switch",
                    "tagline": "India's Largest UPI Switch (48% Market Share)",
                    "tier": "Tier-1 Heavyweight",
                    "stipend_bracket": "₹70,000 – ₹1,00,000/mo",
                    "core_feature": "PhonePe UPI Intent, QR Pay & Automatic Switch Failover on SBI 504 Outages",
                    "status": "ONLINE"
                },
                {
                    "id": "cred",
                    "name": "CRED Pay",
                    "tagline": "High-Ticket Bill Payments & Member Settlement",
                    "tier": "Tier-1 Heavyweight",
                    "stipend_bracket": "₹75,000 – ₹1,00,000/mo",
                    "core_feature": "Atomic CAS Mutex (0 Double-Debits), P2P Credit Recovery & Discount Clamping (<₹500)",
                    "status": "ONLINE"
                },
                {
                    "id": "cashfree",
                    "name": "Cashfree Payments",
                    "tagline": "B2B Auto-Collect & Direct Razorpay Competitor",
                    "tier": "Direct Peer Gateway",
                    "stipend_bracket": "₹40,000 – ₹60,000/mo",
                    "core_feature": "Auto-Collect Virtual Account Numbers (VAN) & Subscription e-Mandates",
                    "status": "ONLINE"
                },
                {
                    "id": "neobank",
                    "name": "Groww / Jupiter / Fi",
                    "tagline": "Neobanks & Wealthtech AutoPay Recovery",
                    "tier": "Wealthtech & Neobanking",
                    "stipend_bracket": "₹50,000 – ₹80,000/mo",
                    "core_feature": "Salary-Cycle Heuristic Scheduling (retries targeted at 1st-5th of month salary surplus)",
                    "status": "ONLINE"
                },
                {
                    "id": "stripe",
                    "name": "Stripe Multi-Currency",
                    "tagline": "Global Cross-Border SaaS & Export Rails",
                    "tier": "Tier-1 Global",
                    "stipend_bracket": "₹1,00,000 – ₹1,50,000+/mo",
                    "core_feature": "Multi-Currency USD/INR FX Conversion & Stripe Smart Retries Engine",
                    "status": "ONLINE"
                },
                {
                    "id": "razorpay",
                    "name": "Razorpay Standard",
                    "tagline": "Standard Indian Gateway Rail",
                    "tier": "Gateway Rail",
                    "stipend_bracket": "₹50,000 – ₹80,000/mo",
                    "core_feature": "Payment Links API & Recurring Subscriptions",
                    "status": "ONLINE"
                }
            ]
        }
