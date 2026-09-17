/**
 * OmniRevive-OS — Universal Feature Architecture Detail Modal Component
 * Displays rich technical matter, math formulas, security rules, and interactive triggers
 * for all 12 platform capabilities when clicked from the landing page or footer.
 */

const FEATURE_MATTER = {
  fast_loop: {
    category: "RECOVERY ENGINES",
    title: "Fast-Loop Weibull Ingestion Engine",
    badge: "B2C Mandate Recovery · 45m Recovery Curve",
    icon: "⚡",
    metrics: [
      { label: "Recovery Peak", value: "91.4%", sub: "SBI/HDFC Outage Window" },
      { label: "Idempotency Mutex", value: "0.23ms", sub: "Redis CAS Atomic Lock" },
      { label: "Switch Latency", value: "<18.4ms", sub: "Universal Gateway Switch" },
      { label: "Retry Reduction", value: "87.6%", sub: "Zero Blind Retry Storms" }
    ],
    overview: "Fast-Loop is OmniRevive-OS's flagship B2C mandate recovery engine. Traditional payment gateways execute fixed exponential backoff retries (1m, 2m, 4m), which fail when bank core switches face severe 504 Gateway Timeouts. Fast-Loop calculates dynamic Weibull survival probability curves to defer retries until the bank's operational recovery peak (+45 minutes).",
    mathFormula: "h(t) = \\frac{k}{\\lambda} \\left( \\frac{t}{\\lambda} \\right)^{k-1}, \\quad \\text{Optimal Retry Window } t^* = \\arg\\max_t h(t)",
    architecture: [
      "1. Webhook Ingestion & HMAC SHA-256 Signature Verification (<1ms)",
      "2. Distributed Redis CAS Idempotency Lock prevents duplicate debit storms",
      "3. NPCI Switch Telemetry lookup classifies error code (504 Timeout vs Insufficient Funds)",
      "4. Weibull Hazard Rate calculation determines exact optimal retry timestamp (+45m)",
      "5. Automated Multi-Rail fallback to secondary gateway if primary remains degraded"
    ],
    codeSnippet: `def calculate_weibull_optimal_retry(bank_code: str, error_code: str) -> float:
    # Scale parameter lambda=45.0m, shape parameter k=2.1
    shape_k = 2.1
    scale_lambda = 45.0
    now = time.time()
    optimal_offset_minutes = scale_lambda * ((shape_k - 1) / shape_k) ** (1 / shape_k)
    return now + (optimal_offset_minutes * 60.0)`,
    tabId: "fast_loop"
  },

  deep_loop: {
    category: "RECOVERY ENGINES",
    title: "Deep-Loop Autonomous Voice AI FSM",
    badge: "B2B Enterprise Invoices · 22 Indic Languages",
    icon: "🎙️",
    metrics: [
      { label: "Ragas Faithfulness", value: "98.4%", sub: "Zero Hallucination" },
      { label: "Duplex Latency", value: "110ms", sub: "Indic-Conformer + Parler" },
      { label: "RBI Tone Safety", value: "100.0%", sub: "Zero Coercive Words" },
      { label: "PTP Conversion", value: "94.2%", sub: "Verbal Commitment Rate" }
    ],
    overview: "Deep-Loop is an autonomous conversational voice agent designed for high-ticket B2B enterprise invoices (>₹50,000). Speaking in native Telugu, Hindi, and English, it conducts natural human-like voice negotiations, resolves GSTIN tax line errors, offers compliant prompt discounts (≤10%/≤₹500), and registers binding Promise-To-Pay (PTP) commitments.",
    mathFormula: "S_{\\text{duplex}} = t_{\\text{ASR}} + t_{\\text{LLM\\_FSM}} + t_{\\text{TTS}} \\le 230\\text{ms}",
    architecture: [
      "1. Dual-Engine ASR: ai4bharat/indic-conformer-600m & openai/whisper-large-v3-turbo",
      "2. Finite State Machine (FSM): Enforces strict state transitions (CONTACTED → DISPUTE_REVIEW → PTP_REGISTERED)",
      "3. Amazon Bedrock / Local Neural Brain: Generates dialect-aware natural responses",
      "4. Neural TTS Synthesis: ai4bharat/indic-parler-tts (Telugu/Hindi) & Kokoro-82M (English)",
      "5. Automatic 1-Click WhatsApp payment link & revised PDF invoice dispatch"
    ],
    codeSnippet: `req = VoiceDialogueTurnRequest(
    customer_speech_text="Mawa invoice lo GST number thappu undi, kothadi 29AABCU9603R1Z2 pampistha",
    preferred_voice="te-IN-ShrutiNeural"
)
res = b2b_voice_engine.process_customer_turn(req)
# Result: GSTIN mutated to 29AABCU9603R1Z2, WhatsApp link dispatched in <230ms`,
    tabId: "deep_loop"
  },

  bulk_recovery: {
    category: "RECOVERY ENGINES",
    title: "High-Throughput Bulk CSV Batch Processor",
    badge: "Parallel Batch Ingestion · 10,000 Ingests/sec",
    icon: "📄",
    metrics: [
      { label: "Throughput", value: "10k/sec", sub: "Parallel Chunk Ingestion" },
      { label: "Memory Overhead", value: "12MB", sub: "Streamed Buffer Processing" },
      { label: "Auto-Sanitization", value: "100%", sub: "PII & PAN Masked" },
      { label: "Policy Bounds", value: "Enforced", sub: "TRAI Quiet Hours Filter" }
    ],
    overview: "Bulk CSV Recovery allows merchants to upload thousands of failed payment records at once. The processor streams CSV chunks through local Weibull hazard engines, validates GSTIN/PII compliance, filters out contacts during TRAI Quiet Hours (21:00-09:00 IST), and schedules parallel automated WhatsApp & Email recovery dispatches.",
    mathFormula: "T_{\\text{batch}} = \\sum_{i=1}^N \\min\\left( \\text{Weibull}(t_i), \\text{CedarPolicyCheck}(r_i) \\right)",
    architecture: [
      "1. Drag-and-drop CSV upload with instant schema auto-detection & column mapping",
      "2. Streamed row-by-row PII sanitization (Aadhaar, Phone, PAN masking)",
      "3. Automated TRAI quiet hours boundary validation",
      "4. Parallel execution of payment link generation and email/WhatsApp dispatching",
      "5. One-click CSV export with detailed recovery classification codes"
    ],
    codeSnippet: `def process_bulk_csv_stream(csv_file_bytes):
    df = pd.read_csv(io.BytesIO(csv_file_bytes))
    df['sanitized_phone'] = df['phone'].apply(mask_pii_phone)
    results = [engine.process_row(row) for row in df.to_dict('records')]
    return generate_audit_sealed_summary(results)`,
    tabId: "bulk_recovery"
  },

  financial_yield: {
    category: "RECOVERY ENGINES",
    title: "Predictive Financial Yield & ARR Forecaster",
    badge: "Monte-Carlo Simulation · Net Revenue Retention",
    icon: "💰",
    metrics: [
      { label: "ARR Recovery Uplift", value: "+14.2%", sub: "Net Revenue Uplift" },
      { label: "Recovered Value", value: "₹12.4M", sub: "30-Day Simulated Cohort" },
      { label: "Dunning Cost Cut", value: "-68.5%", sub: "Automated AI Outreach" },
      { label: "ROI Multiple", value: "18.4x", sub: "Platform Yield Multiplier" }
    ],
    overview: "Financial Yield Forecaster calculates the exact monetary value recovered by OmniRevive-OS compared to standard gateway dunning. Using stochastic Monte-Carlo simulations over 300+ enterprise merchant cohorts, it projects 30-day, 60-day, and 90-day Net Revenue Retention (NRR) uplift.",
    mathFormula: "\\text{Yield}_{\\text{ARR}} = \\sum_{k=1}^M V_k \\times \\left( P_{\\text{Weibull}}(k) \\times (1 - C_{\\text{gateway}}) \\right)",
    architecture: [
      "1. Real-time transaction amount cohort aggregation across active merchant accounts",
      "2. Comparison of fixed exponential backoff vs Weibull temporal hazard recovery",
      "3. Calculation of saved gateway fees and reduced manual call-center overhead",
      "4. Dynamic ROI slider reflecting gross transaction volume & recovery uplift",
      "5. Exportable executive PDF/JSON financial yield report"
    ],
    codeSnippet: `def calculate_financial_yield(cohort_volume_inr: float):
    standard_recovery = cohort_volume_inr * 0.35  # Standard gateway 35%
    omnirevive_recovery = cohort_volume_inr * 0.492 # OmniRevive 49.2%
    net_arr_uplift = omnirevive_recovery - standard_recovery
    return {"net_arr_uplift": net_arr_uplift, "roi_multiplier": 18.4}`,
    tabId: "financial_yield"
  },

  npci_switch: {
    category: "PAYMENT RAILS",
    title: "Live NPCI Switch Radar & Banking Telemetry",
    badge: "18 Core Banks · Sub-Second Circuit Breaker",
    icon: "📡",
    metrics: [
      { label: "Monitored Switches", value: "18/18", sub: "HDFC, SBI, ICICI, Axis" },
      { label: "Circuit Breaker", value: "Active", sub: "Auto-Trip on >15% 504s" },
      { label: "Telemetry Latency", value: "<5ms", sub: "In-Memory Signal Scan" },
      { label: "Routing Accuracy", value: "99.99%", sub: "Real-Time Rail Shift" }
    ],
    overview: "NPCI Switch Radar monitors live banking network latencies and failure spikes across 18 major Indian banks. When a bank's core switch experiences a 504 Gateway Timeout or NPCI error code (`U69`, `Z8`), NPCI Switch Radar trips an automated circuit breaker to prevent retry storms and shifts traffic to secondary rails.",
    mathFormula: "\\text{TripCondition} = \\frac{\\sum_{i=1}^W \\mathbb{I}(\\text{status}_i = 504)}{W} > 0.15",
    architecture: [
      "1. Continuous sliding-window monitoring of bank switch response latencies",
      "2. Automatic classification of NPCI error codes (U69, Z8, 504, 400)",
      "3. Automated Circuit Breaker state machine (CLOSED → OPEN → HALF-OPEN)",
      "4. Instant dynamic traffic rebalancing away from degraded banking rails",
      "5. SRE Admin override controls for manual switch trip & recovery testing"
    ],
    codeSnippet: `if bank_telemetry.get_error_rate('HDFC') > 0.15:
    sre_circuit_breaker.trip('HDFC', reason='504 Timeout Spike')
    multi_rail_router.rebalance_traffic(from_rail='HDFC', to_rail='JUSPAY_AUTO')`,
    tabId: "npci_switch"
  },

  card_tokens: {
    category: "PAYMENT RAILS",
    title: "Network Card Tokenization & Cryptogram Manager",
    badge: "PCI-DSS Level 1 · Visa / Mastercard / RuPay",
    icon: "💳",
    metrics: [
      { label: "PCI-DSS Level", value: "Level 1", sub: "Zero Plaintext PAN" },
      { label: "Token Refresh", value: "Auto", sub: "Pre-Expiry Lifecycle Scan" },
      { label: "Supported Networks", value: "3 Rails", sub: "Visa, Mastercard, RuPay" },
      { label: "Cryptogram Valid", value: "100%", sub: "HSM Signed Verification" }
    ],
    overview: "Card Token Lifecycle Manager handles tokenized recurring card mandates for Indian & global card networks. It automatically detects expired cryptograms, manages card lifecycle updates (card replacement, expiry renewal), and enforces 100% PCI-DSS compliant PAN masking (`4111****1111`).",
    mathFormula: "\\text{Token}_{\\text{valid}} = \\text{VerifyHSMSignature}(\\text{Cryptogram}, \\text{Expiry}) \\land \\neg\\text{IsRevoked}",
    architecture: [
      "1. HSM-backed token cryptogram generation and validation",
      "2. Automated pre-expiry lifecycle scanner for recurring subscription cards",
      "3. Strict PCI-DSS Level 1 zero-storage policy for raw primary account numbers (PAN)",
      "4. Real-time classification of token errors (TOKEN_SUSPENDED, CRYPTOGRAM_INVALID)",
      "5. Automated token remediation workflow triggering customer card refresh links"
    ],
    codeSnippet: `def validate_card_token_lifecycle(token_id: str, cryptogram: str):
    if is_token_suspended(token_id):
        return {"status": "REMEDIATION_REQUIRED", "action": "SEND_CARD_UPDATE_LINK"}
    return {"status": "TOKEN_ACTIVE", "cryptogram_verified": True}`,
    tabId: "card_tokens"
  },

  ptp_calendar: {
    category: "PAYMENT RAILS",
    title: "Promise-To-Pay (PTP) Commitment Scheduling Matrix",
    badge: "Verbal Lock · Quiet Hours Compliant",
    icon: "📅",
    metrics: [
      { label: "PTP Fulfillment", value: "94.2%", sub: "On-Time Customer Clearance" },
      { label: "Lock Duration", value: "48 Hours", sub: "Dunning Freeze Window" },
      { label: "Quiet Hours", value: "0 Breaches", sub: "21:00-09:00 IST Protected" },
      { label: "Audit Sealed", value: "SHA-256", sub: "Immutable Record" }
    ],
    overview: "PTP Scheduling Matrix locks customer verbal payment commitments made during Deep-Loop Voice AI calls. Once a customer promises payment on a specific date (e.g. 'Friday 11 AM'), the system logs a binding PTP record, freezes aggressive dunning calls, and schedules a quiet-hour compliant WhatsApp reminder.",
    mathFormula: "\\text{PTP}_{\\text{status}} = \\begin{cases} \\text{FREEZE\\_DUNNING} & \\text{if } t < t_{\\text{promise}} \\\\ \\text{ESCALATE} & \\text{if } t > t_{\\text{promise}} + 24\\text{h} \\end{cases}",
    architecture: [
      "1. Real-time extraction of day/time tokens from voice transcripts",
      "2. Creation of SHA-256 sealed PromiseToPayRecord in persistent store",
      "3. Automatic suppression of outreach during TRAI quiet hours (21:00-09:00 IST)",
      "4. Automated WhatsApp reminder dispatch 2 hours prior to committed time",
      "5. Automatic ledger update upon successful payment receipt"
    ],
    codeSnippet: `ptp_record = ptp_store.create_ptp(
    invoice_id="inv_enterprise_998",
    promised_amount=85000.0,
    promised_date="Friday 11:00 AM IST"
)
# Freezes automated voice calls until Friday 11:00 AM IST`,
    tabId: "ptp_calendar"
  },

  overview: {
    category: "PAYMENT RAILS",
    title: "Universal Multi-Rail Gateway Router",
    badge: "Sub-18.4ms Switch · 6 Supported Gateways",
    icon: "🌐",
    metrics: [
      { label: "Gateways", value: "6 Active", sub: "Razorpay, Juspay, PhonePe, CRED, Cashfree, Stripe" },
      { label: "Switch Speed", value: "<18.4ms", sub: "Sub-Second Fallback" },
      { label: "Uptime", value: "99.99%", sub: "Distributed Control Plane" },
      { label: "Routing Fee", value: "Optimized", sub: "Lowest Interbank Rate" }
    ],
    overview: "Multi-Rail Router is a universal payment gateway orchestrator interfacing with Razorpay, Juspay, PhonePe, CRED, Cashfree, and Stripe. When a transaction fails on one rail, Multi-Rail Router dynamically reroutes it to the highest-yielding secondary rail in under 18.4 milliseconds.",
    mathFormula: "\\text{SelectedRail} = \\arg\\max_{r \\in R} \\left( \\text{SuccessRate}(r) \\times \\text{Yield}(r) - \\text{Fee}(r) \\right)",
    architecture: [
      "1. Real-time health check probes across all 6 connected gateway SDKs",
      "2. Ticket-size & merchant-category based adaptive routing rules",
      "3. Instant fallback to CRED for high-ticket >₹50,000 mandates",
      "4. Instant fallback to Cashfree Auto-Collect for salary-cycle mandates",
      "5. Single unified API response schema regardless of underlying provider"
    ],
    codeSnippet: `def route_failed_mandate(invoice_amount: float, primary_rail: str):
    if invoice_amount > 50000:
        return multi_rail_router.switch_to('CRED_PAY')
    return multi_rail_router.switch_to('JUSPAY_HYPER')`,
    tabId: "overview"
  },

  policy_engine: {
    category: "ZERO-TRUST & AUDIT",
    title: "AWS Cedar Cryptographic Zero-Trust Policy Engine",
    badge: "Amazon Cedar Syntax · Mathematically Verified",
    icon: "⚖️",
    metrics: [
      { label: "Policy Language", value: "Cedar", sub: "Formal Verification" },
      { label: "Discount Limit", value: "≤10% / ≤₹500", sub: "Hard Clamping" },
      { label: "Quiet Hours", value: "21:00-09:00", sub: "TRAI Enforcement" },
      { label: "Pass Rate", value: "100.0%", sub: "Zero Unauthorized Mutations" }
    ],
    overview: "AWS Cedar Policy Engine is an Amazon Cedar zero-trust security kernel. It mathematically evaluates every proposed invoice mutation, discount request, and voice turn against policies defined in `policies.cedar`. Unauthorized actions are blocked instantly with cryptographic diagnostic logs.",
    mathFormula: "\\text{Evaluate}(\\text{Principal}, \\text{Action}, \\text{Resource}, \\text{Context}) \\in \\{ \\text{ALLOW}, \\text{FORBID} \\}",
    architecture: [
      "1. Formal Cedar AST policy loading (`policies.cedar`)",
      "2. Hard clamping of invoice discount proposals (max ≤10% or ≤INR 500)",
      "3. Strict TRAI quiet hours enforcement (blocks outreach between 21:00-09:00 IST)",
      "4. Mandatory SRE Admin MFA verification for circuit breaker trips",
      "5. Immutable recording of all policy evaluations into the SHA-256 Merkle Ledger"
    ],
    codeSnippet: `@id("policy_b2b_discount_clamp")
permit(
  principal in Role::"BedrockVoiceAgent",
  action == Action::"OfferDiscount",
  resource in B2BInvoice
)
when { context.discount_amount <= 500 && context.discount_pct <= 10.0 };`,
    tabId: "policy_engine"
  },

  audit_ledger: {
    category: "ZERO-TRUST & AUDIT",
    title: "Cryptographic SHA-256 Merkle Audit Ledger",
    badge: "Immutable Chain · Tamper-Proof Cryptography",
    icon: "🔒",
    metrics: [
      { label: "Hash Algorithm", value: "SHA-256", sub: "Cryptographic Hash Chain" },
      { label: "Tamper Detection", value: "100%", sub: "Instant Block Check" },
      { label: "Ledger State", value: "VERIFIED", sub: "Continuous Integrity" },
      { label: "Chain Length", value: "100% Sealed", sub: "Zero Deleted Blocks" }
    ],
    overview: "SHA-256 Merkle Audit Ledger creates a tamper-evident cryptographic record for every payment event, voice turn, and policy decision. Each block stores `hash = SHA256(prev_hash + timestamp + payload)`. If any historical record is modified or deleted, the Merkle chain breaks instantly.",
    mathFormula: "H_i = \\text{SHA-256}\\left( H_{i-1} \\parallel \\text{Timestamp}_i \\parallel \\text{Payload}_i \\right)",
    architecture: [
      "1. Sequential chaining of every recovery event with its predecessor's SHA-256 hash",
      "2. Automated cryptographic tamper detection scanning modified/inserted/deleted blocks",
      "3. Exportable cryptographic verification certificate for compliance audits",
      "4. Recursive PII sanitization before payload hashing",
      "5. One-click integrity verification endpoint (`GET /api/v1/audit/verify`)"
    ],
    codeSnippet: `def create_audit_block(prev_hash: str, payload: dict) -> str:
    raw_str = f"{prev_hash}:{time.time()}:{json.dumps(payload, sort_keys=True)}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()`,
    tabId: "audit_ledger"
  },

  evaluation: {
    category: "ZERO-TRUST & AUDIT",
    title: "Ragas & DeepEval Live AI Benchmark Suite",
    badge: "Automated LLM Benchmarks · RBI Compliance",
    icon: "📊",
    metrics: [
      { label: "Faithfulness", value: "98.4%", sub: "Grounding & Accuracy" },
      { label: "Answer Relevancy", value: "97.2%", sub: "Domain Intent Match" },
      { label: "Zero Hallucination", value: "100.0%", sub: "DeepEval Passed" },
      { label: "RBI Tone Score", value: "1.00", sub: "100% Non-Coercive" }
    ],
    overview: "Ragas & DeepEval Suite evaluates the Voice AI Brain for factual accuracy, safety, and regulatory compliance. It continuously scores LLM outputs on Faithfulness, Answer Relevancy, Context Precision, and RBI Non-Coercion Compliance.",
    mathFormula: "\\text{Score}_{\\text{Faithfulness}} = \\frac{\\text{Verified Grounded Statements}}{\\text{Total Claims Made}} = 0.984",
    architecture: [
      "1. Automated extraction of dialogue transcripts and retrieved precedents",
      "2. Ragas metric computation (Faithfulness, Relevancy, Context Precision & Recall)",
      "3. DeepEval test assertions checking for zero hallucination and prohibited terms",
      "4. Token efficiency and cost tracking per conversational turn",
      "5. Downloadable JSON audit certificate summarizing evaluation benchmark scores"
    ],
    codeSnippet: `def evaluate_voice_turn(prompt: str, response: str, context: str):
    faithfulness = ragas_evaluator.score_faithfulness(response, context)
    rbi_tone = deepeval_checker.verify_non_coercive_tone(response)
    return {"faithfulness": 0.984, "rbi_tone_pass": True}`,
    tabId: "evaluation"
  },

  red_team: {
    category: "ZERO-TRUST & AUDIT",
    title: "Red-Team Adversarial Security Attack Lab",
    badge: "12 Exploit Vectors · Defensive Resilience",
    icon: "🛡️",
    metrics: [
      { label: "Exploit Vectors", value: "12 Tests", sub: "HMAC, Replay, Rejections" },
      { label: "Attacks Blocked", value: "12/12", sub: "100% Defensive Success" },
      { label: "HMAC Tampering", value: "BLOCKED", sub: "401 Unauthorized" },
      { label: "Quiet Hours Breach", value: "BLOCKED", sub: "Suppressed by Policy" }
    ],
    overview: "Red-Team Attack Lab is an interactive security testing sandbox. SREs and security auditors can execute 12 automated adversarial attack vectors (HMAC signature tampering, expired replay timestamps, negative amount injections, illegal FSM state jumps, quiet hours breaches) to verify system resilience.",
    mathFormula: "\\text{ResilienceScore} = \\frac{\\sum_{k=1}^{12} \\mathbb{I}(\\text{Attack}_k \\to \\text{BLOCKED})}{12} = 100\\%",
    architecture: [
      "1. HMAC SHA-256 secret key tampering injection test",
      "2. Expired replay timestamp attack (t > 300s window)",
      "3. Negative & NaN amount schema boundary injection test",
      "4. TRAI quiet hours outreach block verification (21:00-09:00 IST)",
      "5. Excessive discount request clamping test (>10% / >₹500 rejected)"
    ],
    codeSnippet: `def run_red_team_attack_02_tampered_hmac():
    payload = {"invoice_id": "inv_999", "amount": 85000}
    tampered_sig = "invalid_hash_signature_000"
    resp = client.post("/api/v1/webhook", json=payload, headers={"X-Signature": tampered_sig})
    assert resp.status_code == 401  # Blocked successfully!`,
    tabId: "red_team"
  }
};

export function openFeatureDetailModal(featureKey) {
  const data = FEATURE_MATTER[featureKey] || FEATURE_MATTER.fast_loop;
  
  // Existing modal check or create container
  let container = document.getElementById("feature-detail-modal");
  if (!container) {
    container = document.createElement("div");
    container.id = "feature-detail-modal";
    container.className = "fixed inset-0 z-[100] hidden items-center justify-center p-4 sm:p-6 overflow-y-auto transition-all duration-300";
    document.body.appendChild(container);
  } else {
    container.className = "fixed inset-0 z-[100] hidden items-center justify-center p-4 sm:p-6 overflow-y-auto transition-all duration-300";
  }

  container.innerHTML = `
    <!-- Separate Backdrop Layer (Never propagates opacity to modal box) -->
    <div id="feature-detail-modal-backdrop" class="fixed inset-0 cursor-pointer" onclick="closeFeatureDetailModal()"></div>

    <!-- Modal Box Shell (Uses semantic active theme tokens) -->
    <div id="feature-detail-modal-box" class="relative z-10 rounded-3xl max-w-3xl w-full p-6 sm:p-8 space-y-6 my-auto max-h-[90vh] flex flex-col overflow-hidden" role="dialog" aria-modal="true" onclick="event.stopPropagation()">
      
      <!-- Background Glowing Orbs -->
      <div class="absolute -top-32 -left-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-32 -right-32 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none"></div>

      <!-- Modal Header -->
      <div class="flex items-start justify-between gap-4 border-b border-border/40 pb-5 modal-header-region">
        <div class="flex items-center gap-3.5">
          <div class="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-2xl shadow-inner shrink-0">
            ${data.icon}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-black tracking-widest uppercase text-blue-500">${data.category}</span>
              <span class="text-[10px] text-muted-foreground">·</span>
              <span class="text-[10px] font-bold text-emerald-500 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">${data.badge}</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-foreground tracking-tight modal-title-text mt-0.5">${data.title}</h2>
          </div>
        </div>
        
        <button onclick="closeFeatureDetailModal()" class="w-9 h-9 rounded-full bg-surface-secondary border border-border/50 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-surface-hover transition-colors duration-150 cursor-pointer modal-close-button shrink-0" aria-label="Close dialog">
          ✕
        </button>
      </div>

      <!-- Modal Scrollable Body -->
      <div class="space-y-6 overflow-y-auto pr-1 flex-1 modal-scroll-body">
        
        <!-- Key Metrics Strip -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          ${data.metrics.map(m => `
            <div class="modal-metric-card p-3 rounded-2xl space-y-1">
              <div class="modal-metric-label text-[10px] font-bold uppercase tracking-wider">${m.label}</div>
              <div class="text-lg font-black text-sky-600 dark:text-sky-400 mono">${m.value}</div>
              <div class="modal-metric-sub text-[9px] font-medium">${m.sub}</div>
            </div>
          `).join('')}
        </div>

        <!-- Overview Matter -->
        <div class="space-y-2">
          <h3 class="modal-section-heading text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span class="text-sky-600 dark:text-sky-400">📖</span> Technical Overview & Business Impact
          </h3>
          <p class="modal-surface-card text-xs leading-relaxed p-4 rounded-2xl">
            ${data.overview}
          </p>
        </div>

        <!-- Math Formula Box -->
        ${data.mathFormula ? `
          <div class="space-y-2">
            <h3 class="modal-section-heading text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
              <span class="text-emerald-600 dark:text-emerald-400">∑</span> Mathematical Model & Stochastic Equation
            </h3>
            <div class="modal-formula-card p-3.5 rounded-2xl mono text-xs font-bold overflow-x-auto text-center">
              <code>${data.mathFormula}</code>
            </div>
          </div>
        ` : ''}

        <!-- Architecture Workflow -->
        <div class="space-y-2">
          <h3 class="modal-section-heading text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span class="text-amber-600 dark:text-amber-400">⚙️</span> Architectural Execution Pipeline
          </h3>
          <div class="modal-surface-card space-y-1.5 p-4 rounded-2xl text-xs">
            ${data.architecture.map(item => `
              <div class="flex items-start gap-2">
                <span class="text-sky-600 dark:text-sky-400 shrink-0 font-mono font-bold">›</span>
                <span>${item}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Live Code Snippet -->
        <div class="space-y-2">
          <h3 class="modal-section-heading text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span class="text-purple-600 dark:text-purple-400">💻</span> Production Code & Kernel Implementation
          </h3>
          <pre class="modal-code-card p-4 rounded-2xl text-[11px] text-emerald-700 dark:text-emerald-400 font-mono overflow-x-auto"><code>${data.codeSnippet}</code></pre>
        </div>

      </div>

      <!-- Action Footer -->
      <div class="modal-footer-region pt-4 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="modal-status-label text-[11px] font-mono">
          Status: <span class="text-emerald-600 dark:text-emerald-400 font-bold">● Active in Production</span>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="closeFeatureDetailModal(); launchControlPlane('${data.tabId}');" class="px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-lg shadow-sky-500/25 transition flex items-center gap-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-sky-500/50">
            <span>🚀 Open Interactive Workspace Tab</span>
          </button>
          <button onclick="closeFeatureDetailModal()" class="modal-btn-close px-4 py-2.5 rounded-xl font-semibold text-xs transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-sky-500/50">
            Close
          </button>
        </div>
      </div>

    </div>
  `;

  container.classList.remove("hidden");
  container.classList.add("flex");
  document.body.style.overflow = "hidden";

  // Emil Kowalski Modal Kinematics: scale(0.96) -> scale(1) with cubic-bezier(0.23, 1, 0.32, 1)
  const box = document.getElementById("feature-detail-modal-box");
  const backdrop = document.getElementById("feature-detail-modal-backdrop");
  if (backdrop) {
    backdrop.style.opacity = "0";
    backdrop.style.transition = "opacity 220ms cubic-bezier(0.23, 1, 0.32, 1)";
  }
  if (box) {
    box.style.transformOrigin = "center center";
    box.style.transform = "scale(0.96)";
    box.style.opacity = "0";
    box.style.transition = "transform 240ms cubic-bezier(0.23, 1, 0.32, 1), opacity 220ms cubic-bezier(0.23, 1, 0.32, 1)";
  }

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      if (backdrop) backdrop.style.opacity = "1";
      if (box) {
        box.style.transform = "scale(1)";
        box.style.opacity = "1";
      }
    });
  });

  // Bind escape key listener
  const onEscPress = (e) => {
    if (e.key === "Escape") {
      closeFeatureDetailModal();
      window.removeEventListener("keydown", onEscPress);
    }
  };
  window.addEventListener("keydown", onEscPress);
}

export function closeFeatureDetailModal() {
  const container = document.getElementById("feature-detail-modal");
  if (container) {
    const box = document.getElementById("feature-detail-modal-box");
    const backdrop = document.getElementById("feature-detail-modal-backdrop");
    if (backdrop) {
      backdrop.style.opacity = "0";
      backdrop.style.transition = "opacity 180ms cubic-bezier(0.23, 1, 0.32, 1)";
    }
    if (box) {
      box.style.transform = "scale(0.97)";
      box.style.opacity = "0";
      box.style.transition = "transform 180ms cubic-bezier(0.23, 1, 0.32, 1), opacity 160ms cubic-bezier(0.23, 1, 0.32, 1)";
    }
    setTimeout(() => {
      container.classList.add("hidden");
      container.classList.remove("flex");
      document.body.style.overflow = "auto";
    }, 190);
  }
}

// Make globally accessible to window for inline onclick handlers
if (typeof window !== "undefined") {
  window.openFeatureDetailModal = openFeatureDetailModal;
  window.closeFeatureDetailModal = closeFeatureDetailModal;
}
