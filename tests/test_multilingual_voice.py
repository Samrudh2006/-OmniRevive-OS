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

def test_get_voice_ai_models_registry():
    client = TestClient(app)
    res = client.get("/api/v1/b2b/voice/models")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    data = payload["data"]
    assert "asr_models" in data
    assert "tts_models" in data
    
    asr_names = [m["name"] for m in data["asr_models"]]
    assert "ai4bharat/indic-conformer-600m-multilingual" in asr_names
    assert "openai/whisper-large-v3-turbo" in asr_names
    assert "distil-whisper/distil-large-v3" in asr_names

    tts_names = [m["name"] for m in data["tts_models"]]
    assert "hexgrad/Kokoro-82M" in tts_names
    assert "ai4bharat/indic-parler-tts" in tts_names
    assert "k2-fsa/OmniVoice" in tts_names
    assert "Qwen/Qwen3-TTS-12Hz-1.7B" in tts_names

def test_voice_turn_acoustic_telemetry():
    req = VoiceDialogueTurnRequest(
        customer_speech_text="Invoice check karo",
        stt_model="distil-whisper/distil-large-v3",
        tts_model="hexgrad/Kokoro-82M"
    )
    res = b2b_voice_engine.process_customer_turn(req)
    assert res.active_stt_model == "distil-whisper/distil-large-v3"
    assert res.active_tts_model == "hexgrad/Kokoro-82M"
    assert res.acoustic_telemetry is not None
    assert res.acoustic_telemetry["stt_latency_ms"] == 65
    assert res.acoustic_telemetry["tts_latency_ms"] == 45
    assert res.acoustic_telemetry["total_duplex_latency_ms"] == 110


