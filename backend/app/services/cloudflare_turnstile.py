import logging
import httpx
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from backend.app.config import settings

logger = logging.getLogger("RazorRevive.Cloudflare.Turnstile")

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
        secret_key = getattr(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", "1x0000000000000000000000000000000AA")
        
        # In demo mode with dummy testing key, allow local bypass
        if settings.SAFE_DEMO_MODE and (not token or token.startswith("test_") or secret_key.startswith("1x000000")):
            logger.info("[TURNSTILE] Demo mode bypass active for token.")
            return {"success": True, "hostname": "localhost", "challenge_ts": "demo"}

        payload = {
            "secret": secret_key,
            "response": token
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        async with httpx.AsyncClient(timeout=4.0) as client:
            try:
                res = await client.post(cls.VERIFY_URL, data=payload)
                data = res.json()
                if not data.get("success"):
                    logger.warning(f"[TURNSTILE] Verification failed: {data.get('error-codes')}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cloudflare Turnstile CAPTCHA verification failed."
                    )
                return data
            except httpx.RequestError as exc:
                logger.error(f"[TURNSTILE] Request to Cloudflare verification failed: {exc}")
                # Fail open in demo mode, fail closed in strict mode
                if settings.SAFE_DEMO_MODE:
                    return {"success": True, "warning": "Turnstile unreachable in demo"}
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Turnstile verification service unreachable."
                )

turnstile_verifier = CloudflareTurnstileVerifier()
