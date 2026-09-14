from backend.app.gateways.base import PaymentGateway
from backend.app.gateways.razorpay_adapter import RazorpayTestAdapter
from backend.app.gateways.mock_adapter import MockPaymentGateway
from backend.app.gateways.juspay_adapter import JuspayHyperSDKAdapter
from backend.app.gateways.phonepe_adapter import PhonePeSwitchAdapter
from backend.app.gateways.cred_adapter import CredPayAdapter
from backend.app.gateways.cashfree_adapter import CashfreeAdapter
from backend.app.gateways.neobank_adapter import NeobankMandateAdapter
from backend.app.gateways.stripe_adapter import StripeAdapter
from backend.app.gateways.multi_rail_router import MultiRailRouter

# Instantiate the Universal Multi-Rail Gateway Orchestrator
multi_rail_router = MultiRailRouter(default_mode="universal_auto")

# Default system adapter points to the universal multi-rail orchestrator
default_gateway: PaymentGateway = multi_rail_router
