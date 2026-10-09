"""
OmniRevive-OS Bank Health Pulse Monitor
======================================
Real-time synthetic probing and NPCI/Core Banking switch health telemetry.
Maintains exponential moving averages (EMA) of bank latency, timeout rates,
and degradation scores (0.0=Optimal to 1.0=Severe Outage).
Directly updates contextual bandit covariates for proactive traffic deflection.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("OmniRevive.BankHealthPulse")

SUPPORTED_BANKS = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "PNB", "BOB", "UPI_NPCI"]

def np_clip_score(val: float) -> float:
    return max(0.0, min(1.0, val))

class BankHealthPulseSensor:
    """
    Simulates / ingests high-frequency banking rail telemetry.
    Calculates dynamic degradation indices using EWMA (Exponential Weighted Moving Average).
    """
    def __init__(self, decay_factor: float = 0.85):
        self.decay_factor = decay_factor
        self.bank_metrics: Dict[str, Dict[str, Any]] = {}
        self._init_defaults()

    def _init_defaults(self):
        for bank in SUPPORTED_BANKS:
            self.bank_metrics[bank] = {
                "bank": bank,
                "latency_p95_ms": 120.0,
                "error_rate": 0.015,
                "timeout_count_last_5min": 0,
                "degradation_score": 0.05,
                "health_status": "HEALTHY",
                "last_probed_at": time.time(),
                "recommended_switch_action": "NORMAL_ROUTING"
            }

    def record_bank_telemetry(
        self,
        bank: str,
        latency_ms: float,
        is_error: bool,
        is_timeout: bool = False
    ) -> Dict[str, Any]:
        """
        Ingests real-time transaction observation or synthetic probe result.
        Updates EWMA latency, error rate, and overall degradation score.
        """
        bank_upper = bank.upper() if bank.upper() in self.bank_metrics else "UPI_NPCI"
        current = self.bank_metrics[bank_upper]

        # EWMA updates
        alpha = 1.0 - self.decay_factor
        new_latency = (self.decay_factor * current["latency_p95_ms"]) + (alpha * latency_ms)
        error_val = 1.0 if is_error else 0.0
        new_err_rate = (self.decay_factor * current["error_rate"]) + (alpha * error_val)
        
        timeout_delta = 1 if is_timeout else 0
        timeout_count = current["timeout_count_last_5min"] + timeout_delta

        # Compute combined degradation score [0.0, 1.0]
        latency_penalty = min(1.0, max(0.0, (new_latency - 100.0) / 900.0))
        degradation = round(float(np_clip_score((0.4 * latency_penalty) + (0.6 * new_err_rate))), 4)

        if degradation >= 0.70 or is_timeout:
            status = "CRITICAL_OUTAGE"
            action = "EMERGENCY_REROUTE_MANDATORY"
        elif degradation >= 0.35:
            status = "DEGRADED"
            action = "THROTTLE_AND_SOFT_FAILOVER"
        else:
            status = "HEALTHY"
            action = "NORMAL_ROUTING"

        updated = {
            "bank": bank_upper,
            "latency_p95_ms": round(new_latency, 2),
            "error_rate": round(new_err_rate, 4),
            "timeout_count_last_5min": timeout_count,
            "degradation_score": degradation,
            "health_status": status,
            "last_probed_at": time.time(),
            "recommended_switch_action": action
        }
        self.bank_metrics[bank_upper] = updated
        return updated

    def get_bank_degradation(self, bank: str) -> float:
        """Returns the current degradation score (0.0 to 1.0) for a bank."""
        bank_upper = bank.upper() if bank.upper() in self.bank_metrics else "UPI_NPCI"
        return self.bank_metrics.get(bank_upper, {}).get("degradation_score", 0.05)

    def get_all_health_telemetry(self) -> List[Dict[str, Any]]:
        """Returns complete snapshot of all banking rails."""
        return list(self.bank_metrics.values())

    def simulate_synthetic_pulse_scan(self) -> List[Dict[str, Any]]:
        """
        Runs synthetic probe pings across all core banking switch endpoints.
        """
        results = []
        for bank in SUPPORTED_BANKS:
            sim_latency = random.uniform(70.0, 190.0)
            sim_err = random.random() < 0.03
            sim_timeout = sim_latency > 800.0
            res = self.record_bank_telemetry(bank, sim_latency, sim_err, sim_timeout)
            results.append(res)
        return results

# Global Singleton Instance
bank_health_pulse_sensor = BankHealthPulseSensor()
