"""
OmniRevive-OS | Ed25519 Cryptographic Signer for CFO Dual-Key Approvals
Provides hardware-ready asymmetric Ed25519 signatures for high-ticket (>INR 50,000)
quarantine approvals and non-repudiation audit trails.
"""

from __future__ import annotations

import base64
import hmac
import json
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)


@dataclass(frozen=True)
class SignedCFOApproval:
    """Cryptographically signed CFO dual-key approval envelope."""

    approval_id: str
    entity_id: str
    amount_inr: float
    decision: str
    approver_id: str
    signed_at: float
    signature_b64: str
    public_key_b64: str


class CFOEd25519Signer:
    """Manages Ed25519 keypairs and canonical CFO approval signatures."""

    def __init__(self, private_key: Optional[Ed25519PrivateKey] = None):
        self._private_key = private_key or Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()

    @property
    def public_key_b64(self) -> str:
        raw = self._public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base64.b64encode(raw).decode("ascii")

    def export_private_key_pem(self) -> bytes:
        return self._private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        )

    @staticmethod
    def canonical_payload(
        approval_id: str,
        entity_id: str,
        amount_inr: float,
        decision: str,
        approver_id: str,
        signed_at: float,
    ) -> bytes:
        if not (math.isfinite(amount_inr) and math.isfinite(signed_at)):
            raise ValueError("amount_inr and signed_at must be finite numbers")
        body: Dict[str, Any] = {
            "approval_id": approval_id,
            "entity_id": entity_id,
            "amount_inr": round(float(amount_inr), 2),
            "decision": decision.upper(),
            "approver_id": approver_id,
            "signed_at": round(float(signed_at), 3),
        }
        return json.dumps(
            body, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")

    def sign_approval(
        self,
        approval_id: str,
        entity_id: str,
        amount_inr: float,
        decision: str,
        approver_id: str,
        signed_at: Optional[float] = None,
    ) -> SignedCFOApproval:
        if decision.upper() not in {"APPROVED", "REJECTED"}:
            raise ValueError("decision must be APPROVED or REJECTED")
        ts = signed_at if signed_at is not None else time.time()
        payload = self.canonical_payload(
            approval_id, entity_id, amount_inr, decision, approver_id, ts
        )
        sig = self._private_key.sign(payload)
        return SignedCFOApproval(
            approval_id=approval_id,
            entity_id=entity_id,
            amount_inr=round(float(amount_inr), 2),
            decision=decision.upper(),
            approver_id=approver_id,
            signed_at=round(float(ts), 3),
            signature_b64=base64.b64encode(sig).decode("ascii"),
            public_key_b64=self.public_key_b64,
        )

    @classmethod
    def verify_approval(
        cls,
        envelope: SignedCFOApproval,
        trusted_public_key_b64: Optional[str] = None,
    ) -> bool:
        """Verify Ed25519 signature, optionally pinning against a trusted CFO public key."""
        try:
            if trusted_public_key_b64 is not None and not hmac.compare_digest(
                envelope.public_key_b64, trusted_public_key_b64
            ):
                return False
            pub = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(envelope.public_key_b64)
            )
            sig = base64.b64decode(envelope.signature_b64)
            payload = cls.canonical_payload(
                envelope.approval_id,
                envelope.entity_id,
                envelope.amount_inr,
                envelope.decision,
                envelope.approver_id,
                envelope.signed_at,
            )
            pub.verify(sig, payload)
            return True
        except (InvalidSignature, ValueError):
            return False
