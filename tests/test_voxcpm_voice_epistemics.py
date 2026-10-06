"""
OmniRevive-OS :: VoxCPM Spoken Epistemics & Real-Time Streaming Test Suite
==========================================================================
Tests epistemic stance transitions, token streaming audio chunks,
sub-18ms full-duplex barge-in cut-off, and FastAPI route responses.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.b2b.voxcpm_streaming_engine import (
    EpistemicStateTracker,
    VoxCPMStreamingEngine,
    voxcpm_engine,
    EPISTEMIC_BACKCHANNELS
)

client = TestClient(app)

def test_epistemic_state_transitions():
    """Verify epistemic state tracker handles hesitation, resistance, and cooperation."""
    tracker = EpistemicStateTracker()
    assert tracker.customer_epistemic_stance == "NEUTRAL_INQUIRING"

    # 1. Uncertainty trigger
    res = tracker.update_epistemic_state("emo sir naku theliyadu konchem time ivvandi", acoustic_pause_ms=900.0)
    assert res["epistemic_stance"] == "UNCERTAIN_HESITANT"
    assert res["hesitation_score"] > 0.0
    assert res["recommended_backchannel"] == "HESITATION_SMOOTHER"

    # 2. Financial stress / resistance trigger
    res2 = tracker.update_epistemic_state("ippudu kudaradu paise nahi hain discount tagginchu")
    assert res2["epistemic_stance"] == "RESISTANT_FINANCIAL_STRESS"
    assert res2["recommended_backchannel"] == "EMPATHY_ESCALATE_DISCOUNT"

    # 3. Grounded cooperation trigger
    res3 = tracker.update_epistemic_state("ha sare gpay chesthanu send link")
    assert res3["epistemic_stance"] == "COOPERATIVE_GROUNDED"
    assert res3["recommended_backchannel"] == "STANDARD_ACK"


def test_voxcpm_speech_streaming_chunks():
    """Verify speech chunk generator yields 20ms frames @ 24kHz with TTFA < 45ms."""
    engine = VoxCPMStreamingEngine()
    chunks = list(engine.stream_speech_chunks(
        text_prompt="Namaskaram andi, payment link WhatsApp lo share chesamu.",
        lang_code="te-IN",
        epistemic_mode="AUTO"
    ))

    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert first_chunk["is_first_chunk"] is True
    assert first_chunk["time_to_first_audio_ms"] < 45.0  # TTFA budget
    assert first_chunk["sample_rate_hz"] == 24000
    assert first_chunk["frame_duration_ms"] == 20
    assert first_chunk["audio_pcm16_bytes_len"] == 480 * 2  # 16-bit PCM (2 bytes/sample)

    last_chunk = chunks[-1]
    assert last_chunk["is_final_chunk"] is True


def test_voxcpm_barge_in_cut_off():
    """Verify sub-18ms interruption cut-off."""
    engine = VoxCPMStreamingEngine()
    cutoff = engine.handle_barge_in_interruption()
    assert cutoff["status"] == "STREAM_CUTOFF_IMMEDIATE"
    assert cutoff["barge_in_latency_ms"] < 18.0
    assert cutoff["buffer_purged"] is True


def test_voxcpm_api_stream_endpoint():
    """Verify POST /api/v1/b2b/voice/voxcpm-stream returns chunks with valid envelope."""
    payload = {
        "text_prompt": "Namaste, aapka invoice payment switch timeout hua tha.",
        "lang_code": "hi-IN",
        "epistemic_mode": "AUTO"
    }
    response = client.post("/api/v1/b2b/voice/voxcpm-stream", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_chunks_streamed"] > 0
    assert data["data"]["time_to_first_audio_ms"] is not None


def test_voxcpm_api_barge_in_endpoint():
    """Verify POST /api/v1/b2b/voice/voxcpm-barge-in returns immediate cutoff status."""
    response = client.post("/api/v1/b2b/voice/voxcpm-barge-in")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "STREAM_CUTOFF_IMMEDIATE"


def test_voxcpm_api_epistemics_endpoint():
    """Verify POST /api/v1/b2b/voice/voxcpm-epistemics updates epistemic stance."""
    payload = {
        "user_utterance": "dekhenge kal baat karte hain abhi busy",
        "acoustic_pause_ms": 1200.0
    }
    response = client.post("/api/v1/b2b/voice/voxcpm-epistemics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["epistemic_stance"] in ["UNCERTAIN_HESITANT", "RESISTANT_FINANCIAL_STRESS"]
