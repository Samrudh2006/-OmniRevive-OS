import pytest
from backend.app.b2b.voice_agent import B2BVoiceDialogueEngine, VoiceDialogueTurnRequest
from backend.app.b2b.ptp_engine import PTPStore

def test_b2b_voice_gst_dispute_mutation():
    engine = B2BVoiceDialogueEngine()
    req = VoiceDialogueTurnRequest(
        call_session_id="call_mock_1",
        invoice_id="inv_enterprise_998",
        customer_speech_text="Sir invoice mein hamara GST number galat hai, correct GSTIN 29AABCU9603R1Z2 daal kar bhejiye.",
        invoice_amount=85000.0
    )
    resp = engine.process_customer_turn(req)
    
    assert resp.intent_detected == "GST_DISPUTE_RESOLUTION"
    assert resp.action_taken == "MUTATE_RAZORPAY_INVOICE"
    assert resp.invoice_mutated is True
    assert resp.mutation_proposal is not None
    assert resp.mutation_proposal.new_value == "29AABCU9603R1Z2"

def test_b2b_voice_promise_to_pay_registration(tmp_path):
    engine = B2BVoiceDialogueEngine()
    req = VoiceDialogueTurnRequest(
        call_session_id="call_mock_2",
        invoice_id="inv_enterprise_777",
        customer_speech_text="Haanji sir, accountant Friday ko aayega aur funds clear ho jayega 11 baje.",
        invoice_amount=85000.0
    )
    resp = engine.process_customer_turn(req)
    
    assert resp.intent_detected == "PROMISE_TO_PAY_COMMITMENT"
    assert resp.action_taken == "REGISTER_PTP_LOCK"
    assert resp.ptp_created is True
    assert resp.ptp_details is not None

def test_b2b_voice_dispute_human_escalation():
    engine = B2BVoiceDialogueEngine()
    req = VoiceDialogueTurnRequest(
        call_session_id="call_mock_3",
        invoice_id="inv_enterprise_666",
        customer_speech_text="Ye product bilkul kharaab tha, hum payment nahi denge aur lawyer se baat karenge.",
        invoice_amount=85000.0
    )
    resp = engine.process_customer_turn(req)
    
    assert resp.intent_detected == "COMMERCIAL_DISPUTE_ESCALATION"
    assert resp.action_taken == "ESCALATE_TO_HUMAN_CFO"
    assert resp.should_escalate_to_human is True
    assert resp.fsm_current_state == "ESCALATED"

def test_neural_voice_synthesis_get_and_cache():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)

    # 1. Synthesize text via GET
    res1 = client.get("/api/v1/b2b/voice/synthesize", params={"text": "Namaste Sir, Acme payment verify kar rahe hain.", "voice": "en-IN-NeerjaExpressiveNeural"})
    assert res1.status_code in [200, 502]
    if res1.status_code == 200:
        assert res1.headers["content-type"] == "audio/mpeg"
        assert len(res1.content) > 1000

        # 2. Re-synthesize identical text -> Must hit SHA-256 in-memory cache
        res2 = client.get("/api/v1/b2b/voice/synthesize", params={"text": "Namaste Sir, Acme payment verify kar rahe hain.", "voice": "en-IN-NeerjaExpressiveNeural"})
        assert res2.status_code == 200
        assert res2.headers["x-cache"] == "HIT"
        assert res2.content == res1.content

def test_neural_voice_synthesis_validation():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)

    # Empty text must return 400 Bad Request
    res = client.get("/api/v1/b2b/voice/synthesize", params={"text": "   "})
    assert res.status_code == 400

def test_b2b_voice_conversational_intents():
    engine = B2BVoiceDialogueEngine()

    # 1. Discount negotiation
    res_disc = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Bhai kuch discount mil sakta hai kya agar abhi payment karein?",
        invoice_amount=85000.0
    ))
    assert res_disc.intent_detected == "DISCOUNT_NEGOTIATION"
    assert "500" in res_disc.agent_speech_response

    # 2. Partial payment split
    res_split = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Hum abhi 40000 pay kar sakte hain aur remaining next week denge",
        invoice_amount=85000.0
    ))
    assert res_split.intent_detected == "PARTIAL_PAYMENT_SPLIT"
    assert "40,000" in res_split.agent_speech_response

    # 3. Callback request / Busy
    res_busy = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Main abhi client meeting mein hoon, baad mein call karo",
        invoice_amount=85000.0
    ))
    assert res_busy.intent_detected == "CALLBACK_REQUESTED"
    assert "disturb" in res_busy.agent_speech_response.lower()

    # 4. Identity inquiry
    res_who = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Hello, kaun bol raha hai? Kis company se call hai?",
        invoice_amount=85000.0
    ))
    assert res_who.intent_detected == "AGENT_IDENTITY_INQUIRY"
    assert "Razorpay" in res_who.agent_speech_response

    # 5. Dynamic day PTP extraction (e.g. Tuesday)
    res_ptp = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Haanji sir, hum Tuesday subah confirm payment clear kar denge",
        invoice_amount=85000.0
    ))
    assert res_ptp.intent_detected == "PROMISE_TO_PAY_COMMITMENT"
    assert "Tuesday" in res_ptp.agent_speech_response

def test_b2b_voice_casual_talk_and_general_knowledge():
    engine = B2BVoiceDialogueEngine()

    # 1. Casual well-being
    r1 = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Hello how are you doing today?",
        invoice_amount=85000.0
    ))
    assert r1.intent_detected == "CASUAL_WELL_BEING"
    assert "badhiya" in r1.agent_speech_response

    # 2. Humor / Joke
    r2 = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Tell me a funny joke",
        invoice_amount=85000.0
    ))
    assert r2.intent_detected == "CASUAL_HUMOR"
    assert "Haha" in r2.agent_speech_response

    # 3. Telugu casual inquiry
    r3 = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="bagunnava mawa, nuvvu evaru?",
        invoice_amount=85000.0
    ))
    assert r3.intent_detected == "TELUGU_IDENTITY_INQUIRY"
    assert "Neerja" in r3.agent_speech_response
    assert "Razorpay" in r3.agent_speech_response

    # 4. Website explanation
    r4 = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="What is this website about?",
        invoice_amount=85000.0
    ))
    assert r4.intent_detected == "PLATFORM_EXPLANATION"
    assert "RazorRevive" in r4.agent_speech_response

    # 5. General Knowledge
    r5 = engine.process_customer_turn(VoiceDialogueTurnRequest(
        customer_speech_text="Who is the Prime Minister of India?",
        invoice_amount=85000.0
    ))
    assert r5.intent_detected == "GENERAL_KNOWLEDGE"
    assert "Narendra Modi" in r5.agent_speech_response



