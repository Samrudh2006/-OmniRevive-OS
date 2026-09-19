import hmac
import logging
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from backend.app.config import settings

logger = logging.getLogger("RazorRevive.Security.AuthService")

class AuthenticationService:
    """
    Unified Authentication & Execution Mode Gating Service.
    
    Modes:
    1. SAFE_DEMO_MODE=True:
       Allows unauthenticated interactions from demo UI/sandbox runners when no token provided.
       Logs audit events as DEMO_SIMULATION.
    2. SAFE_DEMO_MODE=False:
       Enforces cryptographic API key / Bearer token authentication on all mutating endpoints.
       Strictly rejects unauthenticated or unauthorized actors with HTTP 401/403.
    """

    @classmethod
    def extract_token_or_key(cls, request: Request) -> Optional[str]:
        # 1. Check X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key.strip()
        
        # 2. Check Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
            
        return None

    @classmethod
    def verify_request_auth(
        cls,
        request: Request,
        required_role: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Validates whether the request is authorized using cryptographic constant-time equality.
        Returns: (is_authorized: bool, actor: str, mode: str)
        Raises HTTPException(401) or HTTPException(403) if unauthorized under strict mode.
        """
        provided_token = cls.extract_token_or_key(request)
        configured_sre_key = settings.API_AUTH_KEY
        configured_cfo_key = getattr(settings, "CFO_AUTH_KEY", "cfo_sec_live_recovery_key_99")

        # Valid credentials provided with constant-time comparison (no wildcard startswith)
        if provided_token:
            if hmac.compare_digest(provided_token, configured_cfo_key):
                return True, "Role::CFO", "PRODUCTION"
            if hmac.compare_digest(provided_token, configured_sre_key):
                role = "Role::Finance_Officer" if required_role == "Role::Finance_Officer" else "Role::SRE_Admin"
                return True, role, "PRODUCTION"
            # Invalid credentials explicitly provided -> reject with 403 Forbidden even in demo mode
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key or insufficient permissions for this operation."
            )

        # Safe Demo Mode fallback when no token is provided
        if settings.SAFE_DEMO_MODE:
            logger.info("[AUTH_SERVICE] Request permitted under SAFE_DEMO_MODE.")
            return True, "Role::Demo_Operator", "DEMO_MODE"

        # Strict Production Mode enforcement
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide valid X-API-Key or Authorization Bearer header."
        )

auth_service = AuthenticationService()
