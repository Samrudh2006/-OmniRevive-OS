import os
import uuid
import time
import logging
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Request, status, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from backend.app.config import settings
from backend.app.middleware.rate_limiter import SlidingWindowRateLimiter

# Shared Telemetry Services and Metrics Singletons
from backend.app.services.telemetry_service import (
    s_logger,
    logger,
    LIVE_LOGS_BUFFER,
    LATEST_BENCHMARK_CACHE,
    ACTIVE_SECURITY_ALERTS,
    log_system_event,
    RECOVERY_REQUESTS_TOTAL,
    RECOVERED_GMV_INR,
    DIAGNOSTIC_LATENCY_HISTOGRAM,
    IDEMPOTENCY_COLLISIONS_TOTAL
)

# Core Recovery Pipeline Service (Re-exported for backward compatibility)
from backend.app.services.recovery_execution_service import execute_recovery_pipeline

# Modular Route Controllers
from backend.app.routes.system import router as system_router
from backend.app.routes.benchmarks import router as benchmarks_router
from backend.app.routes.recovery import (
    router as recovery_router,
    SimulatedFailureRequest,
    UpiQrRequest,
    InspectTokenRequest,
    BulkJsonRequest
)
from backend.app.routes.b2b import router as b2b_router
from backend.app.routes.communication import router as communication_router
from backend.app.routes.audit import router as audit_router
from backend.app.routes.telemetry import router as telemetry_router
from backend.app.routes.copilot import router as copilot_router
from backend.app.routes.aws_router import router as aws_router
from backend.app.routes.cfo import router as cfo_router
from backend.app.routes.memory import router as memory_router

TAGS_METADATA = [
    {
        "name": "System & Telemetry",
        "description": "Health checks, system diagnostics, and Prometheus SRE metrics.",
    },
    {
        "name": "Fast-Loop Recovery Engine",
        "description": "Autonomous real-time diagnostic engine, Weibull hazard curves, and dynamic UPI/mandate retries.",
    },
    {
        "name": "Deep-Loop B2B Voice & PTP",
        "description": "Deterministic Finite State Machine (FSM) voice agent for invoice mutation and Promise-to-Pay (PTP) scheduling.",
    },
    {
        "name": "Cryptographic Audit Ledger",
        "description": "Sequential SHA-256 Merkle hash chain verification and forensic ledger export.",
    },
    {
        "name": "Production Benchmarks",
        "description": "100-case held-out production benchmark evaluation and GMV recovery telemetry.",
    },
    {
        "name": "Executive CFO Governance",
        "description": "Zero-trust executive approval queue with cryptographic audit chaining and dual-key signoff.",
    },
    {
        "name": "AWS Zero-Trust Security",
        "description": "Formal AWS Cedar policy enforcement engine and zero-trust evaluation.",
    },
    {
        "name": "AWS Generative AI",
        "description": "Amazon Bedrock foundation model orchestration for voice synthesis and dispute parsing.",
    }
]

app = FastAPI(
    title="RazorRevive-OS API",
    description="""
# 🚀 RazorRevive-OS Control Plane API

Autonomous AI Revenue Recovery Engine with Zero-Trust Cryptographic Guardrails, Dynamic Mandate Retrier & B2B Voice PTP Engine.

### 🏛️ Architecture Highlights:
* **Tier 1 (Fast-Loop):** Sub-millisecond error classification, hazard window optimization, and dynamic UPI payment links.
* **Tier 2 (Deep-Loop):** Deterministic voice FSM for automated dispute resolution and promise-to-pay calendar locks.
* **Tier 3 (Policy Gatekeeper):** Zero-trust compliance rules enforcing TRAI quiet hours (21:00-09:00 IST), maximum discount caps (<=10%, <=INR 500), and distributed idempotency.
* **Audit Ledger:** SHA-256 sequential hash chaining ensuring 100% cryptographic continuity.
    """,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "Razorpay AI Buildathon Engineering Team",
        "url": "https://github.com/Samrudh2006/Razorpay-Target-0.1percent-"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", f"tr_{uuid.uuid4().hex[:12]}")
    request.state.trace_id = trace_id
    
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if "/communication/" in request.url.path and request.url.path.endswith("/html"):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
    else:
        response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(self), payment=(self)"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com data:",
        "img-src 'self' data: blob: https:",
        "connect-src 'self' ws: wss: https:",
        "media-src 'self' blob: data:",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
    response.headers["X-Trace-ID"] = trace_id
    return response

# Standardized Error Handling Middleware & Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    log_system_event("WARN", "HTTP", f"HTTP {exc.status_code}: {exc.detail}", trace_id=trace_id)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            },
            "trace_id": trace_id,
            "timestamp": time.time()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    log_system_event("WARN", "SchemaValidation", "Payload failed schema validation", trace_id=trace_id)
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "SCHEMA_VALIDATION_ERROR",
                "message": "Input payload failed schema validation.",
                "details": exc.errors()
            },
            "trace_id": trace_id,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
    logger.error(f"[UNHANDLED_EXCEPTION] Trace {trace_id}: {exc}", exc_info=True)
    log_system_event("ERROR", "UnhandledException", str(exc), trace_id=trace_id)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal error occurred. Execution safely contained."
            },
            "trace_id": trace_id,
            "timestamp": time.time()
        }
    )

# Security and Rate Limiting Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlidingWindowRateLimiter)

# Static Asset Serving & Dashboard Root
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    assets_dir = os.path.join(frontend_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/copilot_avatar.jpg")
async def serve_copilot_avatar():
    img_path = os.path.join(frontend_dir, "assets", "copilot_avatar.jpg")
    if not os.path.exists(img_path):
        img_path = os.path.join(frontend_dir, "copilot_avatar.jpg")
    if os.path.exists(img_path):
        return FileResponse(img_path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Avatar image not found")

@app.get("/aws_logo.png")
async def serve_aws_logo():
    img_path = os.path.join(frontend_dir, "assets", "aws_logo.png")
    if not os.path.exists(img_path):
        img_path = os.path.join(frontend_dir, "aws_logo.png")
    if os.path.exists(img_path):
        return FileResponse(img_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="AWS logo image not found")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the RazorRevive-OS Control Plane Dashboard."""
    frontend_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>RazorRevive-OS Control Plane Running</h1>"

# Register Modular Routers
app.include_router(system_router)
app.include_router(benchmarks_router)
app.include_router(recovery_router)
app.include_router(b2b_router)
app.include_router(communication_router)
app.include_router(audit_router)
app.include_router(telemetry_router)
app.include_router(copilot_router)
app.include_router(aws_router)
app.include_router(cfo_router)
app.include_router(memory_router)
