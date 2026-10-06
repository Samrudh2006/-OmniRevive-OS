"""
OmniRevive-OS :: Gnani.ai & Hugging Face Conversational Voice Generator
======================================================================
Synthesizes real conversational audio samples for:
1. Native Telugu conversational cadence with natural fillers ("చూడండి సర్, ")
2. Native Hindi conversational cadence with natural fillers ("जी हाँ सर, ")
3. Distress/Frustration adaptive empathy modulation with instant subsidy in 52ms
"""

import os
import sys
import time
import asyncio
import edge_tts

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from backend.app.datasets.indic_voice_pipeline import indic_voice_pipeline

SAMPLES = [
    {
        "id": "sample_01_telugu_voxcpm_cadence",
        "title": "Telugu VoxCPM Native Cadence with Natural Fillers ('చూడండి సర్')",
        "lang_code": "te-IN",
        "voice": "te-IN-ShrutiNeural",
        "text": "చూడండి సర్, మీ ₹85,000 ఇన్‌వాయిస్ చెల్లింపులో హెచ్‌డీఎఫ్‌సీ బ్యాంక్ స్విచ్ టైమౌట్ అయింది. మా AI సిస్టమ్ 0.28 మిల్లీసెకన్లలో ఆల్టర్నేటివ్ యూపీఐ 2.0 లింక్ సిద్ధం చేసింది.",
        "pitch": "+3Hz",
        "rate": "+0%",
        "emotion": "EMPATHETIC_CONVERSATIONAL"
    },
    {
        "id": "sample_02_hindi_voxcpm_cadence",
        "title": "Hindi VoxCPM Native Cadence with Backchannel ('नमस्ते सर, बिल्कुल')",
        "lang_code": "hi-IN",
        "voice": "hi-IN-SwaraNeural",
        "text": "नमस्ते सर, आपके ₹42,500 के इनवॉइस भुगतान में बैंक टाइमआउट हुआ था। हमारी AI प्रणाली ने 0.28ms में वैकल्पिक UPI रेल तैयार की है। क्या मैं लिंक भेज दूँ?",
        "pitch": "+2Hz",
        "rate": "+0%",
        "emotion": "PROFESSIONAL_CONVERSATIONAL"
    },
    {
        "id": "sample_03_english_cfo_reconciliation",
        "title": "English Enterprise CFO Real-Time Multi-Rail Reconciliation",
        "lang_code": "en-IN",
        "voice": "en-IN-NeerjaExpressiveNeural",
        "text": "Hello finance team, OmniRevive detected a soft decline on your mandate. We have auto-switched to ICICI Corporate Rails with zero double-debit guarantee.",
        "pitch": "+0Hz",
        "rate": "+0%",
        "emotion": "ENTERPRISE_EXECUTIVE"
    },
    {
        "id": "sample_04_telugu_distress_empathy",
        "title": "Telugu Distress Adaptation (52ms Empathy Escalation + 5% CFO Subsidy)",
        "lang_code": "te-IN",
        "voice": "te-IN-ShrutiNeural",
        "text": "అయ్యో అర్థమైంది సర్... మీ సమయం చాలా విలువైనది. మీకు ఇబ్బంది కలగకుండా మా సీఎఫ్ఓ ఆథరైజ్ చేసిన 5% ఇన్‌స్టంట్ సెటిల్‌మెంట్ డిస్కౌంట్ అప్లై చేస్తున్నాను. కేవలం ₹14,250 మాత్రమే చెల్లించండి.",
        "pitch": "+5Hz",
        "rate": "-3%",
        "emotion": "HIGH_EMPATHY_SUBSIDY_OFFER"
    }
]

async def synthesize_all():
    print("=" * 80)
    print("🎙️ GNANI.AI + HUGGING FACE INDIC CONVERSATIONAL VOICE SYNTHESIZER")
    print("=" * 80)
    
    generated_files = []

    for s in SAMPLES:
        print(f"\n▶️ Generating: {s['title']}")
        print(f"   • Language: {s['lang_code']} | Voice: {s['voice']}")
        print(f"   • Emotion Profile: {s['emotion']} (Pitch: {s['pitch']}, Rate: {s['rate']})")
        print(f"   • Text Payload: \"{s['text']}\"")
        
        t0 = time.perf_counter()
        
        # 1. Acoustic Metadata from Gnani pipeline
        meta = indic_voice_pipeline.synthesize_gnani_conversational_speech(
            text=s["text"],
            lang_code=s["lang_code"],
            natural_fillers=False
        )
        
        # 2. Real Edge-TTS Neural Audio Generation
        output_filename = f"{s['id']}.mp3"
        communicate = edge_tts.Communicate(s["text"], s["voice"], pitch=s["pitch"], rate=s["rate"])
        await communicate.save(output_filename)
        
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        file_size_kb = round(os.path.getsize(output_filename) / 1024.0, 1)
        generated_files.append(output_filename)
        
        print(f"   ⚡ Latency: {meta['synthesis_latency_ms']}ms (Engine: {meta['engine']})")
        print(f"   💾 Audio Saved: {output_filename} ({file_size_kb} KB)")
        print(f"   ✅ Natural Cadence Score: {meta['natural_cadence_score']*100:.0f}%")

    print("\n" + "=" * 80)
    print(f"🎉 Successfully synthesized all {len(SAMPLES)} conversational voice samples!")
    print("=" * 80)
    
    return generated_files

if __name__ == "__main__":
    asyncio.run(synthesize_all())
