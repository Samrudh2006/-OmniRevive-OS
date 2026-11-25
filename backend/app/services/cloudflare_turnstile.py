import logging
import os
import httpx
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from backend.app.config import settings
from backend.app.services.circuit_breaker import retry_async

logger = logging.getLogger("OmniRevive.Cloudflare.Turnstile")

class CloudflareTurnstileVerifier:
    """
    18. Cloudflare Turnstile CAPTCHA Verification Service (100% Free).
    Validates Turnstile visitor challenge tokens against Cloudflare's siteverify endpoint.
    """

    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    @classmethod
    async def verify_token(
        cls,
        token: str,
        remote_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        secret_key = os.environ.get("CLOUDFLARE_TURNSTILE_SECRET_KEY") or getattr(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", None) or "1x0000000000000000000000000000000AA"
        
        # In demo mode with dummy testing key, allow local bypass
        if settings.SAFE_DEMO_MODE and (not token or token.startswith("test_") or secret_key.startswith("1x000000")):
            logger.info("[TURNSTILE] Demo mode bypass active for token.")
            return {"success": True, "hostname": "localhost", "challenge_ts": "demo"}

        if not settings.SAFE_DEMO_MODE and secret_key.startswith("1x000000"):
            # Cloudflare's published dummy secret always passes; never accept it in strict mode.
            logger.error("[TURNSTILE] Strict mode but no real secret configured; failing closed.")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Turnstile is not configured.")

        payload = {
            "secret": secret_key,
            "response": token
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        async def _call() -> Dict[str, Any]:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(cls.VERIFY_URL, data=payload)
                if res.status_code >= 500:
                    raise httpx.HTTPError(f"Turnstile upstream {res.status_code}")
                return res.json()

        try:
            # Retry transient transport / 5xx failures only (never a definitive "success: false").
            data = await retry_async(_call, attempts=2, base_delay=0.2, retry_on=(httpx.HTTPError,))
        except (httpx.HTTPError, ValueError) as exc:
            logger.error(f"[TURNSTILE] Request to Cloudflare verification failed: {type(exc).__name__}")
            # Fail open in demo mode, fail closed in strict mode
            if settings.SAFE_DEMO_MODE:
                return {"success": True, "warning": "Turnstile unreachable in demo"}
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Turnstile verification service unreachable."
            )
        if not isinstance(data, dict) or not data.get("success"):
            logger.warning(f"[TURNSTILE] Verification failed: {data.get('error-codes') if isinstance(data, dict) else None}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cloudflare Turnstile CAPTCHA verification failed."
            )
        return data

turnstile_verifier = CloudflareTurnstileVerifier()
