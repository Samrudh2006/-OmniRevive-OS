"""
Stage 4 Mathematical Validation & 4-Strategy Discrete-Event Benchmark Tests
"""

import math
import pytest
from backend.app.recovery_optimizer import RecoveryHazardOptimizer
from benchmarks.strategy_comparison import run_four_strategy_comparison


def test_weibull_analytical_vs_scipy_equivalence():
    """Verifies SciPy weibull_min implementation matches closed-form F(t) and h(t) in minutes^-1."""
    prof = RecoveryHazardOptimizer.SYNTHETIC_BANK_HAZARD_PROFILES["HDFC"]
    b_haz = prof["base_hazard"]
    beta = prof["shape_beta"]

    for t in [15.0, 30.0, 45.0, 60.0]:
        cdf_a, haz_a = RecoveryHazardOptimizer.analytical_cdf_and_hazard(t, b_haz, beta)
        prob_s, haz_s = RecoveryHazardOptimizer.compute_cumulative_recovery_probability(t, "HDFC")
        assert abs(prob_s - round(max(0.05, min(0.98, cdf_a)), 4)) <= 1e-4
        assert abs(haz_s - round(haz_a, 5)) <= 1e-4


def test_weibull_parameter_validation_and_bounds():
    with pytest.raises(ValueError):
        RecoveryHazardOptimizer.compute_cumulative_recovery_probability(float("nan"), "HDFC")
    with pytest.raises(ValueError):
        RecoveryHazardOptimizer.compute_cumulative_recovery_probability(float("inf"), "HDFC")
    with pytest.raises(ValueError):
        RecoveryHazardOptimizer.validate_parameters(10.0, -0.05, 1.2)
    with pytest.raises(ValueError):
        RecoveryHazardOptimizer.validate_parameters(10.0, 0.03, 0.0)

    # Edge cases: t <= 0 -> (0.0, 0.0), extreme positive t clamped safely without NaN
    assert RecoveryHazardOptimizer.compute_cumulative_recovery_probability(0.0, "HDFC") == (0.0, 0.0)
    assert RecoveryHazardOptimizer.compute_cumulative_recovery_probability(-10.0, "HDFC") == (0.0, 0.0)
    prob_max, haz_max = RecoveryHazardOptimizer.compute_cumulative_recovery_probability(10000.0, "SBI")
    assert math.isfinite(prob_max) and 0.05 <= prob_max <= 0.98
    assert math.isfinite(haz_max) and haz_max >= 0.0


def test_retry_exhaustion_velocity_block_and_circuit_breaker():
    # Exhausted budget (> MAX_RETRY_ATTEMPTS = 3)
    rec_ex = RecoveryHazardOptimizer.select_optimal_retry_window("TRANSIENT_GATEWAY", attempt_number=4, bank_issuer="HDFC")
    assert rec_ex.retry_eligible is False
    assert rec_ex.recommended_retry_delay_minutes == 0
    assert rec_ex.success_probability == 0.0

    # Suspicious velocity prohibited
    rec_fraud = RecoveryHazardOptimizer.select_optimal_retry_window("SUSPICIOUS_VELOCITY", attempt_number=1, bank_issuer="HDFC")
    assert rec_fraud.retry_eligible is False
    assert rec_fraud.recommended_fallback_rail == "MANUAL_FRAUD_REVIEW"

    # PNB switch outage integrates circuit breaker status & fallback advice
    rec_pnb = RecoveryHazardOptimizer.select_optimal_retry_window("TRANSIENT_GATEWAY", attempt_number=1, bank_issuer="PNB")
    assert rec_pnb.circuit_breaker_open is True
    assert rec_pnb.recommended_fallback_rail is not None
    assert rec_pnb.recommended_retry_delay_minutes >= 90


def test_four_strategy_reproducible_comparison():
    res1 = run_four_strategy_comparison(seed=42, verbose=False)
    res2 = run_four_strategy_comparison(seed=42, verbose=False)
    assert res1 == res2  # Exact deterministic reproducibility

    strats = res1["strategies"]
    assert set(strats.keys()) == {"fixed_interval", "exponential_backoff", "exponential_backoff_jitter", "weibull_optimization"}

    w = strats["weibull_optimization"]
    exp = strats["exponential_backoff"]
    fix = strats["fixed_interval"]

    # Weibull + diagnostic routing achieves higher tx recovery & much fewer wasted gateway calls than fixed/exp baselines
    assert w["classification_accuracy_pct"] == 100.0
    assert w["recovered_count"] > exp["recovered_count"]
    assert w["recovered_count"] > fix["recovered_count"]
    assert w["gateway_load_calls"] < fix["gateway_load_calls"]
    assert w["duplicate_dispatches"] == 0
