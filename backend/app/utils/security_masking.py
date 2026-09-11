"""
RazorRevive-OS Security & Compliance Masking Utilities
Adheres to PCI-DSS v4.0, RBI PII guidelines, and NPCI Tokenization mandates.
Redacts card numbers (PAN), customer phone numbers, UPI VPAs, and Aadhaar numbers.
"""

import re
from typing import Optional, Dict, Any

# Regex patterns for sensitive fintech entities
PAN_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
PHONE_REGEX = re.compile(r'(?:\+?91[-\s]?)?[6-9]\d{9}\b')
UPI_VPA_REGEX = re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b')
AADHAAR_REGEX = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

def mask_pan(pan: str) -> str:
    """
    Masks a 16-digit PAN according to PCI-DSS Requirement 3.4.
    Preserves the first 4 and last 4 digits (e.g. 4111-XXXX-XXXX-1111).
    """
    digits_only = re.sub(r'\D', '', pan)
    if len(digits_only) < 12:
        return "****-****"
    return f"{digits_only[:4]}-XXXX-XXXX-{digits_only[-4:]}"

def mask_phone(phone: str) -> str:
    """
    Masks a 10-digit mobile number preserving +91 prefix and last 3 digits.
    Example: +91 98765 43210 -> +91 98*** **210
    """
    cleaned = re.sub(r'[\s\-]', '', phone)
    if cleaned.startswith('+91'):
        num = cleaned[3:]
        prefix = "+91 "
    elif cleaned.startswith('91') and len(cleaned) == 12:
        num = cleaned[2:]
        prefix = "+91 "
    else:
        num = cleaned
        prefix = ""

    if len(num) == 10:
        return f"{prefix}{num[:2]}*** **{num[-3:]}"
    return f"{prefix}*******{num[-3:] if len(num) >= 3 else ''}"

def mask_upi_vpa(vpa: str) -> str:
    """
    Masks a UPI VPA preserving initial 2 characters and domain handle.
    Example: rahul.verma@okaxis -> ra***@okaxis
    """
    if '@' not in vpa:
        return vpa
    user, handle = vpa.split('@', 1)
    if len(user) <= 2:
        masked_user = user[0] + "***" if user else "***"
    else:
        masked_user = user[:2] + "***"
    return f"{masked_user}@{handle}"

def mask_aadhaar(aadhaar: str) -> str:
    """
    Masks a 12-digit Aadhaar number per UIDAI mandate.
    Example: 1234 5678 9012 -> XXXX-XXXX-9012
    """
    digits_only = re.sub(r'\D', '', aadhaar)
    if len(digits_only) == 12:
        return f"XXXX-XXXX-{digits_only[-4:]}"
    return "XXXX-XXXX-XXXX"

def sanitize_audit_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively scans and redacts sensitive PII and PAN fields in JSON payloads
    prior to cryptographic ledger storage or UI rendering.
    """
    sanitized: Dict[str, Any] = {}
    for key, val in data.items():
        lower_key = key.lower()
        if isinstance(val, dict):
            sanitized[key] = sanitize_audit_payload(val)
        elif isinstance(val, str):
            if "card" in lower_key or "pan" in lower_key:
                sanitized[key] = mask_pan(val)
            elif "phone" in lower_key or "mobile" in lower_key:
                sanitized[key] = mask_phone(val)
            elif "vpa" in lower_key or "upi" in lower_key:
                sanitized[key] = mask_upi_vpa(val)
            elif "aadhaar" in lower_key or "uid" in lower_key:
                sanitized[key] = mask_aadhaar(val)
            else:
                sanitized[key] = val
        else:
            sanitized[key] = val
    return sanitized
