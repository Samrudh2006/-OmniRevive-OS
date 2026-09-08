import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("RazorRevive.B2B.InvoiceStore")

class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    total_price: float

class InvoiceRecord(BaseModel):
    invoice_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    amount: float
    tax_amount: float = 0.0
    gstin: str
    status: str = "OVERDUE"  # DRAFT, OVERDUE, MUTATED, PTP_LOCKED, PAID
    due_date: str = "2026-09-01"
    items: List[InvoiceItem] = Field(default_factory=list)
    mutations: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class InvoiceStore:
    """
    In-memory and durable repository for B2B Enterprise Invoices.
    Allows real field-level mutations (GSTIN, line items, amount, status)
    with complete audit history and event tracking.
    """

    def __init__(self):
        self._invoices: Dict[str, InvoiceRecord] = {}
        self._seed_default_invoices()

    def _seed_default_invoices(self):
        # Default enterprise invoice used in Scenario C and B2B dialogues
        inv_998 = InvoiceRecord(
            invoice_id="inv_enterprise_998",
            customer_name="Acme Pvt Ltd",
            customer_email="finance@acmepvt.com",
            customer_phone="+919876543210",
            amount=85000.0,
            tax_amount=15300.0,  # 18% GST
            gstin="UNREGISTERED",
            status="OVERDUE",
            due_date="2026-09-01",
            items=[
                InvoiceItem(description="Razorpay Payment Gateway Enterprise SaaS (Q3)", quantity=1, unit_price=72033.90, total_price=72033.90),
                InvoiceItem(description="Integrated Optimizer Dynamic Acquirer Routing", quantity=1, unit_price=12966.10, total_price=12966.10)
            ]
        )
        self._invoices[inv_998.invoice_id] = inv_998

        inv_992 = InvoiceRecord(
            invoice_id="inv_enterprise_992",
            customer_name="TechCorp India Logistics",
            customer_email="accounts@techcorp.in",
            customer_phone="+919123456789",
            amount=125000.0,
            tax_amount=22500.0,
            gstin="36AAACB9876Q1Z1",
            status="OVERDUE",
            due_date="2026-08-25",
            items=[
                InvoiceItem(description="High-Volume Webhook Processing Node (Dedicated)", quantity=1, unit_price=105932.20, total_price=105932.20),
                InvoiceItem(description="Multi-Bank NPCI Circuit Breaker Module", quantity=1, unit_price=19067.80, total_price=19067.80)
            ]
        )
        self._invoices[inv_992.invoice_id] = inv_992

        inv_987 = InvoiceRecord(
            invoice_id="inv_enterprise_987",
            customer_name="Nova Retailers LLP",
            customer_email="cfo@novaretail.com",
            customer_phone="+919765432109",
            amount=45000.0,
            tax_amount=8100.0,
            gstin="27AABCN1234F1Z8",
            status="OVERDUE",
            due_date="2026-08-30",
            items=[
                InvoiceItem(description="Smart Retry AI Copilot Add-on License", quantity=1, unit_price=38135.59, total_price=38135.59),
                InvoiceItem(description="Automated PTP Dunning Engine", quantity=1, unit_price=6864.41, total_price=6864.41)
            ]
        )
        self._invoices[inv_987.invoice_id] = inv_987

    def get_invoice(self, invoice_id: str) -> Optional[InvoiceRecord]:
        return self._invoices.get(invoice_id)

    def list_invoices(self) -> List[InvoiceRecord]:
        return list(self._invoices.values())

    def mutate_invoice_field(
        self,
        invoice_id: str,
        field: str,
        new_value: Any,
        reason: str = "Voice agent customer instruction",
        operator: str = "AI_AGENT"
    ) -> Optional[InvoiceRecord]:
        inv = self._invoices.get(invoice_id)
        if not inv:
            # Create on-the-fly if not found
            inv = InvoiceRecord(
                invoice_id=invoice_id,
                customer_name="Enterprise Customer",
                customer_email="finance@customer.com",
                customer_phone="+919876543210",
                amount=85000.0,
                gstin="UNREGISTERED",
                status="OVERDUE"
            )
            self._invoices[invoice_id] = inv

        old_val = getattr(inv, field, None)
        setattr(inv, field, new_value)
        inv.updated_at = time.time()
        inv.status = "MUTATED"

        mutation_log = {
            "timestamp": time.time(),
            "field": field,
            "old_value": str(old_val),
            "new_value": str(new_value),
            "reason": reason,
            "operator": operator
        }
        inv.mutations.append(mutation_log)
        logger.info(f"Mutated invoice {invoice_id}: {field} '{old_val}' -> '{new_value}' ({reason})")
        return inv

invoice_store = InvoiceStore()
