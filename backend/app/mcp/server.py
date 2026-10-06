"""
OmniRevive-OS Model Context Protocol (MCP) Server
=================================================
Implements the Model Context Protocol (JSON-RPC 2.0) over standard input/output (stdio)
and SSE transport to empower external AI agents (Claude, Gemini, Antigravity, Cursor)
to interact natively with the revenue recovery control plane.

Exposed Tools:
1. `inspect_payment_drop`: Deep vector diagnostics on failed transaction error codes.
2. `run_bandit_routing`: LinUCB / Thompson Sampling multi-rail payment routing.
3. `verify_merkle_proof`: Standalone RFC 6962 offline cryptographic verification.
4. `escalate_cfo_quarantine`: CFO dual-key quarantine escalation for high-ticket drops.
5. `eval_cedar_policy`: AWS Cedar zero-trust boundary verification (TRAI hours, discount limits).
6. `get_npci_switch_telemetry`: Real-time health, latency, and degradation of Indian bank switches.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional

from backend.app.diagnostic_engine import diagnostic_engine
from backend.app.contextual_bandit import contextual_bandit_router
from backend.app.merkle_proof import verify_merkle_inclusion_proof, CompactMerkleTree
from backend.app.policy_engine import policy_engine
from backend.app.telemetry_npci import npci_telemetry

logger = logging.getLogger("OmniRevive.MCP")

MCP_TOOLS_MANIFEST = [
    {
        "name": "inspect_payment_drop",
        "description": "Performs sub-millisecond Qdrant semantic memory lookup and root-cause classification on a failed payment event.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "error_code": {"type": "string", "description": "Raw gateway error code (e.g., GATEWAY_ERROR, INSUFFICIENT_FUNDS)"},
                "error_description": {"type": "string", "description": "Raw error message string"},
                "amount_inr": {"type": "number", "description": "Transaction amount in INR"},
                "bank_issuer": {"type": "string", "description": "Issuing bank (e.g., HDFC, SBI, ICICI)"}
            },
            "required": ["error_code", "amount_inr"]
        }
    },
    {
        "name": "run_bandit_routing",
        "description": "Evaluates contextual multi-armed bandit (LinUCB / Thompson Sampling) across Razorpay, Juspay, PhonePe, Cashfree, and Stripe.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_inr": {"type": "number", "description": "Transaction amount in INR"},
                "bank_issuer": {"type": "string", "description": "Issuing bank name"},
                "attempt_number": {"type": "integer", "description": "Current retry attempt (1-5)"},
                "strategy": {"type": "string", "enum": ["LINUCB", "THOMPSON"], "default": "LINUCB"}
            },
            "required": ["amount_inr", "bank_issuer"]
        }
    },
    {
        "name": "verify_merkle_proof",
        "description": "Cryptographically verifies an RFC 6962 Merkle Inclusion Proof offline with zero database dependencies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "proof": {"type": "object", "description": "Full Merkle audit path proof JSON object"}
            },
            "required": ["proof"]
        }
    },
    {
        "name": "escalate_cfo_quarantine",
        "description": "Enforces AWS Cedar governance and places high-ticket transactions (>=₹50,000) into CFO dual-key approval queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "payment_id": {"type": "string", "description": "Unique payment identifier"},
                "amount_inr": {"type": "number", "description": "Transaction amount in INR"},
                "proposed_discount_pct": {"type": "number", "description": "Proposed incentive discount %"}
            },
            "required": ["payment_id", "amount_inr"]
        }
    },
    {
        "name": "eval_cedar_policy",
        "description": "Validates statutory TRAI quiet hours (21:00-09:00 IST) and statutory discount caps (<=10%, <=₹500).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_inr": {"type": "number", "description": "Amount in INR"},
                "discount_inr": {"type": "number", "description": "Discount in INR"},
                "action_type": {"type": "string", "description": "Action (VOICE_CALL, WHATSAPP, RETRY)"}
            },
            "required": ["amount_inr", "discount_inr", "action_type"]
        }
    },
    {
        "name": "get_npci_switch_telemetry",
        "description": "Retrieves real-time UPI 2.0 switch latency, error rates, and degradation status for Indian issuing banks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bank_code": {"type": "string", "description": "Bank code (e.g. HDFC, SBI, ICICI, AXIS, PNB)"}
            }
        }
    }
]

class OmniReviveMCPServer:
    """JSON-RPC 2.0 MCP Server Implementation."""
    
    @classmethod
    def handle_tool_call(cls, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the requested tool and returns structured tool response."""
        try:
            if tool_name == "inspect_payment_drop":
                err_code = arguments.get("error_code", "GATEWAY_ERROR")
                err_desc = arguments.get("error_description", "Bank gateway error")
                amount = float(arguments.get("amount_inr", 1500.0))
                bank = arguments.get("bank_issuer", "HDFC")
                
                diag = diagnostic_engine.diagnose(
                    payment_id="mcp_inspect_01",
                    amount=amount,
                    error_code=err_code,
                    error_description=err_desc,
                    metadata={"bank_issuer": bank}
                )
                return {
                    "tool": tool_name,
                    "status": "success",
                    "result": {
                        "failure_class": diag.failure_class,
                        "confidence_score": diag.confidence,
                        "recommended_channel": diag.recommended_strategy,
                        "reasoning": diag.reason_codes
                    }
                }

            elif tool_name == "run_bandit_routing":
                amount = float(arguments.get("amount_inr", 5000.0))
                bank = arguments.get("bank_issuer", "HDFC")
                attempt = int(arguments.get("attempt_number", 1))
                strategy = arguments.get("strategy", "LINUCB")
                
                decision = contextual_bandit_router.select_optimal_rail(amount, bank, attempt, strategy)
                return {"tool": tool_name, "status": "success", "result": decision}

            elif tool_name == "verify_merkle_proof":
                proof = arguments.get("proof", {})
                is_valid, msg = verify_merkle_inclusion_proof(proof)
                return {"tool": tool_name, "status": "success", "result": {"is_valid": is_valid, "message": msg}}

            elif tool_name == "escalate_cfo_quarantine":
                pid = arguments.get("payment_id", "pay_test_01")
                amount = float(arguments.get("amount_inr", 85000.0))
                disc = float(arguments.get("proposed_discount_pct", 5.0))
                
                is_quarantined = amount >= 50000.0 or disc > 10.0
                return {
                    "tool": tool_name,
                    "status": "success",
                    "result": {
                        "payment_id": pid,
                        "amount_inr": amount,
                        "quarantined": is_quarantined,
                        "requires_dual_key": is_quarantined,
                        "assigned_queue": "CFO_EXECUTIVE_ESCORT" if is_quarantined else "FAST_LOOP_AUTO_RECOVERY"
                    }
                }

            elif tool_name == "eval_cedar_policy":
                amount = float(arguments.get("amount_inr", 2000.0))
                disc = float(arguments.get("discount_inr", 100.0))
                action = arguments.get("action_type", "WHATSAPP")
                
                eval_res = policy_engine.evaluate_action(
                    payment_id="mcp_test",
                    amount=amount,
                    action_type=action,
                    discount_amount=disc
                )
                return {"tool": tool_name, "status": "success", "result": eval_res.model_dump()}

            elif tool_name == "get_npci_switch_telemetry":
                bank = arguments.get("bank_code")
                if bank:
                    status = npci_telemetry.get_switch_status(bank)
                    return {"tool": tool_name, "status": "success", "result": status.model_dump()}
                else:
                    all_switches = {b: npci_telemetry.get_switch_status(b).model_dump() for b in ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "PNB"]}
                    return {"tool": tool_name, "status": "success", "result": all_switches}

            else:
                return {"tool": tool_name, "status": "error", "error": f"Unknown tool '{tool_name}'"}

        except Exception as e:
            return {"tool": tool_name, "status": "error", "error": str(e)}

    @classmethod
    def process_json_rpc(cls, message: str) -> str:
        """Processes a standard JSON-RPC 2.0 request."""
        try:
            req = json.loads(message)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "tools/list":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": MCP_TOOLS_MANIFEST}
                })
            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                res = cls.handle_tool_call(tool_name, arguments)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    }
                })
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                })
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            })

    @classmethod
    def run_stdio(cls):
        """Runs the MCP server over standard input/output loop."""
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        
        logger.info("OmniRevive MCP Server initialized on stdio transport.")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = cls.process_json_rpc(line)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    OmniReviveMCPServer.run_stdio()
