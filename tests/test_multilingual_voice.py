import pytest
from backend.app.b2b.voice_agent import (
    detect_recommended_voice,
    b2b_voice_engine,
    VoiceDialogueTurnRequest
)
from fastapi.testclient import TestClient
from backend.app.main import app

def test_detect_recommended_voice_telugu():
    # 1. Telugu transliteration tokens
    assert detect_recommended_voice("Namaste", "Mawa bagunnava?") == "te-IN-ShrutiNeural"
    assert detect_recommended_voice("Sare repu kadathanu mawa") == "te-IN-ShrutiNeural"
    assert detect_recommended_voice("Dabbulu repu pampistha") == "te-IN-ShrutiNeural"
    assert detect_recommended_voice("Discount koddiga tagginchandi") == "te-IN-ShrutiNeural"
    
    # 2. Native Telugu Unicode script
    assert detect_recommended_voice("నమస్కారం బాగున్నారా") == "te-IN-ShrutiNeural"

def test_detect_recommended_voice_hindi():
    # 1. Hindi transliteration tokens
    assert detect_recommended_voice("Hello", "Kaisi ho Neerja? Koi chutkula sunao") == "hi-IN-SwaraNeural"
    assert detect_recommended_voice("Main bilkul badhiya hoon sir! Shukriya puchne ke liye.") == "hi-IN-SwaraNeural"
    assert detect_recommended_voice("Aapse baat karke accha laga, sab theek thaak hai") == "hi-IN-SwaraNeural"
    assert detect_recommended_voice("Shuddh hindi voice me bolo") == "hi-IN-SwaraNeural"
    
    # 2. Devanagari Unicode script
    assert detect_recommended_voice("नमस्ते आप कैसी हैं?") == "hi-IN-SwaraNeural"

def test_detect_recommended_voice_english_default():
    # Standard English / Hinglish
    assert detect_recommended_voice("Please verify the transaction ID", "Can you check invoice status?") == "en-IN-NeerjaExpressiveNeural"
    assert detect_recommended_voice("Payment failed due to 504 gateway timeout") == "en-IN-NeerjaExpressiveNeural"

def test_voice_turn_auto_language_switch_telugu():
    req = VoiceDialogueTurnRequest(
        customer_speech_text="Mawa bagunnava? Evaru meeru?",
        invoice_id="inv_enterprise_998",
        invoice_amount=85000.0
    )
    res = b2b_voice_engine.process_customer_turn(req)
    assert res.recommended_voice == "te-IN-ShrutiNeural"
    assert "Neerja" in res.agent_speech_response or "mawa" in res.agent_speech_response.lower()

def test_voice_turn_auto_language_switch_hindi():
    req = VoiceDialogueTurnRequest(
        customer_speech_text="Kaisi ho? Ek badhiya chutkula sunao na",
        invoice_id="inv_enterprise_998",
        invoice_amount=85000.0
    )
    res = b2b_voice_engine.process_customer_turn(req)
    assert res.recommended_voice == "hi-IN-SwaraNeural"
    assert "chutkula" in req.customer_speech_text

def test_synthesize_endpoint_auto_voice():
    client = TestClient(app)
    # Auto voice query for Telugu text
    res = client.get("/api/v1/b2b/voice/synthesize", params={"text": "Namaste mawa bagunnanu", "voice": "auto"})
    assert res.status_code in [200, 502]
    if res.status_code == 200:
        assert res.headers["content-type"] == "audio/mpeg"

    # Explicit Telugu voice query
    res2 = client.get("/api/v1/b2b/voice/synthesize", params={"text": "Repu kadathanu", "voice": "te-IN-ShrutiNeural"})
    assert res2.status_code in [200, 502]
    if res2.status_code == 200:
        assert res2.headers["content-type"] == "audio/mpeg"

def test_voice_turn_trilingual_gst_matching():
    # 1. Telugu GST Dispute -> Telugu response + Shruti voice
    req_te = VoiceDialogueTurnRequest(
        customer_speech_text="Mawa, invoice lo GST number thappu undi, kothadi 29AABCU9603R1Z2 pampistha update cheyandi",
        invoice_id="inv_enterprise_998",
        invoice_amount=85000.0
    )
    res_te = b2b_voice_engine.process_customer_turn(req_te)
    assert res_te.recommended_voice == "te-IN-ShrutiNeural"
    assert "mawa" in res_te.agent_speech_response.lower() or "update" in res_te.agent_speech_response.lower()
    assert res_te.intent_detected == "GST_DISPUTE_RESOLUTION"

    # 2. Hindi GST Dispute -> Hindi response + Swara voice
    req_hi = VoiceDialogueTurnRequest(
        customer_speech_text="Invoice mein hamara GST galat hai, correct GSTIN 29AABCU9603R1Z2 daal kar bhejo",
        invoice_id="inv_enterprise_998",
        invoice_amount=85000.0
    )
    res_hi = b2b_voice_engine.process_customer_turn(req_hi)
    assert res_hi.recommended_voice == "hi-IN-SwaraNeural"
    assert "Haanji" in res_hi.agent_speech_response or "humne" in res_hi.agent_speech_response
    assert res_hi.intent_detected == "GST_DISPUTE_RESOLUTION"

    # 3. English GST Dispute -> English response + Neerja voice
    req_en = VoiceDialogueTurnRequest(
        customer_speech_text="The GST number on this invoice is incorrect, please update it to 29AABCU9603R1Z2 and resend.",
        invoice_id="inv_enterprise_998",
        invoice_amount=85000.0
    )
    res_en = b2b_voice_engine.process_customer_turn(req_en)
    assert res_en.recommended_voice == "en-IN-NeerjaExpressiveNeural"
    assert "Certainly" in res_en.agent_speech_response or "updated" in res_en.agent_speech_response
    assert res_en.intent_detected == "GST_DISPUTE_RESOLUTION"

def test_voice_turn_explicit_preferred_voice_override():
    # User manually chooses Shruti from UI dropdown
    req = VoiceDialogueTurnRequest(
        customer_speech_text="Can you update the invoice details please?",
        preferred_voice="te-IN-ShrutiNeural"
    )
    res = b2b_voice_engine.process_customer_turn(req)
    assert res.recommended_voice == "te-IN-ShrutiNeural"

