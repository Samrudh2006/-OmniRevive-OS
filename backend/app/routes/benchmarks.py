import time
import uuid
from fastapi import APIRouter, Request
from benchmarks.benchmark_runner import run_held_out_benchmark
from backend.app.services.telemetry_service import (
    log_system_event,
    LATEST_BENCHMARK_CACHE
)

router = APIRouter()

@router.post("/api/v1/benchmark/run", tags=["Production Benchmarks"], summary="Trigger 100-Batch Recovery Benchmark")
async def trigger_benchmark_run(request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    log_system_event("INFO", "Benchmark", "Initiated 100-batch dynamic held-out evaluation", trace_id=trace_id)
    results = run_held_out_benchmark()
    
    LATEST_BENCHMARK_CACHE["total_transactions"] = results["total_records"]
    LATEST_BENCHMARK_CACHE["at_risk_gmv"] = results["total_at_risk_gmv"]
    LATEST_BENCHMARK_CACHE["recovered_gmv"] = results["recovered_gmv"]
    LATEST_BENCHMARK_CACHE["recovery_rate_pct"] = results["recovered_count"] / float(results["total_records"]) * 100.0
    LATEST_BENCHMARK_CACHE["false_positive_cost_inr"] = results["false_positive_overhead_inr"]

    log_system_event(
        "INFO",
        "Benchmark",
        f"Benchmark completed: {LATEST_BENCHMARK_CACHE['recovery_rate_pct']:.2f}% net recovery across 100 cases",
        trace_id=trace_id
    )

    return {
        "success": True,
        "data": {
            "summary": LATEST_BENCHMARK_CACHE,
            "raw_metrics": results
        },
        "trace_id": trace_id,
        "timestamp": time.time()
    }

@router.get("/api/v1/benchmark/latest", tags=["Production Benchmarks"], summary="Fetch Latest Benchmark Metrics")
async def get_latest_benchmark(request: Request):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    return {
        "success": True,
        "data": LATEST_BENCHMARK_CACHE,
        "trace_id": trace_id,
        "timestamp": time.time()
    }
