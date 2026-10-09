"""
OmniRevive-OS Contextual Multi-Armed Bandit Routing Engine
=========================================================
Research Foundations:
- "A Contextual-Bandit Approach to Personalized Recommendation" (Li et al., WWW 2010 - LinUCB)
- "Analysis of Thompson Sampling for the Multi-Armed Bandit Problem" (Agrawal & Goyal, COLT 2012)

Dynamically routes transactions across multiple payment rails (Razorpay, Juspay, PhonePe, Cashfree, Stripe)
by learning an online linear payoff model based on contextual covariates:
- Normalized Transaction Amount
- Bank Issuer Baseline Latency & Outage Score
- Cyclical Time-of-Day Features (sin/cos encoding)
- Historic Rail Success Rate & Latency Covariance
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger("OmniRevive.ContextualBandit")

SUPPORTED_RAILS = ["RAZORPAY", "JUSPAY", "PHONEPE", "CASHFREE", "STRIPE"]
FEATURE_DIMENSION = 8

class DisjointLinUCBArm:
    """Represents a single payment rail arm with its Ridge Regression parameters."""
    def __init__(self, rail_name: str, d: int = FEATURE_DIMENSION, alpha: float = 0.5):
        self.rail_name = rail_name
        self.d = d
        self.alpha = alpha  # Exploration trade-off hyperparameter
        self.A = np.identity(d, dtype=np.float64)  # d x d covariance matrix (A_a = I + D_a^T D_a)
        self.A_inv = np.identity(d, dtype=np.float64)
        self.b = np.zeros((d, 1), dtype=np.float64)  # d x 1 response vector (b_a = D_a^T c_a)
        self.total_trials = 0
        self.total_rewards = 0.0

    def compute_score(self, x: np.ndarray) -> Tuple[float, float, float]:
        r"""
        Computes LinUCB upper confidence bound:
        p_{t,a} = \hat{\theta}_a^T x_t + \alpha \sqrt{x_t^T A_a^{-1} x_t}
        Returns: (ucb_score, expected_mean, confidence_bonus)
        """
        theta_hat = self.A_inv @ self.b
        expected_mean = float((theta_hat.T @ x).item())
        variance = float((x.T @ self.A_inv @ x).item())
        bonus = self.alpha * math.sqrt(max(1e-6, variance))
        ucb_score = expected_mean + bonus
        return ucb_score, expected_mean, bonus

    def update(self, x: np.ndarray, reward: float):
        """Online Sherman-Morrison rank-1 update for A_inv and vector b."""
        self.A += x @ x.T
        self.b += reward * x
        # Recompute inverse with regularized numerical stability
        try:
            self.A_inv = np.linalg.pinv(self.A)
        except Exception:
            self.A_inv = np.linalg.inv(self.A + 1e-4 * np.identity(self.d))
        self.total_trials += 1
        self.total_rewards += reward


class ThompsonSamplingArm:
    """Thompson Sampling arm with Gaussian likelihood & conjugate normal prior."""
    def __init__(self, rail_name: str, d: int = FEATURE_DIMENSION, v_sq: float = 0.25):
        self.rail_name = rail_name
        self.d = d
        self.v_sq = v_sq  # Prior variance scale
        self.B = np.identity(d, dtype=np.float64)
        self.B_inv = np.identity(d, dtype=np.float64)
        self.f = np.zeros((d, 1), dtype=np.float64)
        self.mu_hat = np.zeros((d, 1), dtype=np.float64)

    def sample_score(self, x: np.ndarray) -> float:
        r"""Draws posterior parameter sample \tilde{\mu} ~ N(\hat{\mu}, v^2 B^{-1}) and returns \tilde{\mu}^T x."""
        cov = self.v_sq * self.B_inv
        # Symmetrize covariance to prevent numerical jitter
        cov = (cov + cov.T) / 2.0
        try:
            sample_theta = np.random.multivariate_normal(self.mu_hat.flatten(), cov).reshape((self.d, 1))
        except Exception:
            sample_theta = self.mu_hat
        return float((sample_theta.T @ x).item())

    def update(self, x: np.ndarray, reward: float):
        self.B += x @ x.T
        self.f += reward * x
        self.B_inv = np.linalg.pinv(self.B)
        self.mu_hat = self.B_inv @ self.f


class ContextualMultiRailRouter:
    """
    Contextual Multi-Rail Routing Engine for Zero-Downtime Payment Recovery.
    Combines LinUCB and Thompson Sampling with bank health telemetry.
    """
    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha
        self.linucb_arms: Dict[str, DisjointLinUCBArm] = {
            rail: DisjointLinUCBArm(rail, d=FEATURE_DIMENSION, alpha=alpha)
            for rail in SUPPORTED_RAILS
        }
        self.ts_arms: Dict[str, ThompsonSamplingArm] = {
            rail: ThompsonSamplingArm(rail, d=FEATURE_DIMENSION)
            for rail in SUPPORTED_RAILS
        }
        self._seed_priors()

    def _seed_priors(self):
        """Warm-start priors with historical fintech baseline success rates."""
        priors = {
            "RAZORPAY": 0.88,
            "JUSPAY": 0.91,
            "PHONEPE": 0.89,
            "CASHFREE": 0.85,
            "STRIPE": 0.94
        }
        for rail, prior_rate in priors.items():
            dummy_x = np.ones((FEATURE_DIMENSION, 1)) * 0.1
            self.linucb_arms[rail].update(dummy_x, prior_rate)
            self.ts_arms[rail].update(dummy_x, prior_rate)

    @staticmethod
    def extract_context_vector(
        amount_inr: float,
        bank_issuer: str,
        attempt_number: int,
        hour_of_day: Optional[int] = None,
        switch_degradation_score: float = 0.0
    ) -> np.ndarray:
        r"""
        Extracts an 8-dimensional normalized context vector x \in R^8:
        x[0]: Intercept bias (1.0)
        x[1]: Log-normalized amount: log10(amount + 1) / 6.0
        x[2]: High ticket binary (>₹50,000)
        x[3]: Bank risk tier (HDFC/ICICI=0.1, SBI/PNB=0.5, Others=0.3)
        x[4]: Attempt penalty: attempt / 5.0
        x[5]: Time-of-day sin component: sin(2 * pi * hour / 24)
        x[6]: Time-of-day cos component: cos(2 * pi * hour / 24)
        x[7]: Live NPCI Switch Degradation penalty (0.0 to 1.0)
        """
        if hour_of_day is None:
            hour_of_day = time.localtime().tm_hour

        bank_upper = (bank_issuer or "DEFAULT").upper()
        bank_tier_map = {
            "HDFC": 0.15, "ICICI": 0.12, "AXIS": 0.20, "KOTAK": 0.18,
            "SBI": 0.45, "PNB": 0.60, "BOB": 0.50, "DEFAULT": 0.30
        }
        bank_score = bank_tier_map.get(bank_upper, 0.30)

        log_amount = math.log10(max(1.0, float(amount_inr)) + 1.0) / 6.0
        is_high_ticket = 1.0 if amount_inr >= 50000.0 else 0.0
        attempt_feat = min(1.0, max(0.0, float(attempt_number) / 5.0))
        hour_rad = 2.0 * math.pi * float(hour_of_day) / 24.0
        sin_hour = math.sin(hour_rad)
        cos_hour = math.cos(hour_rad)
        if switch_degradation_score <= 0.0:
            try:
                from backend.app.services.bank_health_pulse import bank_health_pulse_sensor
                switch_degradation_score = bank_health_pulse_sensor.get_bank_degradation(bank_upper)
            except Exception:
                switch_degradation_score = 0.05

        degrade_feat = min(1.0, max(0.0, float(switch_degradation_score)))

        x = np.array([
            [1.0],
            [log_amount],
            [is_high_ticket],
            [bank_score],
            [attempt_feat],
            [sin_hour],
            [cos_hour],
            [degrade_feat]
        ], dtype=np.float64)
        return x

    def select_optimal_rail(
        self,
        amount_inr: float,
        bank_issuer: str,
        attempt_number: int = 1,
        strategy: str = "LINUCB"
    ) -> Dict[str, Any]:
        """
        Evaluates all candidate payment rails and selects the arm maximizing reward.
        Returns detailed decision telemetry including confidence bounds and fallback hierarchy.
        """
        x = self.extract_context_vector(amount_inr, bank_issuer, attempt_number)
        rail_evaluations = []

        for rail in SUPPORTED_RAILS:
            if strategy.upper() == "THOMPSON":
                score = self.ts_arms[rail].sample_score(x)
                expected_mean = float((self.ts_arms[rail].mu_hat.T @ x).item())
                bonus = score - expected_mean
            else:
                score, expected_mean, bonus = self.linucb_arms[rail].compute_score(x)

            rail_evaluations.append({
                "rail": rail,
                "ucb_score": round(float(score), 4),
                "expected_success_rate": round(float(np.clip(expected_mean, 0.05, 0.99)), 4),
                "exploration_bonus": round(float(bonus), 4),
                "total_observations": self.linucb_arms[rail].total_trials
            })

        # Sort descending by score
        rail_evaluations.sort(key=lambda item: item["ucb_score"], reverse=True)
        winner = rail_evaluations[0]
        fallbacks = [r["rail"] for r in rail_evaluations[1:3]]

        return {
            "selected_rail": winner["rail"],
            "expected_success_rate": winner["expected_success_rate"],
            "ucb_score": winner["ucb_score"],
            "exploration_bonus": winner["exploration_bonus"],
            "strategy": strategy.upper(),
            "fallback_rails": fallbacks,
            "all_rail_evaluations": rail_evaluations,
            "context_summary": {
                "amount_inr": amount_inr,
                "bank_issuer": bank_issuer,
                "attempt_number": attempt_number
            }
        }

    def record_feedback(
        self,
        rail: str,
        amount_inr: float,
        bank_issuer: str,
        attempt_number: int,
        success: bool,
        latency_ms: float = 120.0
    ):
        """
        Online Bayesian update with reward metric.
        Reward function penalizes latency and rewards authorization success:
        R = 1.0 - 0.2 * min(1.0, latency / 1000.0) if success else 0.0
        """
        rail_upper = rail.upper()
        if rail_upper not in self.linucb_arms:
            return

        reward = (1.0 - 0.2 * min(1.0, latency_ms / 1000.0)) if success else 0.0
        x = self.extract_context_vector(amount_inr, bank_issuer, attempt_number)
        
        self.linucb_arms[rail_upper].update(x, reward)
        self.ts_arms[rail_upper].update(x, reward)
        logger.info(f"ContextualBandit updated for rail {rail_upper}: reward={reward:.3f}, trials={self.linucb_arms[rail_upper].total_trials}")

# Singleton instance for live production routing
contextual_bandit_router = ContextualMultiRailRouter()
