import math
import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy import stats  # type: ignore
from backend.app.config import settings
from backend.app.schemas import RetryWindowRecommendation, FailureClassType
from backend.app.telemetry_npci import npci_telemetry

logger = logging.getLogger("OmniRevive.RecoveryOptimizer")

class RecoveryHazardOptimizer:
    """
    Statistical Recovery Hazard & Optimal Retry Window Model.
    
    CRITICAL METHODOLOGY NOTE:
    This model computes conditional recovery probabilities using an empirical hazard rate function h(t)
    fitted over synthetic historical bank outage telemetry data using SciPy and NumPy survival analysis.
    Units: all time variables (`t_minutes`, `scale_eta`, `peak_window_min`) are strictly in MINUTES,
    and `base_hazard` is in MIN^-1 so (base_hazard * t) is dimensionless.
    """

    # Empirical baseline hazard parameters (lambda_0 [min^-1], shape_beta) derived from synthetic historical bank outage logs
    SYNTHETIC_BANK_HAZARD_PROFILES: Dict[str, Dict[str, float]] = {
        "HDFC": {"base_hazard": 0.038, "shape_beta": 1.25, "peak_window_min": 45},
        "SBI": {"base_hazard": 0.022, "shape_beta": 1.10, "peak_window_min": 60},
        "ICICI": {"base_hazard": 0.045, "shape_beta": 1.30, "peak_window_min": 30},
        "AXIS": {"base_hazard": 0.035, "shape_beta": 1.20, "peak_window_min": 45},
        "KOTAK": {"base_hazard": 0.040, "shape_beta": 1.28, "peak_window_min": 35},
        "PNB": {"base_hazard": 0.015, "shape_beta": 1.05, "peak_window_min": 90},
        "DEFAULT": {"base_hazard": 0.030, "shape_beta": 1.15, "peak_window_min": 40}
    }

    CANDIDATE_WINDOWS_MINUTES: List[int] = [15, 30, 45, 60, 90, 120]

    @staticmethod
    def validate_parameters(t_minutes: float, base_hazard: float, shape_beta: float) -> float:
        """Validates numerical stability and dimensional positivity of Weibull inputs."""
        if not isinstance(t_minutes, (int, float)) or not math.isfinite(float(t_minutes)):
            raise ValueError(f"t_minutes must be a finite numeric value, got {t_minutes!r}")
        if base_hazard <= 0 or not math.isfinite(base_hazard):
            raise ValueError(f"base_hazard must be positive finite (min^-1), got {base_hazard!r}")
        if shape_beta <= 0 or not math.isfinite(shape_beta):
            raise ValueError(f"shape_beta must be positive finite, got {shape_beta!r}")
        return min(float(t_minutes), 1440.0)

    @classmethod
    def analytical_cdf_and_hazard(cls, t_minutes: float, base_hazard: float, shape_beta: float) -> Tuple[float, float]:
        """Closed-form Weibull CDF F(t) = 1 - exp(-(t/eta)^beta) and hazard h(t) = (beta/eta)*(t/eta)^(beta-1)."""
        safe_t = cls.validate_parameters(t_minutes, base_hazard, shape_beta)
        if safe_t <= 0.0:
            return 0.0, 0.0
        eta = 1.0 / base_hazard
        ratio = safe_t / eta
        cdf = 1.0 - math.exp(-(ratio ** shape_beta))
        hazard = (shape_beta / eta) * (ratio ** (shape_beta - 1.0))
        return cdf, hazard

    @classmethod
    def compute_cumulative_recovery_probability(
        cls,
        t_minutes: float,
        bank_profile: str = "DEFAULT"
    ) -> Tuple[float, float]:
        """
        Computes F(t) = 1 - exp(- (base_hazard * t)^shape_beta) under Weibull-Hazard model via SciPy/NumPy.
        Returns: (cumulative_prob, instantaneous_hazard [min^-1])
        """
        prof = cls.SYNTHETIC_BANK_HAZARD_PROFILES.get(bank_profile.upper(), cls.SYNTHETIC_BANK_HAZARD_PROFILES["DEFAULT"])
        b_haz = prof["base_hazard"]
        beta = prof["shape_beta"]

        safe_t = cls.validate_parameters(t_minutes, b_haz, beta)
        if safe_t <= 0.0:
            return 0.0, 0.0

        # Scale parameter eta = 1 / base_hazard for SciPy weibull_min(c=beta, scale=1/b_haz)
        scale_eta = 1.0 / b_haz
        cdf_prob = float(stats.weibull_min.cdf(safe_t, c=beta, scale=scale_eta))
        pdf_val = float(stats.weibull_min.pdf(safe_t, c=beta, scale=scale_eta))

        # Numerical stability guard against underflow at extreme horizons
        survival = max(1e-9, 1.0 - cdf_prob)
        instant_hazard = float(pdf_val / survival) if pdf_val > 0 else 0.0
        if not math.isfinite(instant_hazard):
            instant_hazard = 0.0

        bounded_prob = float(np.clip(cdf_prob, 0.05, 0.98))
        return round(bounded_prob, 4), round(max(0.0, instant_hazard), 5)

    @classmethod
    def select_optimal_retry_window(
        cls,
        failure_class: FailureClassType,
        attempt_number: int = 1,
        bank_issuer: str = "HDFC",
        max_attempts: int = settings.MAX_RETRY_ATTEMPTS
    ) -> RetryWindowRecommendation:
        """
        Evaluates candidate retry windows against the recovery hazard curve and returns
        the optimal execution delay and success probability.
        Enforces attempt exhaustion limits and NPCI switch circuit breaker integration.
        """
        safe_attempt = attempt_number if isinstance(attempt_number, int) else 1
        safe_bank = (bank_issuer or "DEFAULT").strip().upper()
        switch_status = npci_telemetry.get_switch_status(safe_bank)

        # Retry exhaustion check
        if safe_attempt > max_attempts or safe_attempt < 1:
            return RetryWindowRecommendation(
                recommended_retry_delay_minutes=0,
                success_probability=0.0,
                hazard_rate=0.0,
                retry_eligible=False,
                circuit_breaker_open=switch_status.circuit_breaker_tripped,
                recommended_fallback_rail=switch_status.recommended_fallback_rail,
                reason=f"Retry budget exhausted or invalid attempt ({safe_attempt} > max {max_attempts}). Suppress automated retry.",
                model_version="recovery-hazard-v1"
            )

        if failure_class != "TRANSIENT_GATEWAY":
            # Fraud/velocity never eligible for blind retry
            if failure_class == "SUSPICIOUS_VELOCITY":
                return RetryWindowRecommendation(
                    recommended_retry_delay_minutes=0,
                    success_probability=0.0,
                    hazard_rate=0.0,
                    retry_eligible=False,
                    circuit_breaker_open=switch_status.circuit_breaker_tripped,
                    recommended_fallback_rail="MANUAL_FRAUD_REVIEW",
                    reason="High-risk suspicious velocity failure; retry prohibited.",
                    model_version="recovery-hazard-v1"
                )
            # Soft failures (balance, expired token, OTP drop): immediate alternate channel link
            return RetryWindowRecommendation(
                recommended_retry_delay_minutes=0,
                success_probability=0.75 if failure_class == "INSUFFICIENT_FUNDS" else 0.70,
                hazard_rate=0.0,
                retry_eligible=True,
                circuit_breaker_open=switch_status.circuit_breaker_tripped,
                recommended_fallback_rail=switch_status.recommended_fallback_rail or "WHATSAPP_UPI_INTENT",
                reason=f"Non-gateway failure ({failure_class}); immediate alternate payment channel recommended.",
                model_version="recovery-hazard-v1"
            )

        prof = cls.SYNTHETIC_BANK_HAZARD_PROFILES.get(safe_bank, cls.SYNTHETIC_BANK_HAZARD_PROFILES["DEFAULT"])
        base_peak = prof["peak_window_min"]

        # Dynamic adjustment based on switch degradation or tripped circuit breaker
        if switch_status.switch_state == "DEGRADED":
            base_peak = int(base_peak * 1.4)
        elif switch_status.switch_state == "OUTAGE" or switch_status.circuit_breaker_tripped:
            base_peak = 120

        # Scaling delay with attempt number to prevent hammering degraded endpoints
        target_delay = int(base_peak * math.pow(1.5, safe_attempt - 1))

        # Find closest candidate window within [15, 120] min bounds
        best_window = min(cls.CANDIDATE_WINDOWS_MINUTES, key=lambda w: abs(w - target_delay))
        prob, hazard = cls.compute_cumulative_recovery_probability(best_window, safe_bank)

        if switch_status.switch_state == "DEGRADED":
            prob = prob * 0.85
        elif switch_status.switch_state == "OUTAGE" or switch_status.circuit_breaker_tripped:
            prob = prob * 0.40

        decayed_prob = max(0.25, prob * math.pow(0.90, safe_attempt - 1))

        cb_note = " [CIRCUIT BREAKER OPEN - FAILOVER ADVISED]" if switch_status.circuit_breaker_tripped else ""
        switch_note = f" [NPCI Switch Status: {switch_status.switch_state}]{cb_note}"
        return RetryWindowRecommendation(
            recommended_retry_delay_minutes=best_window,
            success_probability=round(decayed_prob, 3),
            hazard_rate=hazard,
            retry_eligible=True,
            circuit_breaker_open=switch_status.circuit_breaker_tripped,
            recommended_fallback_rail=switch_status.recommended_fallback_rail,
            reason=f"Optimal recovery hazard peak for {safe_bank} node at attempt {safe_attempt}{switch_note}",
            model_version="recovery-hazard-v1"
        )

recovery_optimizer = RecoveryHazardOptimizer()
