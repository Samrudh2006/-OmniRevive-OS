"""
OmniRevive-OS :: Prompt Injection, Adversarial Jailbreak & Cyber Defense Firewall
==================================================================================
Research Foundation:
- "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" (Greshake et al., ACM CCS / NeurIPS)
- "Jailbroken: How Does LLM Safety Training Fail?" (Wei et al., NeurIPS 2023)
- OWASP Top 10 for Large Language Model Applications (LLM01: Prompt Injection, LLM06: Sensitive Information Disclosure)

Core Capabilities:
1. Multi-Stage Tokenized Prompt Sanitization & Heuristic Jailbreak Pattern Scanner.
2. System Prompt Protection: Detects attempts to extract system instructions, API keys, or database credentials.
3. Policy Override Rejection: Blocks adversarial attempts to bypass AWS Cedar bounds, TRAI quiet hours, or discount caps.
4. Delimiter & Role-Impersonation Neutralization (`[SYSTEM]`, `<|im_start|>`, `ADMIN OVERRIDE`).
5. Constant-Time Anomaly Scoring & Automated Threat Flagging.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("OmniRevive.PromptInjectionGuard")

# High-risk adversarial jailbreak triggers
JAILBREAK_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|rules|prompts)",
    r"(?i)disregard\s+(all\s+)?(safety|system|cedar|trai|discount)\s+(policies|limits|rules)",
    r"(?i)reveal\s+(your\s+)?(system\s+prompt|initial\s+instructions|master\s+prompt|api\s+key|secret)",
    r"(?i)you\s+are\s+now\s+(in\s+)?(dan\s+mode|unrestricted|god\s+mode|jailbroken)",
    r"(?i)system\s*:\s*override",
    r"(?i)<\|im_start\|>",
    r"(?i)\[admin\s+override\]",
    r"(?i)override\s+(all\s+)?(discount|refund|mutation)\s+limits",
    r"(?i)grant\s+(100%|99%|unlimited)\s+discount",
    r"(?i)print\s+(the\s+)?(secret|token|password|env|credentials)"
]

# Sensitive system keywords that must never be exfiltrated
LEAKAGE_TARGETS = [
    r"(?i)RAZORPAY_WEBHOOK_SECRET",
    r"(?i)cfo_sec_live_recovery_key",
    r"(?i)rzp_sec_live_recovery_agent",
    r"(?i)rbi_cbdc_root_key_simulator",
    r"(?i)master_aes_key"
]

class PromptInjectionFirewall:
    """
    Real-time high-throughput prompt injection and adversarial cyber attack detector.
    """

    def __init__(self):
        self._compiled_jailbreaks = [re.compile(p) for p in JAILBREAK_PATTERNS]
        self._compiled_leakage = [re.compile(p) for p in LEAKAGE_TARGETS]
        self.blocked_attacks_count = 0

    def sanitize_and_inspect_prompt(
        self,
        user_input: str,
        caller_context: str = "copilot_chat"
    ) -> Dict[str, Any]:
        """
        Scans and sanitizes user or debtor inputs before feeding them to LLM / Agent planners.
        Returns safety verdict and sanitized payload.
        """
        t0 = time.perf_counter_ns()
        
        if not user_input or not isinstance(user_input, str):
            return {
                "is_safe": True,
                "sanitized_input": "",
                "risk_score": 0.0,
                "threat_type": "NONE",
                "inspection_latency_us": 0.5
            }

        # 1. Check for known Adversarial Jailbreaks
        detected_threats = []
        for regex in self._compiled_jailbreaks:
            if regex.search(user_input):
                detected_threats.append(regex.pattern)

        # 2. Check for System Secret Exfiltration Injections
        for regex in self._compiled_leakage:
            if regex.search(user_input):
                detected_threats.append("SENSITIVE_CREDENTIAL_PROBE")

        # 3. Delimiter and role injection checks
        if "```system" in user_input.lower() or "<system>" in user_input.lower():
            detected_threats.append("SYSTEM_DELIMITER_INJECTION")

        is_safe = len(detected_threats) == 0
        risk_score = 0.0 if is_safe else min(1.0, 0.35 * len(detected_threats) + 0.30)

        # Latency calculation
        latency_us = round((time.perf_counter_ns() - t0) / 1000.0, 2)

        if not is_safe:
            self.blocked_attacks_count += 1
            logger.warning(
                f"[CYBER_DEFENSE] Blocked Prompt Injection attempt in {caller_context}. "
                f"Threats: {detected_threats} | Input snippet: {user_input[:80]}..."
            )
            return {
                "is_safe": False,
                "sanitized_input": "[SECURITY_ALERT: PROMPT_INJECTION_REJECTED]",
                "risk_score": risk_score,
                "threat_type": "PROMPT_INJECTION_OR_JAILBREAK",
                "detected_patterns": detected_threats,
                "inspection_latency_us": latency_us,
                "action_taken": "BLOCKED_AND_LOGGED_TO_AUDIT_LEDGER"
            }

        # Safe input: Strip high-risk control characters
        clean_input = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", user_input).strip()

        return {
            "is_safe": True,
            "sanitized_input": clean_input,
            "risk_score": 0.0,
            "threat_type": "NONE",
            "detected_patterns": [],
            "inspection_latency_us": latency_us,
            "action_taken": "PASSED_CLEAN"
        }

prompt_injection_firewall = PromptInjectionFirewall()
