import time
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter

router = APIRouter()

class CedarEvaluationPayload(BaseModel):
    principal: str = Field(default="Role::SRE_Admin")
    action: str = Field(default="Action::TripCircuitBreaker")
    resource: str = Field(default="BankingSwitch::SBI")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

@router.get("/aws/cedar/policies", tags=["AWS Zero-Trust Security"])
@router.get("/api/v1/aws/cedar/policies", tags=["AWS Zero-Trust Security"])
async def get_cedar_policies():
    """Returns active AWS Cedar formal zero-trust authorization policies."""
    from aws.cedar.cedar_engine import get_cedar_engine
    engine = get_cedar_engine()
    return {
        "success": True,
        "data": {
            "specification": "AWS Cedar v3.0",
            "policy_sha256": engine.policy_hash,
            "raw_policies": engine.raw_policies,
            "rule_count": 4,
            "enforcement_mode": "STRICT_ZERO_TRUST"
        },
        "timestamp": time.time()
    }

@router.post("/aws/cedar/evaluate", tags=["AWS Zero-Trust Security"])
@router.post("/api/v1/aws/cedar/evaluate", tags=["AWS Zero-Trust Security"])
async def evaluate_cedar_policy(payload: CedarEvaluationPayload):
    """Evaluates an access request against AWS Cedar formal security policies."""
    from aws.cedar.cedar_engine import get_cedar_engine
    engine = get_cedar_engine()
    result = engine.evaluate(
        principal=payload.principal,
        action=payload.action,
        resource=payload.resource,
        context=payload.context
    )
    return {
        "success": True,
        "data": result.to_dict(),
        "timestamp": time.time()
    }

@router.get("/aws/bedrock/status", tags=["AWS Generative AI"])
@router.get("/api/v1/aws/bedrock/status", tags=["AWS Generative AI"])
async def get_bedrock_status():
    """Returns current Amazon Bedrock foundation model configuration and telemetry."""
    from aws.bedrock.bedrock_client import get_bedrock_agent
    agent = get_bedrock_agent()
    return {
        "success": True,
        "data": {
            "foundation_model": agent.model_id,
            "target_region": agent.region,
            "is_live_aws": agent.is_live,
            "mode": "Live Amazon Bedrock" if agent.is_live else "Local Zero-Cost Emulated",
            "supported_actions": [
                "B2B_HINGLISH_VOICE_SYNTHESIS",
                "GSTIN_DISPUTE_EXTRACTION",
                "PROMISE_TO_PAY_COMMITMENT_PARSER"
            ]
        },
        "timestamp": time.time()
    }
