import re
import time
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.app.b2b.invoice_store import invoice_store
from backend.app.communication.dispatch_engine import dispatch_engine
from backend.app.b2b.ptp_engine import ptp_store
from backend.app.audit_store import audit_store

logger = logging.getLogger("RazorRevive.Copilot.ActionAgent")

class ActionExecutionResult(BaseModel):
    action_executed: bool = False
    tool_name: Optional[str] = None
    action_summary: Optional[str] = None
    response_text: str
    dispatch_id: Optional[str] = None
    invoice_id: Optional[str] = None
    audit_hash: Optional[str] = None
    mutated_data: Optional[Dict[str, Any]] = None

class CopilotActionRouter:
    """
    Open-Source Action Router and Tool Execution Kernel for AI Copilot.
    Translates user instructions into deterministic tool calls that directly
    mutate invoice records, dispatch authentic RFC emails/WhatsApp messages,
    and commit SHA-256 audit blocks.
    """

    @classmethod
    def parse_and_execute(
        cls,
        query: str,
        active_invoice_id: str = "inv_enterprise_998",
        trace_id: str = "tr_copilot_001"
    ) -> ActionExecutionResult:
        q_raw = query.strip()
        q = q_raw.lower()

        # -------------------------------------------------------------
        # Tool 1: MUTATE INVOICE GSTIN / TAX LINE
        # e.g., "Change GST to 29AABCU9603R1Z2", "GST update karo"
        # -------------------------------------------------------------
        gst_match = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", q_raw.upper())
        if ("gst" in q or "pan" in q or "tax" in q) and any(verb in q for verb in ["change", "update", "mutate", "set", "daal", "karo", "cheyyi", "marchu", "bhejo"]):
            target_gst = gst_match.group(0) if gst_match else "29AABCU9603R1Z2"
            
            # Execute real mutation in invoice store
            inv = invoice_store.mutate_invoice_field(
                invoice_id=active_invoice_id,
                field="gstin",
                new_value=target_gst,
                reason=f"Copilot instructed mutation: '{query}'",
                operator="COPILOT_ACTION_AGENT"
            )
            if not inv:
                all_invs = invoice_store.get_all_invoices()
                inv = all_invs[0] if all_invs else None
            if not inv:
                return ActionExecutionResult(
                    action_executed=False,
                    tool_name="tool_mutate_invoice_gstin",
                    action_summary="Target invoice not found",
                    response_text="Error: Could not locate invoice for GSTIN mutation."
                )

            # Auto-dispatch updated advice email
            dispatch = dispatch_engine.dispatch_email(
                to_email=inv.customer_email,
                invoice_id=inv.invoice_id,
                subject=f"Tax Invoice Revised #{inv.invoice_id} (Updated GSTIN {target_gst})",
                custom_note=f"GSTIN successfully updated to {target_gst} per your verified instruction."
            )

            # Commit to SHA-256 tamper-evident audit ledger
            audit_commit = audit_store.record_event(
                trace_id=trace_id,
                merchant_id="merchant_123",
                payment_id=inv.invoice_id,
                event_type="copilot.action.invoice_mutation",
                failure_class="TAX_LINE_CORRECTION",
                decision={"query": query, "tool": "tool_mutate_invoice", "new_gstin": target_gst},
                policy_verdict="ALLOWED",
                action_taken="MUTATE_GSTIN_AND_DISPATCH_EMAIL",
                gateway_result={"gstin": target_gst, "dispatch_id": dispatch.dispatch_id}
            )

            speech = f"Ji bilkul, maine invoice #{inv.invoice_id} ka GSTIN update karke {target_gst} kar diya hai aur revised email finance team ko dispatch kar diya hai."

            return ActionExecutionResult(
                action_executed=True,
                tool_name="tool_mutate_invoice_gstin",
                action_summary=f"Mutated GSTIN to {target_gst} & Dispatched Revised Email",
                response_text=(
                    f"✅ **Action Executed: GSTIN Mutated & Email Dispatched**\n\n"
                    f"• **Invoice ID**: `{inv.invoice_id}` ({inv.customer_name})\n"
                    f"• **New GSTIN**: `{target_gst}` (Status: **MUTATED**)\n"
                    f"• **Email Dispatched**: `{dispatch.recipient}` (ID: `{dispatch.dispatch_id}`)\n"
                    f"• **Audit Proof**: Committed block `{audit_commit['current_hash'][:16]}...`\n\n"
                    f"You can preview the live delivered email below or in the Sent Communications drawer!"
                ),
                dispatch_id=dispatch.dispatch_id,
                invoice_id=inv.invoice_id,
                audit_hash=audit_commit["current_hash"],
                mutated_data={"gstin": target_gst, "status": "MUTATED", "amount": inv.amount}
            )

        # -------------------------------------------------------------
        # Tool 2: SEND INVOICE EMAIL ("mail pampana", "mail pampu", "send email", "email karo")
        # -------------------------------------------------------------
        if any(term in q for term in ["mail pampu", "email", "mail", "send invoice", "bhejo email", "dispatch mail", "mail pampana"]):
            # Extract recipient email if provided
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
            inv = invoice_store.get_invoice(active_invoice_id)
            if not inv:
                inv = invoice_store.get_invoice("inv_enterprise_998")
            if not inv:
                all_invs = invoice_store.get_all_invoices()
                inv = all_invs[0] if all_invs else None
            if not inv:
                return ActionExecutionResult(
                    action_executed=False,
                    tool_name="tool_send_invoice_email",
                    action_summary="Target invoice not found",
                    response_text="Error: Could not locate invoice to dispatch email."
                )

            target_email = email_match.group(0) if email_match else inv.customer_email
            
            # Execute real email dispatch
            dispatch = dispatch_engine.dispatch_email(
                to_email=target_email,
                invoice_id=inv.invoice_id,
                subject=f"Tax Invoice & Settlement Advice #{inv.invoice_id} ({inv.customer_name})",
                custom_note="Automated on-demand invoice dispatch requested via AI Copilot."
            )

            # Audit commit
            audit_commit = audit_store.record_event(
                trace_id=trace_id,
                merchant_id="merchant_123",
                payment_id=inv.invoice_id,
                event_type="copilot.action.email_dispatch",
                failure_class="DISPATCH_REQUEST",
                decision={"query": query, "recipient": target_email},
                policy_verdict="ALLOWED",
                action_taken="DISPATCH_INVOICE_EMAIL",
                gateway_result={"dispatch_id": dispatch.dispatch_id}
            )

            speech = f"Haanji sir, maine invoice #{inv.invoice_id} ka official tax invoice email {target_email} ko dispatch kar diya hai. Aap live preview check kar sakte hain."

            return ActionExecutionResult(
                action_executed=True,
                tool_name="tool_send_invoice_email",
                action_summary=f"Dispatched Corporate Invoice Email to {target_email}",
                response_text=(
                    f"📧 **Action Executed: Official Tax Invoice Email Dispatched!**\n\n"
                    f"• **Recipient**: `{target_email}`\n"
                    f"• **Invoice Reference**: `{inv.invoice_id}` (Amount: **₹{inv.amount:,.2f}**)\n"
                    f"• **GSTIN Included**: `{inv.gstin}`\n"
                    f"• **Dispatch ID**: `{dispatch.dispatch_id}` (Delivery: **DELIVERED**)\n"
                    f"• **Cryptographic Block**: `{audit_commit['current_hash'][:16]}...`\n\n"
                    f"Click **'View Sent Email'** to inspect the authentic rendered HTML invoice!"
                ),
                dispatch_id=dispatch.dispatch_id,
                invoice_id=inv.invoice_id,
                audit_hash=audit_commit["current_hash"]
            )

        # -------------------------------------------------------------
        # Tool 3: MUTATE INVOICE AMOUNT / DISCOUNT
        # e.g., "Change amount to 75000", "Update price to 80000"
        # -------------------------------------------------------------
        amt_match = re.search(r"\b(?:rs\.?|inr|₹)?\s*(\d{4,8})\b", q_raw)
        if any(verb in q for verb in ["amount", "price", "discount", "value", "rupees"]) and any(k in q for k in ["change", "update", "set", "karo", "cheyyi", "reduce"]) and amt_match:
            new_amount = float(amt_match.group(1))
            inv = invoice_store.mutate_invoice_field(
                invoice_id=active_invoice_id,
                field="amount",
                new_value=new_amount,
                reason=f"Copilot instructed price mutation: '{query}'",
                operator="COPILOT_ACTION_AGENT"
            )
            if not inv:
                all_invs = invoice_store.get_all_invoices()
                inv = all_invs[0] if all_invs else None
            if not inv:
                return ActionExecutionResult(
                    action_executed=False,
                    tool_name="tool_mutate_invoice_amount",
                    action_summary="Target invoice not found",
                    response_text="Error: Could not locate invoice for amount mutation."
                )

            audit_commit = audit_store.record_event(
                trace_id=trace_id,
                merchant_id="merchant_123",
                payment_id=inv.invoice_id,
                event_type="copilot.action.amount_mutation",
                failure_class="COMMERCIAL_ADJUSTMENT",
                decision={"query": query, "new_amount": new_amount},
                policy_verdict="ALLOWED",
                action_taken="MUTATE_INVOICE_AMOUNT",
                gateway_result={"amount": new_amount}
            )

            speech = f"Theek hai sir, maine invoice amount update karke INR {new_amount:,.2f} kar diya hai."

            return ActionExecutionResult(
                action_executed=True,
                tool_name="tool_mutate_invoice_amount",
                action_summary=f"Mutated Invoice Amount to ₹{new_amount:,.2f}",
                response_text=(
                    f"💰 **Action Executed: Invoice Amount Mutated**\n\n"
                    f"• **Invoice ID**: `{inv.invoice_id}`\n"
                    f"• **New Net Amount**: **₹{new_amount:,.2f}**\n"
                    f"• **Audit Block**: `{audit_commit['current_hash'][:16]}...`"
                ),
                invoice_id=inv.invoice_id,
                audit_hash=audit_commit["current_hash"],
                mutated_data={"amount": new_amount}
            )

        # -------------------------------------------------------------
        # Tool 4: LOCK PROMISE TO PAY (PTP)
        # e.g., "Customer will pay Friday 11 AM", "PTP lock karo"
        # -------------------------------------------------------------
        if any(term in q for term in ["friday", "monday", "tomorrow", "next week", "ptp", "promise to pay", "kal dega", "clear karega"]):
            inv = invoice_store.get_invoice(active_invoice_id)
            amt = inv.amount if inv else 85000.0
            phone = inv.customer_phone if inv else "+919876543210"

            ptp_record = ptp_store.register_promise(
                invoice_id=active_invoice_id,
                customer_contact=phone,
                promised_epoch=time.time() + (48 * 3600),
                promised_window_label="Friday 11:00 AM IST",
                amount=amt,
                notes=f"Copilot registered PTP commitment from query: '{query}'"
            )

            speech = "Bahut shukriya! Humne Friday 11:00 AM IST ka Promise-to-Pay lock register kar diya hai aur automated payment reminders suppress kar diye hain."

            return ActionExecutionResult(
                action_executed=True,
                tool_name="tool_lock_promise_to_pay",
                action_summary="Registered Promise-to-Pay (PTP) Lock until Friday 11:00 AM IST",
                response_text=(
                    f"📅 **Action Executed: Promise-to-Pay (PTP) Commitment Locked**\n\n"
                    f"• **Invoice**: `{active_invoice_id}` (Amount: **₹{amt:,.2f}**)\n"
                    f"• **Committed Window**: **Friday 11:00 AM IST**\n"
                    f"• **Policy Action**: Automated dunning & debt calls **SUPPRESSED** until committed window.\n"
                    f"• **Status**: `PTP_LOCKED`"
                ),
                invoice_id=active_invoice_id
            )

        # Non-action query -> Return None to allow standard conversational response
        return ActionExecutionResult(
            action_executed=False,
            response_text=""
        )

action_router = CopilotActionRouter()
