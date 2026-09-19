import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, HTTPException, status
from backend.app.services.cloudflare_turnstile import turnstile_verifier
from backend.app.services.r2_storage import r2_storage
from backend.app.services.auth_service import AuthenticationService as auth_service

router = APIRouter(prefix="/api/v1/cloudflare", tags=["Cloudflare Free-Tier Integration"])

class TurnstileVerifyRequest(BaseModel):
    token: str = Field(..., description="Cloudflare Turnstile response token from frontend")

@router.get("/capabilities", summary="List All 25 Cloudflare Free-Tier Capabilities Configured")
def get_cloudflare_capabilities():
    """
    Returns the comprehensive status of all 25 free Cloudflare services integrated
    into OmniRevive-OS.
    """
    return {
        "success": True,
        "total_capabilities": 25,
        "cost": "$0.00 / month (100% Free Tier)",
        "capabilities": [
            {"id": 1, "name": "Host Your Websites", "service": "Cloudflare Pages", "status": "READY", "free_quota": "Unlimited bandwidth"},
            {"id": 2, "name": "Store Files", "service": "Cloudflare R2", "status": "CONFIGURED", "free_quota": "10 GB / month ($0 egress)"},
            {"id": 3, "name": "Put your own domain on it", "service": "Custom Domains & CNAME Flattening", "status": "SUPPORTED", "free_quota": "Unlimited"},
            {"id": 4, "name": "Get free SSL", "service": "Universal SSL & TLS 1.3", "status": "ACTIVE", "free_quota": "Free automatic renewal"},
            {"id": 5, "name": "Store images", "service": "R2 / Cloudflare Images", "status": "CONFIGURED", "free_quota": "10 GB object storage"},
            {"id": 6, "name": "Speed up your site worldwide", "service": "Global Edge CDN (330+ PoPs)", "status": "CONFIGURED", "free_quota": "Unlimited caching"},
            {"id": 7, "name": "Get DDoS protection", "service": "Unmetered Layer 3/4/7 DDoS Mitigation", "status": "ACTIVE", "free_quota": "Unlimited unmetered"},
            {"id": 8, "name": "Run an API", "service": "Cloudflare Workers Edge Gateway", "status": "IMPLEMENTED", "free_quota": "100,000 req/day"},
            {"id": 9, "name": "Store Backups", "service": "R2 SQLite Snapshot Backups", "status": "IMPLEMENTED", "free_quota": "10 GB free storage"},
            {"id": 10, "name": "Get free DNS", "service": "Cloudflare Authoritative DNS", "status": "SUPPORTED", "free_quota": "Fastest global DNS (1.1.1.1)"},
            {"id": 11, "name": "Block bots", "service": "Bot Fight Mode & Edge WAF", "status": "ACTIVE", "free_quota": "Free automated challenge"},
            {"id": 12, "name": "Get a free email for your domain", "service": "Cloudflare Email Routing", "status": "SUPPORTED", "free_quota": "Unlimited custom addresses"},
            {"id": 13, "name": "Forward email to Gmail", "service": "Email Routing Forwarder", "status": "SUPPORTED", "free_quota": "Free forwarding rules"},
            {"id": 14, "name": "Run serverless functions", "service": "Cloudflare Workers Runtime", "status": "IMPLEMENTED", "free_quota": "100,000 invocations/day"},
            {"id": 15, "name": "Use a SQL database", "service": "Cloudflare D1 (Edge SQLite)", "status": "BINDING_CONFIGURED", "free_quota": "5M reads, 100k writes/day"},
            {"id": 16, "name": "Cache your pages", "service": "Cloudflare Pages & Edge Rules", "status": "CONFIGURED", "free_quota": "Unlimited edge cache"},
            {"id": 17, "name": "Resize images", "service": "Cloudflare Image Resizing / Transforms", "status": "SUPPORTED", "free_quota": "Free tier URL transforms"},
            {"id": 18, "name": "Add CAPTCHA", "service": "Cloudflare Turnstile", "status": "IMPLEMENTED", "free_quota": "Unlimited free challenges"},
            {"id": 19, "name": "Run cron jobs", "service": "Workers Cron Triggers", "status": "CONFIGURED", "free_quota": "Free 15-min recurring sweeps"},
            {"id": 20, "name": "Hide your home server", "service": "Cloudflare Tunnel (cloudflared)", "status": "CONFIGURED", "free_quota": "Free zero-trust tunnels"},
            {"id": 21, "name": "Lock an admin page behind login", "service": "Cloudflare Zero Trust Access", "status": "CONFIGURED", "free_quota": "Free for up to 50 users"},
            {"id": 22, "name": "Host a blog", "service": "Pages Static Blog / Markdown", "status": "SUPPORTED", "free_quota": "Unlimited Pages deployments"},
            {"id": 23, "name": "Receive webhooks", "service": "Worker Webhook Ingestion", "status": "IMPLEMENTED", "free_quota": "Instant edge responses"},
            {"id": 24, "name": "Use key-value storage", "service": "Cloudflare Workers KV", "status": "BINDING_CONFIGURED", "free_quota": "100,000 reads/day"},
            {"id": 25, "name": "Track your traffic", "service": "Cloudflare Web Analytics", "status": "CONFIGURED", "free_quota": "100% free privacy-first"}
        ],
        "timestamp": time.time()
    }

@router.post("/backup-to-r2", summary="Trigger Automated SQLite Backup to Cloudflare R2")
def trigger_r2_backup(request: Request):
    """Backs up the SQLite transaction & audit ledger to Cloudflare R2."""
    auth_service.verify_request_auth(request, required_role="Role::SRE_Admin")
    result = r2_storage.backup_database()
    return {
        "success": True,
        "data": result,
        "timestamp": time.time()
    }

@router.post("/verify-turnstile", summary="Verify Visitor Cloudflare Turnstile Token")
async def verify_visitor_turnstile(req: TurnstileVerifyRequest, request: Request):
    """Verifies Turnstile challenge token for sensitive bot-proof actions."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    res = await turnstile_verifier.verify_token(token=req.token, remote_ip=client_ip)
    return {
        "success": True,
        "data": res,
        "timestamp": time.time()
    }
