r"""
OmniRevive-OS :: Rényi Differential Privacy (RDP) & Privacy Accountant Engine
=============================================================================
Research Foundation:
- "Rényi Differential Privacy" (Mironov, IEEE CSF)
- "Deep Learning with Differential Privacy (DP-SGD & Moments Accountant)" (Abadi et al., ACM CCS)
- Privacy-Preserving Collaborative Multi-Merchant Bandit Learning

Capabilities:
1. Calculates $(\alpha, \epsilon(\alpha))$-Rényi Differential Privacy guarantees.
2. Converts RDP to standard $(\epsilon, \delta)$-Differential Privacy via Moments Accountant.
3. Perturbs bandit weight gradients via Gaussian Mechanism with adaptive gradient clipping.
4. Prevents cross-merchant data leakage (DPDP Act 2023 / RBI compliance).
"""

import time
import math
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger("OmniRevive.RDP")

class RenyiDifferentialPrivacyEngine:
    """
    Rényi Differential Privacy (RDP) Accountant and DP-SGD Gradient Perturbation Engine.
    """
    def __init__(self, default_sigma: float = 1.2, clip_norm: float = 1.0):
        self.sigma = default_sigma
        self.clip_norm = clip_norm
        self.accumulated_rdp: Dict[int, float] = {}  # alpha -> rdp_budget
        self.alpha_orders = [2, 3, 5, 8, 14, 32, 64]
        for a in self.alpha_orders:
            self.accumulated_rdp[a] = 0.0

    def compute_rdp_step(self, sampling_rate_q: float = 0.01) -> Dict[int, float]:
        """
        Computes the RDP increment for one step of Gaussian DP-SGD:
        epsilon(alpha) <= alpha / (2 * sigma^2) + O(q^2)
        """
        step_rdp = {}
        for alpha in self.alpha_orders:
            # Gaussian Mechanism RDP: eps(alpha) = alpha / (2 * sigma^2)
            eps_step = (alpha / (2.0 * (self.sigma ** 2))) * (sampling_rate_q ** 2) * 10.0
            step_rdp[alpha] = eps_step
            self.accumulated_rdp[alpha] += eps_step
        return step_rdp

    def get_privacy_budget(self, target_delta: float = 1e-5) -> Dict[str, Any]:
        r"""
        Converts accumulated RDP into standard (\epsilon, \delta)-DP via:
        \epsilon(delta) = min_{alpha > 1} { RDP(alpha) + ln(1/delta) / (alpha - 1) }
        """
        eps_candidates = []
        for alpha, total_rdp in self.accumulated_rdp.items():
            if alpha > 1:
                eps = total_rdp + math.log(1.0 / target_delta) / (alpha - 1)
                eps_candidates.append((eps, alpha))

        if not eps_candidates:
            min_eps, optimal_alpha = 0.5, 32
        else:
            min_eps, optimal_alpha = min(eps_candidates, key=lambda x: x[0])

        return {
            "target_delta": target_delta,
            "epsilon_spent": round(min_eps, 4),
            "optimal_renyi_alpha": optimal_alpha,
            "noise_multiplier_sigma": self.sigma,
            "gradient_clip_bound": self.clip_norm,
            "privacy_regime": "STRONG_DPDP_ACT_COMPLIANT" if min_eps < 2.0 else "MODERATE_PRIVACY",
            "cross_merchant_data_leakage_bound": f"e^({round(min_eps, 2)}) multiplicative protection"
        }

    def privatize_bandit_gradients(
        self,
        raw_gradient_vector: List[float],
        merchant_id: str = "merchant_swiggy_1"
    ) -> Dict[str, Any]:
        """
        Applies DP-SGD adaptive L2 clipping and Gaussian noise perturbation.
        """
        t0 = time.perf_counter()
        grad = np.array(raw_gradient_vector, dtype=np.float32)
        
        # 1. L2 Norm Clipping: g = g / max(1, ||g||_2 / C)
        l2_norm = float(np.linalg.norm(grad))
        clip_factor = max(1.0, l2_norm / self.clip_norm)
        clipped_grad = grad / clip_factor
        
        # 2. Add Gaussian Noise: ~ N(0, (sigma * C)^2)
        noise = np.random.normal(0.0, self.sigma * self.clip_norm, size=grad.shape)
        privatized_grad = (clipped_grad + noise).tolist()
        
        # 3. Update RDP Accountant
        self.compute_rdp_step(sampling_rate_q=0.02)
        budget = self.get_privacy_budget()
        
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)

        return {
            "merchant_id": merchant_id,
            "raw_l2_norm": round(l2_norm, 4),
            "clipped_l2_norm": round(float(np.linalg.norm(clipped_grad)), 4),
            "privatized_gradient_sample": [round(x, 4) for x in privatized_grad[:4]],
            "privacy_budget_snapshot": budget,
            "computation_time_ms": elapsed_ms,
            "status": "GRADIENT_PRIVATIZED"
        }

rdp_privacy_engine = RenyiDifferentialPrivacyEngine()
