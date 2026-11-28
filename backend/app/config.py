from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from typing import Dict, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "OmniRevive-OS"
    APP_VERSION: str = "1.2.0"
    ENVIRONMENT: str = "sandbox"
    DEBUG: bool = True
    DATABASE_PATH: str = "recovery_audit.db"
    
    # Universal Gateway Adapters (Juspay, Cashfree, PhonePe, CRED, Razorpay)
    DEFAULT_GATEWAY_PROVIDER: str = "universal_multi_rail"
    RAZORPAY_KEY_ID: str = "rzp_test_mock12345"
    RAZORPAY_KEY_SECRET: str = "mock_secret_key_12345"
    # No guessable default: a published fallback secret would let anyone forge webhooks. Set RAZORPAY_WEBHOOK_SECRET in the
    # environment; otherwise a random per-process value is used and every unsigned/forged webhook is rejected.
    RAZORPAY_WEBHOOK_SECRET: str = secrets.token_urlsafe(32)
    RAZORPAY_WEBHOOK_SECRET_PREVIOUS: Optional[str] = None
    WEBHOOK_REQUIRE_TIMESTAMP: bool = False
    MAX_WEBHOOK_BYTES: int = 1048576  # 1 MiB max webhook body size

    # Local Open-Source AI Engine (Zero External API Keys Required)
    AI_PROVIDER: str = "LOCAL_OPENSOURCE" # "LOCAL_OPENSOURCE" | "OLLAMA"
    LOCAL_MODEL_NAME: str = "OmniRevive-Embed-v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDED_AI_ENABLED: bool = True


    # Security & Execution Modes
    SAFE_DEMO_MODE: bool = True
    # No built-in default secret: set API_AUTH_KEY / CFO_AUTH_KEY in the environment.
    # Without them a random per-process key is generated, so nothing is guessable from the repo.
    API_AUTH_KEY: str = secrets.token_urlsafe(32)
    CFO_AUTH_KEY: str = secrets.token_urlsafe(32)
    # Optional mapping of tenant-scoped merchant API keys -> merchant_id (enforces cross-tenant isolation)
    MERCHANT_TENANT_KEYS: Dict[str, str] = {}
    CANONICAL_DOMAIN: str = "https://omnirevive-os.antideploy.com"
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "https://omnirevive-os.antideploy.com",
        "https://razorpay-target-0-1percent.onrender.com",
        "https://razorrevive-os.onrender.com"
    ]
    REDIS_URL: Optional[str] = None
    # Inbound request timeout (seconds). 0 disables. Streaming endpoints are exempt.
    REQUEST_TIMEOUT_SECONDS: float = 30.0

    MAX_RETRY_ATTEMPTS: int = 3
    MAX_DISCOUNT_PERCENT: float = 10.0
    MAX_DISCOUNT_AMOUNT_INR: float = 500.0
    HIGH_VALUE_THRESHOLD_INR: float = 50000.0
    HIGH_VALUE_CONFIDENCE_THRESHOLD: float = 0.85
    MIN_CONFIDENCE_THRESHOLD: float = 0.60
    
    # TRAI Quiet-Hours Enforcement
    ENABLE_TRAI_COMPLIANCE: bool = True
    TRAI_QUIET_START_HOUR_IST: int = 21 # 9:00 PM IST
    TRAI_QUIET_END_HOUR_IST: int = 9   # 9:00 AM IST

    def validate_production_readiness(self) -> list[str]:
        """Returns a list of warnings/blockers if running outside SAFE_DEMO_MODE."""
        issues: list[str] = []
        if not self.SAFE_DEMO_MODE:
            import os
            if not os.getenv("API_AUTH_KEY") or len(self.API_AUTH_KEY) < 16:
                issues.append("API_AUTH_KEY must be explicitly configured (>=16 chars) when SAFE_DEMO_MODE=False.")
            if not os.getenv("CFO_AUTH_KEY") or len(self.CFO_AUTH_KEY) < 16:
                issues.append("CFO_AUTH_KEY must be explicitly configured (>=16 chars) when SAFE_DEMO_MODE=False.")
            if not os.getenv("RAZORPAY_WEBHOOK_SECRET") or "mock" in self.RAZORPAY_WEBHOOK_SECRET.lower():
                issues.append("RAZORPAY_WEBHOOK_SECRET must be set to a production secret when SAFE_DEMO_MODE=False.")
        return issues

settings = Settings()
