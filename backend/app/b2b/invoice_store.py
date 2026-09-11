import time
import json
import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.security import get_db_connection

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
    Durable and Memory-Cached Repository for B2B Enterprise Invoices backed by SQLite WAL mode.
    Enforces Indian statutory GSTIN format validation under GST Rule 46.
    Allows field-level mutations (GSTIN, line items, amount, status)
    with sequential mutation audit logs and durable ACID persistence.
    """

    GSTIN_REGEX = re.compile(r"^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._invoices: Dict[str, InvoiceRecord] = {}
        self._init_db()

    def _get_conn(self):
        return get_db_connection(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS b2b_invoices (
                    invoice_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    amount REAL NOT NULL,
                    tax_amount REAL DEFAULT 0.0,
                    gstin TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    mutations_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_inv_status ON b2b_invoices (status)")

        # Load existing from DB or seed defaults
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM b2b_invoices")
        if cursor.fetchone()[0] == 0:
            self._seed_default_invoices()
        else:
            self._load_from_db()

    def _load_from_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invoice_id, customer_name, customer_email, customer_phone,
                   amount, tax_amount, gstin, status, due_date, items_json,
                   mutations_json, created_at, updated_at
            FROM b2b_invoices
        """)
        for r in cursor.fetchall():
            items = [InvoiceItem(**it) for it in json.loads(r[9])] if r[9] else []
            mutations = json.loads(r[10]) if r[10] else []
            inv = InvoiceRecord(
                invoice_id=r[0],
                customer_name=r[1],
                customer_email=r[2],
                customer_phone=r[3],
                amount=r[4],
                tax_amount=r[5],
                gstin=r[6],
                status=r[7],
                due_date=r[8],
                items=items,
                mutations=mutations,
                created_at=r[11],
                updated_at=r[12]
            )
            self._invoices[inv.invoice_id] = inv

    def _persist_invoice(self, inv: InvoiceRecord):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO b2b_invoices (
                    invoice_id, customer_name, customer_email, customer_phone,
                    amount, tax_amount, gstin, status, due_date, items_json,
                    mutations_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(invoice_id) DO UPDATE SET
                    customer_name = excluded.customer_name,
                    customer_email = excluded.customer_email,
                    customer_phone = excluded.customer_phone,
                    amount = excluded.amount,
                    tax_amount = excluded.tax_amount,
                    gstin = excluded.gstin,
                    status = excluded.status,
                    due_date = excluded.due_date,
                    items_json = excluded.items_json,
                    mutations_json = excluded.mutations_json,
                    updated_at = excluded.updated_at
            """, (
                inv.invoice_id,
                inv.customer_name,
                inv.customer_email,
                inv.customer_phone,
                inv.amount,
                inv.tax_amount,
                inv.gstin,
                inv.status,
                inv.due_date,
                json.dumps([it.model_dump() for it in inv.items]),
                json.dumps(inv.mutations),
                inv.created_at,
                inv.updated_at
            ))

    def _seed_default_invoices(self):
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
        self._persist_invoice(inv_998)

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
        self._persist_invoice(inv_992)

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
        self._persist_invoice(inv_987)

    @classmethod
    def validate_gstin_format(cls, gstin_str: str) -> bool:
        """
        Validates Indian statutory GSTIN format:
        15 characters: 2-digit state code (01-37 or 97) + 10-char PAN + 1 entity num + 'Z' + 1 checksum char.
        Returns True if valid or 'UNREGISTERED', False otherwise.
        """
        if not gstin_str or gstin_str.upper() == "UNREGISTERED":
            return True
        clean = gstin_str.strip().upper()
        if len(clean) != 15:
            return False
        # State code check (01 to 37, or 97)
        state_code = int(clean[:2]) if clean[:2].isdigit() else -1
        if not ((1 <= state_code <= 37) or state_code == 97):
            return False
        return bool(cls.GSTIN_REGEX.match(clean))

    def get_invoice(self, invoice_id: str) -> Optional[InvoiceRecord]:
        if invoice_id in self._invoices:
            return self._invoices[invoice_id]
        # Query DB
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invoice_id, customer_name, customer_email, customer_phone,
                   amount, tax_amount, gstin, status, due_date, items_json,
                   mutations_json, created_at, updated_at
            FROM b2b_invoices WHERE invoice_id = ?
        """, (invoice_id,))
        r = cursor.fetchone()
        if not r:
            return None
        items = [InvoiceItem(**it) for it in json.loads(r[9])] if r[9] else []
        mutations = json.loads(r[10]) if r[10] else []
        inv = InvoiceRecord(
            invoice_id=r[0], customer_name=r[1], customer_email=r[2], customer_phone=r[3],
            amount=r[4], tax_amount=r[5], gstin=r[6], status=r[7], due_date=r[8],
            items=items, mutations=mutations, created_at=r[11], updated_at=r[12]
        )
        self._invoices[invoice_id] = inv
        return inv

    def list_invoices(self) -> List[InvoiceRecord]:
        self._load_from_db()
        return list(self._invoices.values())

    def mutate_invoice_field(
        self,
        invoice_id: str,
        field: str,
        new_value: Any,
        reason: str = "Voice agent customer instruction",
        operator: str = "AI_AGENT"
    ) -> Optional[InvoiceRecord]:
        inv = self.get_invoice(invoice_id)
        if not inv:
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

        # Validate GSTIN if targeted
        if field == "gstin":
            val_str = str(new_value).strip().upper()
            if not self.validate_gstin_format(val_str):
                raise ValueError(f"Statutory Validation Failed: '{new_value}' is not a compliant 15-character Indian GSTIN format.")
            new_value = val_str

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
        self._persist_invoice(inv)
        logger.info(f"Mutated invoice {invoice_id}: {field} '{old_val}' -> '{new_value}' ({reason})")
        return inv

invoice_store = InvoiceStore()
