import time
import uuid
from typing import Dict, Any, List, Optional
from prometheus_client import Counter, Histogram
import structlog
import logging

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
s_logger = structlog.get_logger()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RazorRevive")

# Prometheus Metrics Definitions for Production SRE Telemetry
RECOVERY_REQUESTS_TOTAL = Counter(
    "razorrevive_recovery_requests_total",
    "Total count of revenue recovery requests processed",
    ["status", "failure_class"]
)
RECOVERED_GMV_INR = Counter(
    "razorrevive_recovered_gmv_inr_total",
    "Total Gross Merchandise Value recovered in INR"
)
DIAGNOSTIC_LATENCY_HISTOGRAM = Histogram(
    "razorrevive_diagnostic_latency_seconds",
    "End-to-end diagnostic and hazard window latency in seconds",
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)
IDEMPOTENCY_COLLISIONS_TOTAL = Counter(
    "razorrevive_idempotency_collisions_total",
    "Total count of concurrent duplicate attacks blocked by distributed mutex"
)

LIVE_LOGS_BUFFER: List[Dict[str, Any]] = []

def log_system_event(level: str, module: str, message: str, trace_id: str = "tr_system", details: Optional[Dict[str, Any]] = None):
    s_logger.info(message, module=module, trace_id=trace_id, details=details or {})
    now_ist = time.strftime("%d %b %Y, %I:%M:%S %p", time.gmtime(time.time() + 5.5 * 3600))
    entry = {
        "id": f"log_{uuid.uuid4().hex[:8]}",
        "timestamp": now_ist,
        "epoch": time.time(),
        "level": level.upper(),
        "module": module,
        "message": message,
        "trace_id": trace_id,
        "details": details or {}
    }
    LIVE_LOGS_BUFFER.insert(0, entry)
    if len(LIVE_LOGS_BUFFER) > 200:
        LIVE_LOGS_BUFFER.pop()

# Initialize baseline logs
log_system_event("INFO", "Bootstrap", "RazorRevive-OS Control Plane initialized in Sandbox/Test Mode.")
log_system_event("INFO", "Security", "HMAC SHA-256 Verifier & Distributed Idempotency Mutex active.")
log_system_event("INFO", "Policy", "TRAI Quiet Hours (21:00-09:00 IST) & Discount Clamping (<=10%, <=500 INR) active.")

LATEST_BENCHMARK_CACHE = {
    "total_transactions": 100,
    "at_risk_gmv": 542850.0,
    "recovered_gmv": 425600.0,
    "recovery_rate_pct": 78.39,
    "false_positive_cost_inr": 1240.0,
    "human_escalations": 8,
    "safety_suppressions": 10,
    "idempotency_violations": 0,
    "policy_violations": 0,
    "avg_decision_latency_sec": 1.23,
    "breakdown": {
        "bank_outage": {"label": "Bank Outage", "cases": 35, "percentage": 35, "color": "#2563eb"},
        "soft_declines": {"label": "Soft Declines", "cases": 25, "percentage": 25, "color": "#8b5cf6"},
        "expired_tokens": {"label": "Expired Tokens", "cases": 20, "percentage": 20, "color": "#f97316"},
        "drop_offs": {"label": "Drop-offs", "cases": 10, "percentage": 10, "color": "#06b6d4"},
        "fraud_spikes": {"label": "Fraud Spikes", "cases": 10, "percentage": 10, "color": "#ef4444"}
    }
}

ACTIVE_SECURITY_ALERTS = [
    {
        "id": "alt_01",
        "severity": "HIGH",
        "title": "Suspicious Velocity Spike Detected",
        "description": "5 rapid card declines within 60s from IP 192.168.1.104. Automated defense triggered: Outreach suppressed and rerouted to fraud team.",
        "timestamp": "10 minutes ago",
        "status": "CONTAINED",
        "action_taken": "SAFETY_SUPPRESSION"
    },
    {
        "id": "alt_02",
        "severity": "MEDIUM",
        "title": "HDFC Gateway Latency Spike (504)",
        "description": "Issuing bank HDFC node response time exceeded 4500ms. Recovery hazard model shifted retry windows to +45m peak.",
        "timestamp": "25 minutes ago",
        "status": "MONITORING",
        "action_taken": "HAZARD_PEAK_SHIFT"
    }
]
