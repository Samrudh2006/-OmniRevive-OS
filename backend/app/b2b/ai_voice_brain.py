"""
OmniRevive-OS Intelligent Voice AI Brain (Zero-API-Key Edition)
================================================================
Sophisticated local intent classification + contextual response generation.
No external API calls required — works completely offline.
"""

import os
import re
import time
import logging
from typing import Optional, Dict, List

logger = logging.getLogger("RazorRevive.B2B.AIVoiceBrain")

# ---------------------------------------------------------------------------
# Intent taxonomy
# ---------------------------------------------------------------------------
INTENT_GST_ERROR        = "GST_ERROR"
INTENT_UTR_SHARED       = "UTR_SHARED"
INTENT_PTP_COMMIT       = "PTP_COMMIT"
INTENT_DISPUTE_LEGAL    = "DISPUTE_LEGAL"
INTENT_PARTIAL_PAY      = "PARTIAL_PAY"
INTENT_CALLBACK         = "CALLBACK_REQUEST"
INTENT_WHATSAPP_LINK    = "WHATSAPP_LINK"
INTENT_CANNOT_PAY       = "CANNOT_PAY"
INTENT_ACKNOWLEDGEMENT  = "ACKNOWLEDGEMENT"
INTENT_GREETING         = "GREETING"
INTENT_QUESTION_AMOUNT  = "QUESTION_AMOUNT"
INTENT_QUESTION_DETAILS = "QUESTION_DETAILS"
INTENT_DEFAULT          = "DEFAULT"

# ---------------------------------------------------------------------------
# Intent detection patterns — ordered by specificity
# ---------------------------------------------------------------------------
INTENT_PATTERNS: List[Dict] = [
    {
        "intent": INTENT_DISPUTE_LEGAL,
        "patterns": [
            r"\b(lawyer|court|fraud|cheating|defective|refund|police|legal|consumer forum)\b",
            r"\b(kharaab|dhoka|court lo|vakailu|nyayam|fraud chesaru)\b",
            r"\b(fraud hai|case karenge|court jaayenge|vakeel)\b",
        ]
    },
    {
        "intent": INTENT_UTR_SHARED,
        "patterns": [
            r"\b(UTR|NEFT|RTGS|IMPS|already paid|transfer kar diya|bhej diya|payment ho gaya|pay chesamu|dabbulu pampanu)\b",
            r"\b(payment done|transferred|sent|bheja|pampinchu)\b",
        ]
    },
    {
        "intent": INTENT_PTP_COMMIT,
        "patterns": [
            r"\b(will pay|friday|monday|tuesday|salary|payroll|next week|kal|parson|shukravar|somvar)\b",
            r"\b(11 am|morning|evening|saturday|roju|chesthamu|karenge|dunga|denge)\b",
            r"\b(promise|commit|pakka|zaroor|avunu pay|chestha)\b",
        ]
    },
    {
        "intent": INTENT_GST_ERROR,
        "patterns": [
            r"\b(gst|gstin|gstn|tax invoice|gst number|gst galat|gst thappu|gst update|gst correct|wrong gst)\b",
            r"\b(gstin mismatch|gst saripoladam|gst error|gst dispute|corrected invoice|revised invoice)\b",
        ]
    },
    {
        "intent": INTENT_PARTIAL_PAY,
        "patterns": [
            r"\b(partial|part payment|kuch pay|kontha ivadam|half|50%|installment|kistu)\b",
        ]
    },
    {
        "intent": INTENT_WHATSAPP_LINK,
        "patterns": [
            r"\b(whatsapp|link bhejo|link pampandi|payment link|upi link|qr code|qr)\b",
        ]
    },
    {
        "intent": INTENT_CALLBACK,
        "patterns": [
            r"\b(call back|baad mein|tarvata|later|busy|meeting mein|repu matladataanu)\b",
        ]
    },
    {
        "intent": INTENT_CANNOT_PAY,
        "patterns": [
            r"\b(cannot pay|can.t pay|no money|funds nahi|ledu|cheyaledu|cash crunch|paise ledu)\b",
        ]
    },
    {
        "intent": INTENT_QUESTION_AMOUNT,
        "patterns": [
            r"\b(kitna|amount|how much|total|invoice amount|balance due|pending amount|enta)\b",
        ]
    },
    {
        "intent": INTENT_QUESTION_DETAILS,
        "patterns": [
            r"\b(which invoice|invoice number|kaunsa invoice|invoice details|invoice lo emi)\b",
        ]
    },
    {
        "intent": INTENT_ACKNOWLEDGEMENT,
        "patterns": [
            r"^(ok|okay|theek|avunu|haan|yes|sure|alright|understood|got it|samajh gaya|arthamaindi|fine)[.!,]?$",
        ]
    },
    {
        "intent": INTENT_GREETING,
        "patterns": [
            r"\b(namaste|namaskar|hello|hi |good morning|good afternoon|namaskaram|vanakkam)\b",
        ]
    },
]

# ---------------------------------------------------------------------------
# Response corpus — 3 natural variants per intent per language
# ---------------------------------------------------------------------------
RESPONSES: Dict[str, Dict[str, List[str]]] = {

    INTENT_GST_ERROR: {
        "telugu": [
            "GSTIN mismatch arthamaindi andi. Memu correct GSTIN tho revised invoice 5 minutes lo WhatsApp lo pampistamu. Meeru confirm chesthe venuvante payment process cheyavachu.",
            "Meeru cheppindi correct andi. GSTIN update chesi revised invoice generate chesamu, WhatsApp lo link vastundi andi.",
            "Invoice lo GSTIN error fix chesamu andi. Revised invoice ready ga undi, WhatsApp lo receipt pampistamu.",
        ],
        "hindi": [
            "GSTIN mismatch samajh aa gaya sir. Hum correct GSTIN se revised invoice 5 minute mein WhatsApp pe bhej rahe hain.",
            "Bilkul sahi baat hai. GSTIN update karke revised invoice ready kar di, WhatsApp link abhi aayega.",
            "Invoice mein GSTIN error fix kar diya. Revised invoice aapke WhatsApp pe 2 minute mein aa jayegi.",
        ],
        "english": [
            "Completely understood. We've corrected the GSTIN and are generating a revised invoice. You'll receive it on WhatsApp within 5 minutes.",
            "The GSTIN mismatch is resolved on our end. A revised invoice is being dispatched to your WhatsApp right now.",
            "That GSTIN discrepancy is now fixed. The revised tax invoice will reach your WhatsApp in under 5 minutes.",
        ],
    },

    INTENT_UTR_SHARED: {
        "telugu": [
            "UTR number note chesukunnamu andi, dhanyavadamulu. Memu ippude bank reconciliation start chestamu. 2 business hours lo confirm chestamu.",
            "Payment confirmation receive chesamu andi. UTR verify chesi ledger lo update chestamu. Receipt email chestamu.",
            "Chala baaga undi andi! UTR memu bank tho verify chestamu, tavaraga settlement confirm chestamu.",
        ],
        "hindi": [
            "UTR number receive kar liya, bahut shukriya. Bank reconciliation abhi start, 2 business hours mein confirm ho jayega.",
            "Payment confirmation mil gayi sir. UTR verify karke ledger update ho jayega. Receipt jald hi milegi.",
            "Bahut achha sir! UTR bank se verify hoga aur settlement 2 hours mein confirm ho jayega.",
        ],
        "english": [
            "UTR received, thank you. We're initiating bank reconciliation now and will send a confirmation receipt within 2 business hours.",
            "Payment noted. We'll verify the UTR and update the ledger. Expect a settlement confirmation shortly.",
            "Excellent. Our reconciliation team will validate the UTR and close the invoice by end of day.",
        ],
    },

    INTENT_PTP_COMMIT: {
        "telugu": [
            "Chala baagundi andi! Adi Promise-to-Pay ga register chesamu. Meeru cheppina date ki reminder pampistamu andi.",
            "Sari andi, aa date ki PTP lock chesamu system lo. Oka day mundu WhatsApp reminder vastundi.",
            "Perfect andi! Date confirm chesamu, PTP audit chain lo seal chesamu. Automated reminder pampistamu.",
        ],
        "hindi": [
            "Bahut achha sir! Promise-to-Pay register kar liya. Uss date se ek din pehle WhatsApp reminder bhejenge.",
            "Theek hai ji, date lock kar di. Payment ke din reminder automatically aayega.",
            "Perfect! PTP confirmed. Ek din pehle reminder aur payment link bhi ready rahega.",
        ],
        "english": [
            "Wonderful! Promise-to-Pay has been logged. We'll send a reminder one day prior on WhatsApp with the payment link ready.",
            "Excellent. PTP registered. Expect a reminder the day before with the payment link active.",
            "Perfect, that date is confirmed and sealed in our audit chain. Reminder will be sent automatically.",
        ],
    },

    INTENT_DISPUTE_LEGAL: {
        "telugu": [
            "Arthamaindi andi. Memu Senior Accounts Director ki ippude escalate chestamu, varu meeku direct ga call chesi resolve chestharu.",
            "Mee concern note chesukunnamu andi. Senior accounts team ki escalation create chesamu, 24 hours lo executive contact chestharu.",
            "Samajhinnamu andi. Idi serious ga treat chestamu, Senior Director immediately inform avutadu.",
        ],
        "hindi": [
            "Aapki concern samajh mein aa gayi. Senior Accounts Director ke paas abhi escalate kar rahe hain, woh directly baat karenge.",
            "Note kar liya sir. Aapka case senior team ko transfer hua, 24 ghante mein executive contact karega.",
            "Samajh gaye. Is matter ko seriously lete hain, Senior Director aaj aapse baat karenge.",
        ],
        "english": [
            "We completely understand and take this seriously. Escalating to our Senior Accounts Director who will personally reach out today.",
            "Your concern has been noted and escalated. A dedicated resolution executive will contact you within 24 hours.",
            "This is being flagged as a priority dispute. Our Senior Director will personally call you to discuss resolution.",
        ],
    },

    INTENT_PARTIAL_PAY: {
        "telugu": [
            "Partial payment discuss cheyavachu andi! 50% ippude pay chesi remaining next month chesithe convenient ga untundi.",
            "Sari andi, partial payment option available undi. Kontha settle chesthe remaining ki flexible date fix cheyavachu.",
            "No problem andi! Initial payment chesthe invoice hold release avutundi, remaining ki time istamu.",
        ],
        "hindi": [
            "Bilkul sir, partial payment ka option hai. 50% abhi dein toh invoice hold release ho jaayegi.",
            "Theek hai, partial arrange ho sakta hai. Kuch amount abhi, baki ke liye flexible date.",
            "Haan, partial payment accept karein hum. Advance mein kuch amount aane se dono ke liye easy hoga.",
        ],
        "english": [
            "Absolutely. If you can settle 50% now, we'll release the invoice hold and set a flexible date for the balance.",
            "That's manageable. An initial payment gets the invoice moving, and we can schedule the remainder at your convenience.",
            "Partial settlement is available. A down payment now secures the arrangement and gives your team flexibility.",
        ],
    },

    INTENT_WHATSAPP_LINK: {
        "telugu": [
            "Ippude UPI payment link WhatsApp lo pampistamu andi. 2 minutes lo receive avutundi, click chesi pay cheyavachu.",
            "Link ippude pampistamu andi. Mee WhatsApp number confirm chesthe venuvante pampistamu.",
            "Dynamic UPI QR tho payment link generate chesamu, mee WhatsApp ki ippude vastundi.",
        ],
        "hindi": [
            "Abhi UPI payment link WhatsApp pe bhej rahe hain. 2 minute mein aayega, click karke pay karein.",
            "Link abhi bhej raha hoon! WhatsApp number confirm karein toh turant bhejta hoon.",
            "Dynamic UPI link ready, aapke WhatsApp pe abhi pohonch jaayega.",
        ],
        "english": [
            "Sending the UPI payment link to your WhatsApp right now. It should arrive within 2 minutes.",
            "Dynamic UPI link generated. Please confirm your WhatsApp number and it'll be dispatched immediately.",
            "Payment link is on its way. It's valid for 24 hours and supports all UPI apps and cards.",
        ],
    },

    INTENT_CALLBACK: {
        "telugu": [
            "Sari andi, mee convenient time ki callback schedule chestamu. Evening ki call chesthamu.",
            "Okemanti andi, tarvata matladadam. Meeru time cheppandi, aa time ki call chestamu.",
            "Samajhinnamu andi. Evening 5 PM convenient ga untundaa callback ki?",
        ],
        "hindi": [
            "Bilkul sir, aapki convenient time pe callback schedule kar lete hain.",
            "Theek hai, baad mein baat karte hain. Kya evening 5 baje theek rahega?",
            "Koi baat nahi. Callback book kar liya. Aap apna time batayein.",
        ],
        "english": [
            "Absolutely, we'll schedule a callback at your convenience. Would evening 5 PM work?",
            "No problem at all. I'll book a callback — what time works best for you?",
            "Understood. Callback scheduled. Our team will reach you at your preferred time.",
        ],
    },

    INTENT_CANNOT_PAY: {
        "telugu": [
            "Arthamaindi andi, ippudu kashta situation. Chintinchakandi, oka small initial payment chesthe remaining ki 45 days extension istaamu.",
            "Okemanti andi, solutions untayi. Partial settlement chesthe rest ki flexible time istaamu.",
            "Samajhinnamu andi. Minimum amount tho start chesthe, full resolution ki flexible plan create chestamu.",
        ],
        "hindi": [
            "Hum samajhte hain sir. Ek chhota initial payment karein toh baki ke liye 45 din ka extension de sakte hain.",
            "Chinta mat karein. Thodi payment abhi karo, baaki ke liye flexible plan bana denge.",
            "Bilkul samajha. Minimum amount se shuru karein, baaki ke liye accommodate kar lenge.",
        ],
        "english": [
            "We understand cash flow challenges. A minimum payment now allows us to arrange a 45-day extension for the balance.",
            "Don't worry. A small initial amount protects your credit line and gives you more time for the balance.",
            "Hardship arrangements are available. A token payment now keeps the account current while we structure the rest.",
        ],
    },

    INTENT_QUESTION_AMOUNT: {
        "telugu": [
            "Invoice total rupees 85,000 undi andi, GST included ga. Ippude pay chesthe 2% early settlement discount available undi.",
            "Pending amount 85,000 rupees andi. UPI, NEFT, RTGS anni options available unnaayi.",
            "Total due 85,000 rupees. Partial payment chesithe kuda okemante undi.",
        ],
        "hindi": [
            "Invoice total 85,000 rupaye hai sir, GST included. Abhi pay karein toh 2% discount bhi mil sakta hai.",
            "Pending amount 85,000 rupaye hai. UPI, NEFT, RTGS koi bhi mode se pay karein.",
            "Total 85,000 rupaye due hai. Partial payment bhi accept hai.",
        ],
        "english": [
            "The outstanding invoice total is Rs 85,000 inclusive of GST. An early settlement discount of 2% is available today.",
            "Total due is Rs 85,000. Payment options include UPI, net banking, or NEFT transfer.",
            "The invoice balance is Rs 85,000. Partial payments are also accepted.",
        ],
    },

    INTENT_QUESTION_DETAILS: {
        "telugu": [
            "Invoice ID: INV-ENT-998, Amount: 85,000 rupees. GSTIN mismatch valla hold lo undi andi, memu fix chesamu.",
            "Adi Acme Enterprises invoice andi — GST correction tarvata release avutundi.",
            "Invoice details: INV-ENT-998, 85,000 rupees, vendor: Acme Enterprises. Updated invoice WhatsApp lo pampistamu.",
        ],
        "hindi": [
            "Invoice ID: INV-ENT-998, Amount: 85,000 rupaye. GSTIN mismatch ki wajah se hold tha, fix ho gaya.",
            "Yeh Acme Enterprises ka invoice hai. Updated version WhatsApp pe bhej rahe hain.",
            "Invoice INV-ENT-998, 85,000 rupaye. GST correction ke baad payment proceed ho sakti hai.",
        ],
        "english": [
            "Invoice INV-ENT-998 for Rs 85,000 from Acme Enterprises. The GSTIN has been corrected and the revised invoice is ready.",
            "This is invoice INV-ENT-998, Rs 85,000, GSTIN now corrected. Shall I send the revised invoice to your WhatsApp?",
            "Invoice INV-ENT-998, Rs 85,000 — fully corrected and ready for payment. I can dispatch to WhatsApp or email.",
        ],
    },

    INTENT_ACKNOWLEDGEMENT: {
        "telugu": [
            "Sari andi! Inkemi help kavali?",
            "Chala baagundi andi. Payment proceed cheyalanukuntunnara, link pampinchuma?",
            "Okemanti andi. Ready ga unnappudu cheppandi, process chestamu.",
        ],
        "hindi": [
            "Theek hai sir! Kuch aur help chahiye?",
            "Achha ji. Payment link chahte hain ya kuch aur?",
            "Bilkul. Jab ready ho payment ke liye, humein batayein.",
        ],
        "english": [
            "Perfect! Is there anything else I can help clarify?",
            "Great. When ready to proceed, just say the word and I'll send the payment link.",
            "Understood. Feel free to ask anything else about the invoice.",
        ],
    },

    INTENT_GREETING: {
        "telugu": [
            "Namaskaram andi! Nenu Shruti, OmniRevive accounts team nunchi. Mee Acme Enterprises invoice regarding matladutunnanu. Telugu, Hindi, ledu English lo matladavachu.",
            "Vanakkam andi! Shruti here, accounts department. 85,000 rupees invoice resolve cheydam ki call chesanu.",
            "Namaskaram! Mee invoice settlement ki help cheyavalani unnaanu andi.",
        ],
        "hindi": [
            "Namaste sir! Main Swara, OmniRevive accounts team se. Aapke invoice ke baare mein baat karne ke liye call kiya.",
            "Namaskar! Main Swara hoon, accounts se. 85,000 rupaye ke invoice ke liye call thi.",
            "Namaste! Invoice resolve karne mein madad ke liye main yahan hoon.",
        ],
        "english": [
            "Good day! I'm Neerja from OmniRevive Accounts, calling about the Rs 85,000 invoice. Do you have a moment?",
            "Hello! Neerja here. I can assist in Telugu, Hindi, or English. How may I help you today?",
            "Hi there! I'm Neerja, calling about invoice INV-ENT-998. Let's find the quickest resolution together.",
        ],
    },

    INTENT_DEFAULT: {
        "telugu": [
            "Arthamaindi andi. Mee issue resolve cheyadam ki ready ga unnamu. GST, payment link, ledu PTP — emi kavali cheppandi.",
            "Sari andi, help cheyadam ki ikkade unnaanu. Invoice payment, WhatsApp link, ledu callback — choose cheyandi.",
            "Samajhinnamu andi. Best option choose cheddamu — UPI link, partial payment, ledu extended deadline.",
        ],
        "hindi": [
            "Samajh gaye sir. Aapki samasya solve karne ke liye hum yahan hain. GST correction, payment link, ya PTP — batayein.",
            "Bilkul, madad ke liye tayyar hain. Kuch bhi ho, batayein.",
            "Theek hai sir. Partial payment, extension, ya abhi UPI se settle — aap decide karein.",
        ],
        "english": [
            "Understood. We're here to find the best resolution — GST correction, payment link, installment plan, or callback.",
            "No problem. I can assist with invoice corrections, payment links, Promise-to-Pay, or a callback at your convenience.",
            "Of course. Let's work this out. Would payment today or a scheduled follow-up be more convenient?",
        ],
    },
}


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------
def detect_intent(user_speech: str) -> str:
    text = user_speech.strip().lower()
    for rule in INTENT_PATTERNS:
        for pat in rule["patterns"]:
            if re.search(pat, text, re.IGNORECASE):
                return rule["intent"]
    return INTENT_DEFAULT


# ---------------------------------------------------------------------------
# Language normalization
# ---------------------------------------------------------------------------
def normalize_lang(lang: str) -> str:
    if not lang:
        return "english"
    lang = lang.lower()
    if "te" in lang or "telugu" in lang or "shruti" in lang:
        return "telugu"
    if "hi" in lang or "hindi" in lang or "swara" in lang or "hinglish" in lang:
        return "hindi"
    return "english"


# ---------------------------------------------------------------------------
# Main response generator
# ---------------------------------------------------------------------------
_response_counters: Dict[str, int] = {}


def get_best_ai_response(
    user_speech: str,
    lang: str,
    invoice_amount: float = 85000.0,
    invoice_id: str = "inv_enterprise_998",
) -> Optional[str]:
    """
    Returns a contextually appropriate, natural response.
    Rotates through variants per intent to avoid repetition.
    Always returns a string — never None.
    """
    norm_lang = normalize_lang(lang)
    intent = detect_intent(user_speech)

    pool = RESPONSES.get(intent, RESPONSES[INTENT_DEFAULT]).get(
        norm_lang,
        RESPONSES.get(intent, RESPONSES[INTENT_DEFAULT]).get("english", [])
    )
    if not pool:
        pool = RESPONSES[INTENT_DEFAULT]["english"]

    # Rotate responses
    counter_key = f"{intent}:{norm_lang}"
    idx = _response_counters.get(counter_key, 0) % len(pool)
    _response_counters[counter_key] = idx + 1

    response = pool[idx]
    response = response.replace("85,000", f"{invoice_amount:,.0f}")
    response = response.replace("INV-ENT-998", invoice_id)

    logger.info(f"[AIVoiceBrain] intent={intent} lang={norm_lang} idx={idx}")
    return response


def detect_intent_for_audit(user_speech: str) -> str:
    return detect_intent(user_speech)
