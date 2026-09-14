/**
 * OmniRevive-OS: 2026 Next-Gen Fintech Control Plane Landing Gateway
 * Universal AI Revenue Recovery Engine for Multi-Rail Indian Gateways
 */

export const landingGateway = {
  activeStep: 0,
  stepTimer: null,
  activeVoiceLang: 'telugu',

  // Architecture Hub Data Store (8 Satellite Nodes)
  architectureNodes: {
    weibull_retries: {
      title: "Weibull Hazard Dynamic Retries",
      subsystem: "Mathematical Failure Decay Engine",
      sla: "3.2ms Window Computation",
      badge: "Mathematical Invariant",
      icon: "📈",
      description: "Continuous Poisson & Weibull temporal hazard probability modeling that identifies the exact inflection point when downstream bank switches recover. Completely replaces blind exponential backoff that causes switch choking and rate-limit drops.",
      handledCodes: ["GATEWAY_504", "NPCI_TIMEOUT_91", "HDFC_DOWN_500", "BANK_SWITCH_DEGRADE"],
      codeSnippet: `// Weibull Hazard Rate Function
function calculateOptimalRetry(beta = 1.42, alpha = 45.0) {
  const t_optimal = alpha * Math.pow((beta - 1) / beta, 1 / beta);
  return { retryAt: "T+" + Math.round(t_optimal) + "m", confidence: "95.4%" };
}`,
      metrics: "78.39% Recovery Rate · ₹4.25L Recovered",
      workspaceTab: "analytics"
    },
    npci_switch: {
      title: "NPCI Switch Radar & UPI 2.0 Telemetry",
      subsystem: "Real-Time Switch Health Ingestion",
      sla: "Sub-50ms Polling & Telemetry",
      badge: "Multi-Rail Invariant",
      icon: "📡",
      description: "Live synthetic health probes and webhook telemetry monitoring 18 major Indian bank switches (HDFC, ICICI, SBI, Axis, Kotak) to prevent failed transaction routing during switch degradation.",
      handledCodes: ["NPCI_U16", "NPCI_U69", "UPI_LIMIT_EXCEEDED", "REMITTER_DOWN"],
      codeSnippet: `// NPCI Switch Health Resolver
const switchHealth = await npciRadar.evaluateSwitchCluster({
  banks: ["HDFC", "ICICI", "SBI"],
  degradationThreshold: 0.12,
  routeFallback: "DYNAMIC_UPI_LINK"
});`,
      metrics: "18 Bank Endpoints · 99.99% Uptime",
      workspaceTab: "npci_switch"
    },
    cedar_policy: {
      title: "AWS Cedar Zero-Trust Policy Gatekeeper",
      subsystem: "Deterministic Compliance Engine",
      sla: "0.28ms Sub-Millisecond Evaluation",
      badge: "Zero-Trust Invariant",
      icon: "⚖️",
      description: "Formally verified zero-trust rules enforce TRAI quiet hours (21:00-09:00 IST), maximum discount clamping (<=10%, <=500 INR), and non-coercive regulatory compliance. AI recommendations never bypass policy.",
      handledCodes: ["POLICY_QUIET_HOURS", "DISCOUNT_EXCEEDED", "MAX_ATTEMPTS_BREACH", "COERCIVE_OUTREACH"],
      codeSnippet: `// AWS Cedar Deterministic Policy Rule
permit(
  principal == Role::"RecoveryAgent",
  action == Action::"TriggerRecovery",
  resource == Payment::"FailedTransaction"
) when {
  context.time_ist.hour >= 9 && context.time_ist.hour < 21 &&
  context.discount_pct <= 10 && context.attempts < 3
};`,
      metrics: "100% Policy Pass · 0 Compliance Violations",
      workspaceTab: "policy_engine"
    },
    voice_fsm: {
      title: "Trilingual B2B Voice Dialogue FSM",
      subsystem: "Deep-Loop Conversational AI",
      sla: "180ms Turn Response (Telugu / Hindi / English)",
      badge: "Trilingual Engine",
      icon: "🎙️",
      description: "Autonomous multi-turn voice negotiation engine that extracts customer dispute intents, dynamically updates GSTIN invoice errors, and secures binding Promise-to-Pay (PTP) commitments.",
      handledCodes: ["INVOICE_DISPUTE_GST", "BILLING_MISMATCH", "PAYMENT_DEFERRED", "PARTIAL_DISPUTE"],
      codeSnippet: `// Trilingual Dialogue State Machine
const fsmState = await voiceAgent.processTurn({
  audioStream: rawPCM,
  detectedLanguage: "te-IN", // Telugu / Hindi / English
  currentIntent: "GST_NUMBER_CORRECTION",
  ptpCommitment: "2026-09-19T11:00:00+05:30"
});`,
      metrics: "3 Languages · 92.4% PTP Settlement Rate",
      workspaceTab: "deep_loop"
    },
    redis_cas: {
      title: "Redis CAS Distributed Idempotency Mutex",
      subsystem: "Zero Double-Debit Protection",
      sla: "0.23ms Atomic Mutex Gate",
      badge: "Concurrency Invariant",
      icon: "🔒",
      description: "Compare-And-Swap (CAS) distributed lock ensures high-frequency webhooks across 10,000 req/sec never trigger concurrent duplicate charges or double-debited accounts.",
      handledCodes: ["CONCURRENT_WEBHOOK", "DUPLICATE_RETRY", "RACE_CONDITION", "IDEMPOTENCY_COLLISION"],
      codeSnippet: `// Redis CAS Atomic Mutex Acquisition
const lockAcquired = await redis.set(
  \`idempotency:lock:\${paymentId}\`,
  traceId,
  "NX", "EX", 300 // 5-minute atomic lease
);
if (!lockAcquired) throw new DuplicateExecutionError();`,
      metrics: "0 Double-Debits · 10k Req/sec Scale",
      workspaceTab: "overview"
    },
    card_tokens: {
      title: "Card Token Lifecycle & Network COF Tokens",
      subsystem: "Card-on-File Cryptographic Refresh",
      sla: "1.4ms Token Health Assessment",
      badge: "PCI-DSS Invariant",
      icon: "💳",
      description: "Monitors RBI-mandated network token lifecycles (Visa, Mastercard, RuPay) and automatically triggers fresh cryptograms prior to recurring mandate execution to prevent recurring subscription drops.",
      handledCodes: ["COF_CRYPT_EXPIRED", "TOKEN_DEACTIVATED", "CARD_SUSPENDED", "MANDATE_FAIL_RB03"],
      codeSnippet: `// Network Token Cryptogram Validator
const tokenStatus = await cardTokenEngine.evaluateLifecycle({
  tokenRef: "tok_visa_98124912",
  expiryCheck: true,
  autoRefreshCryptogram: true
});`,
      metrics: "99.4% Token Readiness · Visa/Mastercard/RuPay",
      workspaceTab: "card_tokens"
    },
    merkle_ledger: {
      title: "Immutable SHA-256 Merkle Audit Ledger",
      subsystem: "Cryptographic Evidence Trail",
      sla: "Sequential Block Sealing",
      badge: "Cryptographic Invariant",
      icon: "📜",
      description: "Every webhook diagnosis, policy evaluation, discount mutation, and recovery execution is cryptographically hashed into a tamper-proof sequential Merkle chain for auditors and CFOs.",
      handledCodes: ["AUDIT_PROOF_GEN", "CHAIN_INTEGRITY_CHECK", "REGULATORY_EXPORT", "TAMPER_DETECT"],
      codeSnippet: `// Sequential Merkle Audit Block Sealing
const block = merkleLedger.sealBlock({
  traceId: "tr_9a12bc34",
  policyVerdict: "ALLOWED",
  prevBlockHash: "0000a4b9812e...",
  timestamp: Date.now()
});`,
      metrics: "100% Tamper Proof · Zero Unaudited Decisions",
      workspaceTab: "audit_ledger"
    },
    cfo_approval: {
      title: "CFO Executive Dual-Key Governance",
      subsystem: "High-Value Tax & Mutation Gate",
      sla: "Asynchronous Webhook & SMS Approval",
      badge: "Financial Governance",
      icon: "🏛️",
      description: "Automatic circuit breaker for tax ledger mutations and discount waivers exceeding ₹50,000 INR, requiring dual-key cryptographic sign-off before financial commitment.",
      handledCodes: ["HIGH_VALUE_GATE", "CFO_APPROVAL_REQUIRED", "TAX_MUTATION_HOLD", "DISCOUNT_OVERRIDE"],
      codeSnippet: `// CFO Executive Dual-Key Gatekeeper
if (invoiceValue > 50000) {
  await financialGovernance.requireDualKeySignOff({
    invoiceId: "inv_enterprise_998",
    cfoKey: "cfo_sig_77a912b",
    auditLogged: true
  });
}`,
      metrics: "₹50k+ Circuit Breaker · Dual-Key Signed",
      workspaceTab: "overview"
    }
  },

  // Sandbox failure scenario presets
  sandboxScenarios: {
    hdfc_504: {
      title: "HDFC Bank Timeout 504 (Weibull Hazard Retry)",
      amount: "₹2,499.00",
      customer: "Aarav Sharma (+91 98765 43210)",
      paymentId: "pay_HDFC_9A12BC34",
      error: "GATEWAY_TIMEOUT_504",
      confidence: "95.4%",
      decision: "Weibull Hazard Retry at T+45m (Optimal Inflection)",
      window: "45 mins (11:00:24 AM)",
      policy: "ALLOWED (TRAI Quiet Hours & Discount Guard Passed)"
    },
    upi_u16: {
      title: "UPI Insufficient Funds U16 (Salary-Date PTP Booking)",
      amount: "₹4,999.00",
      customer: "Priya Patel (+91 98112 34567)",
      paymentId: "pay_UPI_88KD109A",
      error: "NPCI_U16_INSUFFICIENT_FUNDS",
      confidence: "91.8%",
      decision: "Trilingual Voice Outreach -> PTP Booked for Salary Date",
      window: "5 Days (Fri 11:00 AM)",
      policy: "ALLOWED (Non-Coercive Outreach & WhatsApp Fallback)"
    },
    card_token: {
      title: "Card Token Cryptogram Expired (COF Auto-Refresh)",
      amount: "₹12,500.00",
      customer: "Karan Verma (+91 97654 32109)",
      paymentId: "pay_CARD_77LM0021",
      error: "COF_CRYPT_EXPIRED",
      confidence: "98.2%",
      decision: "Network Token Cryptogram Refreshed & Instant Re-dispatch",
      window: "Instant (<18.4ms)",
      policy: "ALLOWED (RBI Card Tokenization Compliance Verified)"
    },
    high_val_invoice: {
      title: "High-Value ₹85,000 GST Dispute (CFO Dual-Key Gate)",
      amount: "₹85,000.00",
      customer: "Acme Enterprise Pvt Ltd",
      paymentId: "inv_enterprise_998",
      error: "GST_INVOICE_DISPUTE",
      confidence: "88.6%",
      decision: "GSTIN Mutation Proposed -> Pending CFO Dual-Key Sign-off",
      window: "Approval Gated",
      policy: "APPROVAL_GATED (Invoice > ₹50,000 Threshold Breached)"
    }
  },

  init() {
    this.bindEvents();
    this.startDecisionTrailAutoReplay();
    this.initTypewriterEffect();
    this.initCardTiltInteractions();
    this.initScrollytelling();
  },

  bindEvents() {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeNodeDeepDive();
        const hud = document.getElementById("sre-hud-boot-overlay");
        if (hud && !hud.classList.contains("hidden")) {
          this.skipHudBoot();
        }
      }
    });
  },

  /**
   * Launch the full OmniRevive-OS Control Plane with a 1.2s SRE HUD Boot Sequence
   */
  launchControlPlane(targetTab = 'overview') {
    const landing = document.getElementById("landing-gateway-container");
    const appShell = document.getElementById("app-workspace-shell");
    const hud = document.getElementById("sre-hud-boot-overlay");

    this.closeNodeDeepDive();

    if (!hud) {
      if (landing) landing.classList.add("hidden");
      if (appShell) appShell.classList.remove("hidden");
      if (typeof window.switchNavTab === "function") window.switchNavTab(targetTab);
      return;
    }

    if (typeof window.playFintechAudio === "function") {
      window.playFintechAudio("success");
    }

    hud.classList.remove("hidden");
    hud.classList.add("flex");

    const steps = [
      { id: "hud-step-1", delay: 100 },
      { id: "hud-step-2", delay: 350 },
      { id: "hud-step-3", delay: 600 },
      { id: "hud-step-4", delay: 850 },
      { id: "hud-step-5", delay: 1100 }
    ];

    steps.forEach((step) => {
      setTimeout(() => {
        const el = document.getElementById(step.id);
        if (el) {
          el.classList.remove("opacity-20", "text-slate-500");
          el.classList.add("opacity-100", "text-emerald-400");
          const badge = el.querySelector(".hud-status-badge");
          if (badge) {
            badge.classList.remove("bg-slate-800", "text-slate-400");
            badge.classList.add("bg-emerald-500/20", "text-emerald-300", "border-emerald-500/40");
            badge.textContent = "LOCKED";
          }
        }
      }, step.delay);
    });

    setTimeout(() => {
      hud.classList.add("opacity-0");
      setTimeout(() => {
        hud.classList.add("hidden");
        hud.classList.remove("flex", "opacity-0");

        if (landing) landing.classList.add("hidden");
        if (appShell) appShell.classList.remove("hidden");

        const showcaseBtn = document.getElementById("header-showcase-btn");
        if (showcaseBtn) showcaseBtn.classList.remove("hidden");

        window.scrollTo({ top: 0, behavior: "smooth" });

        if (typeof window.switchNavTab === "function") {
          window.switchNavTab(targetTab);
        }

        if (typeof window.renderWeibullCurve === "function") {
          window.renderWeibullCurve();
        }
      }, 300);
    }, 1350);
  },

  skipHudBoot() {
    const landing = document.getElementById("landing-gateway-container");
    const appShell = document.getElementById("app-workspace-shell");
    const hud = document.getElementById("sre-hud-boot-overlay");

    if (hud) {
      hud.classList.add("hidden");
      hud.classList.remove("flex");
    }
    if (landing) landing.classList.add("hidden");
    if (appShell) appShell.classList.remove("hidden");

    const showcaseBtn = document.getElementById("header-showcase-btn");
    if (showcaseBtn) showcaseBtn.classList.remove("hidden");
  },

  returnToShowcase() {
    const landing = document.getElementById("landing-gateway-container");
    const appShell = document.getElementById("app-workspace-shell");

    if (appShell) appShell.classList.add("hidden");
    if (landing) {
      landing.classList.remove("hidden");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  },

  /**
   * Orbital Constellation: Open Deep-Dive Drawer / Modal ("Click to know more")
   */
  openNodeDeepDive(nodeKey) {
    const data = this.architectureNodes[nodeKey];
    if (!data) return;

    const modal = document.getElementById("architecture-node-modal");
    if (!modal) return;

    document.getElementById("modal-node-title").textContent = data.title;
    document.getElementById("modal-node-subsystem").textContent = data.subsystem;
    document.getElementById("modal-node-sla").textContent = data.sla;
    document.getElementById("modal-node-badge").textContent = data.badge;
    document.getElementById("modal-node-desc").textContent = data.description;
    document.getElementById("modal-node-metrics").textContent = data.metrics;
    document.getElementById("modal-node-code").textContent = data.codeSnippet;

    const codesContainer = document.getElementById("modal-node-codes");
    if (codesContainer) {
      codesContainer.innerHTML = data.handledCodes
        .map(c => `<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-sky-500/15 text-sky-400 border border-sky-500/30">${c}</span>`)
        .join("");
    }

    const launchBtn = document.getElementById("modal-node-launch-btn");
    if (launchBtn) {
      launchBtn.onclick = () => this.launchControlPlane(data.workspaceTab);
    }

    if (typeof window.playFintechAudio === "function") {
      window.playFintechAudio("click");
    }

    modal.classList.remove("hidden");
    modal.classList.add("flex");
  },

  closeNodeDeepDive() {
    const modal = document.getElementById("architecture-node-modal");
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  },

  /**
   * Live Interactive Failure-to-Recovery Sandbox on Landing Page
   */
  selectLandingScenario(scenarioKey) {
    const data = this.sandboxScenarios[scenarioKey];
    if (!data) return;

    const amtEl = document.getElementById("landing-sb-amount");
    const custEl = document.getElementById("landing-sb-customer");
    const payEl = document.getElementById("landing-sb-payid");
    const errEl = document.getElementById("landing-sb-error");
    const confEl = document.getElementById("landing-sb-conf");
    const decEl = document.getElementById("landing-sb-decision");
    const winEl = document.getElementById("landing-sb-window");
    const polEl = document.getElementById("landing-sb-policy");

    if (amtEl) amtEl.textContent = data.amount;
    if (custEl) custEl.textContent = data.customer;
    if (payEl) payEl.textContent = data.paymentId;
    if (errEl) errEl.textContent = data.error;
    if (confEl) confEl.textContent = data.confidence;
    if (decEl) decEl.textContent = data.decision;
    if (winEl) winEl.textContent = data.window;
    if (polEl) polEl.textContent = data.policy;

    const buttons = document.querySelectorAll("[id^='sb-chip-']");
    buttons.forEach(btn => {
      if (btn.id === `sb-chip-${scenarioKey}`) {
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
      } else {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
      }
    });

    if (typeof window.playFintechAudio === "function") {
      window.playFintechAudio("click");
    }

    const term = document.getElementById("landing-sandbox-terminal");
    if (term) {
      term.innerHTML = `<span class="text-slate-500">> Ready to simulate: ${data.title}</span>\n<span class="text-sky-400">> Click '⚡ Run Instant AI Recovery Simulation' to trigger live orchestration pipeline...</span>`;
    }
  },

  runLandingSandboxSimulation() {
    const term = document.getElementById("landing-sandbox-terminal");
    const progressSteps = document.querySelectorAll(".landing-sb-step");
    if (!term) return;

    if (typeof window.playFintechAudio === "function") {
      window.playFintechAudio("click");
    }

    term.innerHTML = `<span class="text-emerald-400">> [${new Date().toLocaleTimeString()}] INGESTION: Razorpay webhook payload received (HMAC SHA-256 VALIDATED)...</span>\n`;

    const logs = [
      { text: `> [${new Date().toLocaleTimeString()}] MUTEX: Redis CAS lock acquired (0.23ms) -> 0 double-debit guarantee sealed.`, delay: 300, step: 0 },
      { text: `> [${new Date().toLocaleTimeString()}] QDRANT: Matched 4 historical recovery precedents with cosine similarity 0.942.`, delay: 650, step: 1 },
      { text: `> [${new Date().toLocaleTimeString()}] WEIBULL: Hazard rate curve calculated -> Peak probability window at T+45min.`, delay: 1000, step: 2 },
      { text: `> [${new Date().toLocaleTimeString()}] CEDAR POLICY: Evaluated 8 regulatory invariants -> VERDICT: ALLOW (100% Compliant).`, delay: 1350, step: 3 },
      { text: `> [${new Date().toLocaleTimeString()}] ACTION DISPATCHED: Autonomous recovery pipeline executed in 18.4ms. Merkle Block sealed! 🚀`, delay: 1700, step: 4 }
    ];

    logs.forEach(log => {
      setTimeout(() => {
        term.innerHTML += `<span class="text-sky-300">${log.text}</span>\n`;
        term.scrollTop = term.scrollHeight;
        if (progressSteps[log.step]) {
          progressSteps[log.step].classList.remove("opacity-30", "bg-slate-800");
          progressSteps[log.step].classList.add("opacity-100", "bg-emerald-500/20", "text-emerald-300", "border-emerald-500/50");
        }
        if (log.step === 4 && typeof window.playFintechAudio === "function") {
          window.playFintechAudio("success");
          if (typeof window.confetti === "function") {
            window.confetti({ particleCount: 30, spread: 60, origin: { y: 0.8 } });
          }
        }
      }, log.delay);
    });
  },

  /**
   * Trilingual Voice Studio Demonstration
   */
  playLandingVoiceDemo(lang) {
    this.activeVoiceLang = lang;
    const transcripts = {
      telugu: {
        text: '"Mawa, invoice lo GST number thappu undi, kothadi 29AABCU9603R1Z2 pampistha, 19th September pay chestha."',
        intent: "GSTIN Error Disputed & PTP Booked (19 Sept 11:00 AM)",
        audioWave: "Active Voice Synthesis (Telugu / te-IN)",
        langName: "Telugu (తెలుగు)"
      },
      hindi: {
        text: '"Bhai, billing amount mein discount apply nahi hua. Discount theek karke bhej do, Friday ko payment confirm kar dunga."',
        intent: "Discount Waiver Claimed & PTP Confirmed (Friday 11:00 AM)",
        audioWave: "Active Voice Synthesis (Hindi / hi-IN)",
        langName: "Hindi (हिंदी)"
      },
      english: {
        text: '"Hi OmniRevive, we are updating our ERP vendor registration. Please re-route the payment link via Dynamic UPI."',
        intent: "Dynamic UPI Link Re-routed & Immediate Settlement",
        audioWave: "Active Voice Synthesis (Indian English / en-IN)",
        langName: "English (en-IN)"
      }
    };

    const data = transcripts[lang];
    if (!data) return;

    document.getElementById("landing-voice-transcript").textContent = data.text;
    document.getElementById("landing-voice-intent").textContent = data.intent;
    document.getElementById("landing-voice-status").textContent = data.audioWave;

    ["telugu", "hindi", "english"].forEach(l => {
      const btn = document.getElementById(`voice-lang-btn-${l}`);
      if (btn) {
        if (l === lang) {
          btn.className = "px-3 py-1 rounded-full text-xs font-bold bg-purple-600 text-white border border-purple-400 shadow-md transition";
        } else {
          btn.className = "px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 hover:text-white transition";
        }
      }
    });

    if (typeof window.playFintechAudio === "function") {
      window.playFintechAudio("click");
    }
  },

  /**
   * Interactive Decision Trail Replay Animation on Landing Hero
   */
  startDecisionTrailAutoReplay() {
    const totalSteps = 4;
    if (this.stepTimer) clearInterval(this.stepTimer);

    this.stepTimer = setInterval(() => {
      this.activeStep = (this.activeStep + 1) % totalSteps;
      this.updateDecisionTrailUI(this.activeStep);
    }, 2800);
  },

  selectDecisionTrailStep(stepIndex) {
    if (this.stepTimer) clearInterval(this.stepTimer);
    this.activeStep = stepIndex;
    this.updateDecisionTrailUI(stepIndex);
    this.startDecisionTrailAutoReplay();
  },

  updateDecisionTrailUI(stepIndex) {
    for (let i = 0; i < 4; i++) {
      const stepItem = document.getElementById(`landing-trail-step-${i}`);
      const stepDot = document.getElementById(`landing-trail-dot-${i}`);
      if (stepItem) {
        if (i === stepIndex) {
          stepItem.classList.add("border-sky-500", "bg-sky-500/10", "scale-[1.01]");
          stepItem.classList.remove("border-slate-200", "dark:border-[#142442]", "bg-transparent");
        } else {
          stepItem.classList.remove("border-sky-500", "bg-sky-500/10", "scale-[1.01]");
          stepItem.classList.add("border-slate-200", "dark:border-[#142442]", "bg-transparent");
        }
      }
      if (stepDot) {
        if (i === stepIndex) {
          stepDot.classList.add("bg-sky-400", "ring-4", "ring-sky-400/20");
          stepDot.classList.remove("bg-slate-400");
        } else {
          stepDot.classList.remove("bg-sky-400", "ring-4", "ring-sky-400/20");
          stepDot.classList.add("bg-slate-400");
        }
      }
    }
  },

  /**
   * Typewriter Letter-by-Letter Animation for Hero Headline
   */
  typewriterIndex: 0,
  typewriterCharIndex: 0,
  typewriterIsDeleting: false,
  typewriterTimer: null,
  typewriterPhrases: [
    "Recover the Lost 0.1% GMV Across India's Payment Rails",
    "Weibull Temporal Hazard Windows for Intelligent Retries",
    "Sub-Millisecond Zero-Trust AWS Cedar Policy Gatekeeper",
    "Trilingual Autonomous B2B Voice Dispute Resolution FSM",
    "Sequential SHA-256 Merkle Ledger Audit Trail Invariants",
    "0.23ms CAS Mutex Gate for Real-Time Multi-Rail Recovery"
  ],

  initTypewriterEffect() {
    const el = document.getElementById("hero-typewriter-text");
    if (!el) return;

    if (this.typewriterTimer) {
      clearTimeout(this.typewriterTimer);
      this.typewriterTimer = null;
    }

    // Initialize with full initial phrase
    this.typewriterIndex = 0;
    this.typewriterCharIndex = this.typewriterPhrases[0].length;
    this.typewriterIsDeleting = false;
    el.textContent = this.typewriterPhrases[0];

    const tick = () => {
      const currentPhrase = this.typewriterPhrases[this.typewriterIndex];
      if (this.typewriterIsDeleting) {
        this.typewriterCharIndex--;
        el.textContent = currentPhrase.substring(0, this.typewriterCharIndex);
      } else {
        this.typewriterCharIndex++;
        el.textContent = currentPhrase.substring(0, this.typewriterCharIndex);
      }

      let speed = this.typewriterIsDeleting ? 18 : 42;

      // Full phrase typed: give 3.2s generous reading time for humans
      if (!this.typewriterIsDeleting && this.typewriterCharIndex === currentPhrase.length) {
        speed = 3200;
        this.typewriterIsDeleting = true;
      } else if (this.typewriterIsDeleting && this.typewriterCharIndex === 0) {
        this.typewriterIsDeleting = false;
        this.typewriterIndex = (this.typewriterIndex + 1) % this.typewriterPhrases.length;
        speed = 450;
      }

      this.typewriterTimer = setTimeout(tick, speed);
    };

    // First wait 3200ms on the initial phrase so humans have comfortable time to read, then start animation
    this.typewriterTimer = setTimeout(() => {
      this.typewriterIsDeleting = true;
      tick();
    }, 3200);
  },

  selectWorkspaceMockupTab(tabKey) {
    const tabs = ["detect", "connect", "investigate", "decide"];
    tabs.forEach((t) => {
      const btn = document.getElementById(`ws-mockup-tab-${t}`);
      if (btn) {
        if (t === tabKey) {
          btn.className = "px-4 py-2 border-b-2 border-blue-500 text-blue-400 font-bold transition";
        } else {
          btn.className = "px-4 py-2 text-slate-400 hover:text-white font-medium transition";
        }
      }
    });
  },

  selectShowcaseTab(tabKey) {
    const tabs = ["monitoring", "voice", "policy", "ledger"];
    tabs.forEach((t) => {
      const btn = document.getElementById(`showcase-tab-${t}`);
      const panel = document.getElementById(`showcase-panel-${t}`);
      if (btn) {
        if (t === tabKey) {
          btn.className = "px-4 py-2 rounded-xl text-xs font-bold bg-sky-500/20 text-sky-300 border border-sky-500/40 transition cursor-pointer flex items-center gap-2 shadow-sm";
        } else {
          btn.className = "px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 text-slate-400 border border-slate-800 hover:text-white transition cursor-pointer flex items-center gap-2";
        }
      }
      if (panel) {
        if (t === tabKey) {
          panel.classList.remove("hidden");
        } else {
          panel.classList.add("hidden");
        }
      }
    });
  },

  initCardTiltInteractions() {
    document.querySelectorAll(".tilt-card").forEach((card) => {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        card.style.setProperty("--mouse-x", `${(x / rect.width) * 100}%`);
        card.style.setProperty("--mouse-y", `${(y / rect.height) * 100}%`);
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)";
      });
    });
  },

  initScrollytelling() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("scrolly-visible");
            const curve = entry.target.querySelector(".self-drawing-curve");
            if (curve) {
              curve.style.animation = "none";
              curve.offsetHeight;
              curve.style.animation = "self-draw-stroke 2.8s cubic-bezier(0.16, 1, 0.3, 1) forwards";
            }
          }
        });
      },
      { threshold: 0.15 }
    );

    document.querySelectorAll("section[id^='showcase-']").forEach((sec) => {
      observer.observe(sec);
    });
  }
};

window.landingGateway = landingGateway;
window.launchControlPlane = (tab) => landingGateway.launchControlPlane(tab);
window.returnToShowcase = () => landingGateway.returnToShowcase();
window.selectDecisionTrailStep = (idx) => landingGateway.selectDecisionTrailStep(idx);
window.selectShowcaseTab = (key) => landingGateway.selectShowcaseTab(key);
window.selectWorkspaceMockupTab = (key) => landingGateway.selectWorkspaceMockupTab(key);
window.openNodeDeepDive = (node) => landingGateway.openNodeDeepDive(node);
window.closeNodeDeepDive = () => landingGateway.closeNodeDeepDive();
window.selectLandingScenario = (scen) => landingGateway.selectLandingScenario(scen);
window.runLandingSandboxSimulation = () => landingGateway.runLandingSandboxSimulation();
window.playLandingVoiceDemo = (lang) => landingGateway.playLandingVoiceDemo(lang);
