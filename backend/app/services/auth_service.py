import hmac
import logging
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from backend.app.config import settings

logger = logging.getLogger("OmniRevive.Security.AuthService")

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
        required_role: Optional[str] = None,
        allow_demo: bool = True
    ) -> Tuple[bool, str, str]:
        """
        Validates whether the request is authorized using cryptographic constant-time equality.
        Returns: (is_authorized: bool, actor: str, mode: str)
        Raises HTTPException(401) or HTTPException(403) if unauthorized under strict mode.
        """
        provided_token = cls.extract_token_or_key(request)
        configured_sre_key = settings.API_AUTH_KEY
        configured_cfo_key = settings.CFO_AUTH_KEY
        tenant_keys = getattr(settings, "MERCHANT_TENANT_KEYS", {}) or {}

        # Valid credentials provided with constant-time comparison (no wildcard startswith)
        if provided_token:
            token_bytes = provided_token.encode("utf-8")
            if hmac.compare_digest(token_bytes, configured_cfo_key.encode("utf-8")):
                return True, "Role::CFO", "PRODUCTION"
            if hmac.compare_digest(token_bytes, configured_sre_key.encode("utf-8")):
                if required_role == "Role::CFO":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CFO executive role required for this operation."
                    )
                role = "Role::Finance_Officer" if required_role == "Role::Finance_Officer" else "Role::SRE_Admin"
                return True, role, "PRODUCTION"

            # Check tenant-scoped merchant keys in constant time
            for k, tenant_id in tenant_keys.items():
                if hmac.compare_digest(token_bytes, k.encode("utf-8")):
                    if required_role in ("Role::CFO", "Role::SRE_Admin"):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Tenant key does not hold required {required_role} privilege."
                        )
                    request.state.authorized_merchant_id = tenant_id
                    return True, f"Tenant::{tenant_id}", "PRODUCTION"

            # Invalid credentials explicitly provided -> reject with 403 Forbidden even in demo mode
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key or insufficient permissions for this operation."
            )

        # Safe Demo Mode fallback when no token is provided
        if settings.SAFE_DEMO_MODE and allow_demo:
            logger.info("[AUTH_SERVICE] Request permitted under SAFE_DEMO_MODE.")
            return True, "Role::Demo_Operator", "DEMO_MODE"

        # Strict Production Mode enforcement
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide valid X-API-Key or Authorization Bearer header."
        )

    @classmethod
    def resolve_authorized_tenant(
        cls,
        request: Request,
        requested_merchant_id: Optional[str] = None,
    ) -> Optional[str]:
        """Enforces tenant boundary isolation for tenant-scoped tokens."""
        bound_tenant = getattr(request.state, "authorized_merchant_id", None)
        if bound_tenant:
            if requested_merchant_id and requested_merchant_id != bound_tenant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cross-tenant access denied: caller is scoped to '{bound_tenant}'."
                )
            return bound_tenant
        return requested_merchant_id

auth_service = AuthenticationService()
