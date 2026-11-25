import hashlib
import hmac
from backend.app.config import settings
from backend.app.security import verify_razorpay_signature


def test_default_webhook_secret_is_not_the_published_mock_value():
    assert settings.RAZORPAY_WEBHOOK_SECRET != "whsec_mock_signature_test"
    assert len(settings.RAZORPAY_WEBHOOK_SECRET) >= 32


def test_signature_forged_with_old_public_default_is_rejected():
    payload = b'{"event":"payment.failed"}'
    forged = hmac.new(b"whsec_mock_signature_test", payload, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(payload, forged) is False


def test_signature_with_configured_secret_is_accepted():
    payload = b'{"event":"payment.failed"}'
    good = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(payload, good) is True
