import time
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.schemas import CFOApprovalItem, CFOApprovalStatusType
from backend.app.security import get_db_connection
from backend.app.audit_store import audit_store
from aws.cedar.cedar_engine import get_cedar_engine

logger = logging.getLogger("RazorRevive.CFO.Service")

class CFOApprovalService:
    """
    Zero-Trust Executive Approval Gating Service for High-Value Payment Recovery & Invoices.
    Enforces the explicit state machine:
        REQUESTED -> PENDING_APPROVAL -> APPROVED -> EXECUTED
    or
        REQUESTED / PENDING_APPROVAL -> REJECTED

    Guarantees:
    1. Cryptographic SHA-256 Audit Trail integration.
    2. Formal AWS Cedar Zero-Trust policy evaluation.
    3. Replay attack and invalid state transition prevention.
    4. Durable SQLite WAL persistence.
    """

    VALID_TRANSITIONS: Dict[str, set[str]] = {
        "REQUESTED": {"PENDING_APPROVAL", "REJECTED"},
        "PENDING_APPROVAL": {"APPROVED", "REJECTED"},
        "APPROVED": {"EXECUTED", "REJECTED"},
        "EXECUTED": set(),  # Terminal state
        "REJECTED": set()   # Terminal state
    }

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._init_db()

    def _get_conn(self):
        return get_db_connection(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cfo_approval_queue (
                    approval_id TEXT PRIMARY KEY,
                    request_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    status TEXT NOT NULL,
                    requester TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    requested_at REAL NOT NULL,
                    decided_at REAL,
                    decided_by TEXT,
                    decision_notes TEXT,
                    cedar_policy_evaluated TEXT,
                    cedar_decision TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cfo_status ON cfo_approval_queue (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cfo_entity ON cfo_approval_queue (entity_id)")

            # Seed default high-value pending approval if empty for immediate demo capability
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cfo_approval_queue")
            if cursor.fetchone()[0] == 0:
                now = time.time()
                conn.execute("""
                    INSERT INTO cfo_approval_queue (
                        approval_id, request_type, entity_id, amount, currency, status,
                        requester, reason, requested_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "cfo_app_default_01",
                    "HIGH_VALUE_RECOVERY_ANOMALY",
                    "pay_ent_high_9921",
                    125000.0,
                    "INR",
                    "PENDING_APPROVAL",
                    "POLICY_ENGINE_GATE_3",
                    "Transaction amount INR 125,000 exceeds ₹50,000 high-value threshold with confidence 0.72 < 0.85.",
                    now - 1200
                ))
                conn.execute("""
                    INSERT INTO cfo_approval_queue (
                        approval_id, request_type, entity_id, amount, currency, status,
                        requester, reason, requested_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "cfo_app_default_02",
                    "B2B_INVOICE_TDS_MUTATION",
                    "inv_enterprise_998",
                    85000.0,
                    "INR",
                    "PENDING_APPROVAL",
                    "B2B_VOICE_AGENT",
                    "Proposed GSTIN & 10% TDS line item mutation for Acme Pvt Ltd under GST Rule 46.",
                    now - 600
                ))

    def create_request(
        self,
        entity_id: str,
        amount: float,
        reason: str,
        request_type: str = "HIGH_VALUE_RECOVERY_ANOMALY",
        requester: str = "POLICY_ENGINE_GATE_3"
    ) -> CFOApprovalItem:
        """Enters an operation into the CFO review queue in PENDING_APPROVAL state."""
        approval_id = f"cfo_{uuid.uuid4().hex[:10]}"
        now = time.time()

        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO cfo_approval_queue (
                    approval_id, request_type, entity_id, amount, currency, status,
                    requester, reason, requested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                approval_id, request_type, entity_id, amount, "INR", "PENDING_APPROVAL",
                requester, reason, now
            ))

        logger.info(f"[CFO_SERVICE] Created approval request {approval_id} for {entity_id} (INR {amount:,.2f})")
        return CFOApprovalItem(
            approval_id=approval_id,
            request_type=request_type,
            entity_id=entity_id,
            amount=amount,
            currency="INR",
            status="PENDING_APPROVAL",
            requester=requester,
            reason=reason,
            requested_at=now
        )

    def list_queue(self, status: Optional[str] = None, limit: int = 50) -> List[CFOApprovalItem]:
        """Lists pending or historical CFO approval records."""
        conn = self._get_conn()
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                SELECT approval_id, request_type, entity_id, amount, currency, status,
                       requester, reason, requested_at, decided_at, decided_by,
                       decision_notes, cedar_policy_evaluated, cedar_decision
                FROM cfo_approval_queue
                WHERE status = ?
                ORDER BY requested_at DESC LIMIT ?
            """, (status.upper(), limit))
        else:
            cursor.execute("""
                SELECT approval_id, request_type, entity_id, amount, currency, status,
                       requester, reason, requested_at, decided_at, decided_by,
                       decision_notes, cedar_policy_evaluated, cedar_decision
                FROM cfo_approval_queue
                ORDER BY requested_at DESC LIMIT ?
            """, (limit,))

        items = []
        for r in cursor.fetchall():
            items.append(CFOApprovalItem(
                approval_id=r[0],
                request_type=r[1],
                entity_id=r[2],
                amount=r[3],
                currency=r[4],
                status=r[5],
                requester=r[6],
                reason=r[7],
                requested_at=r[8],
                decided_at=r[9],
                decided_by=r[10],
                decision_notes=r[11],
                cedar_policy_evaluated=r[12],
                cedar_decision=r[13]
            ))
        return items

    def get_approval(self, approval_id: str) -> Optional[CFOApprovalItem]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT approval_id, request_type, entity_id, amount, currency, status,
                   requester, reason, requested_at, decided_at, decided_by,
                   decision_notes, cedar_policy_evaluated, cedar_decision
            FROM cfo_approval_queue WHERE approval_id = ?
        """, (approval_id,))
        r = cursor.fetchone()
        if not r:
            return None
        return CFOApprovalItem(
            approval_id=r[0],
            request_type=r[1],
            entity_id=r[2],
            amount=r[3],
            currency=r[4],
            status=r[5],
            requester=r[6],
            reason=r[7],
            requested_at=r[8],
            decided_at=r[9],
            decided_by=r[10],
            decision_notes=r[11],
            cedar_policy_evaluated=r[12],
            cedar_decision=r[13]
        )

    def process_decision(
        self,
        approval_id: str,
        action: str,  # "APPROVE" or "REJECT"
        actor: str = "Role::CFO",
        notes: str = "Authorized under CFO governance mandate",
        trace_id: str = "tr_cfo"
    ) -> CFOApprovalItem:
        """
        Executes the approval or rejection state transition.
        Enforces state validation, Cedar Zero-Trust check, and audit ledger persistence.
        """
        item = self.get_approval(approval_id)
        if not item:
            raise ValueError(f"Approval request {approval_id} not found.")

        target_status: CFOApprovalStatusType = "APPROVED" if action.upper() == "APPROVE" else "REJECTED"

        # Validate legal transition
        allowed = self.VALID_TRANSITIONS.get(item.status, set())
        if target_status not in allowed:
            raise ValueError(f"Invalid transition for {approval_id}: Cannot transition from {item.status} to {target_status}. Allowed: {allowed}")

        # Evaluate AWS Cedar Zero-Trust Authorization
        cedar_action = "Action::ApproveCFOEscalation" if action.upper() == "APPROVE" else "Action::RejectCFOEscalation"
        cedar_engine = get_cedar_engine()
        cedar_res = cedar_engine.evaluate(
            principal=actor,
            action=cedar_action,
            resource=f"CFOApproval::{approval_id}",
            context={"amount": int(item.amount), "request_type": item.request_type}
        )

        now = time.time()
        final_status = target_status
        if cedar_res.decision != "ALLOW" and action.upper() == "APPROVE":
            # If Cedar denies the executive approval action, block it
            raise PermissionError(f"Cedar Zero-Trust Policy DENY for {actor}: {cedar_res.diagnostics.get('reason', 'Unauthorized')}")

        conn = self._get_conn()
        with conn:
            conn.execute("""
                UPDATE cfo_approval_queue
                SET status = ?, decided_at = ?, decided_by = ?, decision_notes = ?,
                    cedar_policy_evaluated = ?, cedar_decision = ?
                WHERE approval_id = ?
            """, (
                final_status, now, actor, notes, cedar_res.policy_id, cedar_res.decision, approval_id
            ))

        # If approved, immediately transition into EXECUTED for end-to-end completion
        if final_status == "APPROVED":
            with conn:
                conn.execute("UPDATE cfo_approval_queue SET status = 'EXECUTED' WHERE approval_id = ?", (approval_id,))
            final_status = "EXECUTED"

        # Commit non-repudiable audit event to SHA-256 ledger
        audit_store.record_event(
            trace_id=trace_id,
            merchant_id="merchant_enterprise_cfo",
            payment_id=item.entity_id,
            event_type=f"cfo.approval.{action.lower()}",
            failure_class="HIGH_VALUE_GATING",
            decision={
                "approval_id": approval_id,
                "action": action,
                "amount": item.amount,
                "notes": notes,
                "cedar_decision": cedar_res.decision
            },
            policy_verdict="ALLOWED" if cedar_res.decision == "ALLOW" else "DENIED",
            action_taken=f"CFO_{final_status}",
            gateway_result={"approval_id": approval_id, "status": final_status, "decided_by": actor}
        )

        logger.info(f"[CFO_SERVICE] Processed {action} for {approval_id}: transitioned {item.status} -> {final_status}")
        return self.get_approval(approval_id) # type: ignore

cfo_service = CFOApprovalService()
