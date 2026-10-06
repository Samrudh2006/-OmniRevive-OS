"""
OmniRevive-OS Columnar Analytics & OLAP Query Engine
====================================================
Simulates sub-10ms ClickHouse / Apache Parquet columnar analytics for high-volume
payment recovery time-series.

Stores columnar vectors (numpy arrays) for:
- Timestamp (epoch float64)
- Amount (float32)
- Bank (categorical uint8)
- Error Class (categorical uint8)
- Recovery Latency (float32)
- Recovered Status (bool)
"""

import time
import logging
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger("OmniRevive.ColumnarOLAP")

BANK_MAP = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "PNB", "OTHER"]
ERROR_MAP = ["TRANSIENT_GATEWAY", "INSUFFICIENT_FUNDS", "EXPIRED_MANDATE", "USER_DROPOUT", "SUSPICIOUS_VELOCITY"]

class ColumnarAnalyticsStore:
    """High-performance in-memory columnar query engine."""
    def __init__(self, initial_capacity: int = 10000):
        self.capacity = initial_capacity
        self.size = 0
        
        # Column vectors
        self.col_timestamp = np.zeros(initial_capacity, dtype=np.float64)
        self.col_amount = np.zeros(initial_capacity, dtype=np.float32)
        self.col_bank = np.zeros(initial_capacity, dtype=np.uint8)
        self.col_error = np.zeros(initial_capacity, dtype=np.uint8)
        self.col_latency = np.zeros(initial_capacity, dtype=np.float32)
        self.col_recovered = np.zeros(initial_capacity, dtype=bool)

        self._seed_sample_analytics()

    def _seed_sample_analytics(self):
        """Seeds 2,500 historical transaction drop logs for immediate analytical OLAP querying."""
        np.random.seed(42)
        count = 2500
        now = time.time()
        
        self.col_timestamp[:count] = now - np.random.uniform(0, 86400 * 7, size=count)
        self.col_amount[:count] = np.random.exponential(scale=3500.0, size=count) + 99.0
        self.col_bank[:count] = np.random.randint(0, len(BANK_MAP), size=count)
        self.col_error[:count] = np.random.randint(0, len(ERROR_MAP), size=count)
        self.col_latency[:count] = np.random.normal(loc=120.0, scale=35.0, size=count)
        self.col_recovered[:count] = np.random.random(size=count) > 0.22  # 78% recovery rate
        self.size = count

    def execute_olap_aggregation(
        self,
        bank_filter: Optional[str] = None,
        min_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes sub-millisecond vectorized aggregation using NumPy columnar SIMD instructions.
        """
        start_t = time.perf_counter()
        
        mask = np.ones(self.size, dtype=bool)
        if bank_filter and bank_filter.upper() in BANK_MAP:
            bank_idx = BANK_MAP.index(bank_filter.upper())
            mask &= (self.col_bank[:self.size] == bank_idx)
            
        if min_amount is not None:
            mask &= (self.col_amount[:self.size] >= min_amount)

        matched_count = int(np.sum(mask))
        if matched_count == 0:
            query_time_ms = round((time.perf_counter() - start_t) * 1000, 3)
            return {
                "matched_records": 0,
                "total_gmv_inr": 0.0,
                "recovery_rate_pct": 0.0,
                "mean_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "query_execution_time_ms": query_time_ms
            }

        amounts = self.col_amount[:self.size][mask]
        recovered = self.col_recovered[:self.size][mask]
        latencies = self.col_latency[:self.size][mask]

        total_gmv = float(np.sum(amounts))
        recovered_gmv = float(np.sum(amounts[recovered]))
        recovery_rate = float(np.mean(recovered)) * 100.0
        mean_lat = float(np.mean(latencies))
        p95_lat = float(np.percentile(latencies, 95))

        query_time_ms = round((time.perf_counter() - start_t) * 1000, 3)

        return {
            "matched_records": matched_count,
            "total_at_risk_gmv_inr": round(total_gmv, 2),
            "total_recovered_gmv_inr": round(recovered_gmv, 2),
            "net_recovery_rate_pct": round(recovery_rate, 2),
            "mean_latency_ms": round(mean_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "query_execution_time_ms": query_time_ms,
            "columnar_vector_engine": "ClickHouse-Style In-Memory SIMD"
        }

columnar_analytics_store = ColumnarAnalyticsStore()
