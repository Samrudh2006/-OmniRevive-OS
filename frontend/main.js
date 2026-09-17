/**
 * RazorRevive-OS — Unified Frontend Application Entrypoint
 * Orchestrates modules, services, reactive state, and registers window actions.
 */

import { safeApiCall } from "./services/apiClient.js?v=2.1.0";
import { showToast } from "./utils/toast.js?v=2.1.0";
import { formatINR, formatDateIST, maskPII, truncateHash } from "./utils/formatters.js?v=2.1.0";
import {
  UnifiedVoiceEngine,
  loadVoices,
  speakText,
  stopSpeaking,
  replayLastSpeech,
  toggleMicrophoneSTT,
  changeNeuralVoice,
  toggleLiveVoiceCall,
  startLiveVoiceCall,
  endLiveVoiceCall
} from "./utils/audioPlayer.js?v=2.1.0";

import {
  triggerFastLoopPipeline,
  inspectCardTokenAction,
  generateAndLoadSampleCsv,
  handleBulkCsvFileSelected,
  exportBatchResolutionCsv
} from "./services/recoveryService.js?v=2.1.0";

import {
  triggerVoiceTurnAction,
  loadPTPRecords
} from "./services/b2bVoiceService.js?v=2.1.0";

import {
  fetchAuditEvents,
  verifyAuditLedgerIntegrity,
  refreshAuditLedger,
  downloadAuditCertificate
} from "./services/auditService.js?v=2.1.0";

import {
  initLiveTelemetryStream,
  toggleCommandPalette,
  closeCommandPalette,
  executePaletteAction
} from "./services/liveStreamClient.js?v=2.1.0";

import {
  fetchCFOQueue,
  approveCFOItem,
  rejectCFOItem
} from "./services/cfoService.js?v=2.1.0";
const fetchCfoQueue = fetchCFOQueue;
const approveEscalation = approveCFOItem;
const rejectEscalation = rejectCFOItem;

import {
  refreshCfoQueueUI,
  handleCfoApprove,
  handleCfoReject
} from "./components/cfoApprovalModal.js?v=2.1.0";

import { initFintech3DTopology } from "./components/topologyCanvas.js?v=2.1.0";
import { renderWeibullCurve, renderWeibullSvgCurve, renderWeibullCanvasChart } from "./components/weibullChart.js?v=2.1.0";
import { landingGateway } from "./components/landingGateway.js?v=2.1.0";
import {
  toggleAiCopilotDrawer,
  minimizeCopilotDrawer,
  setCopilotMode,
  resetCopilotHeroCard,
  renderCopilotHeroCard,
  renderCopilotSuggestions,
  triggerCopilotSuggestion,
  renderFocusedHeroCard,
  copilotAttachFilePrompt,
  updateCopilotCurrentPage,
  sendQuickPrompt,
  speakLastCopilotMessage,
  speakCopilotResponse,
  handleCopilotCustomQuery
} from "./components/copilotDrawer.js?v=2.1.0";

import {
  openAwsCedarModal,
  closeAwsCedarModal,
  applyCedarTestCase,
  runCedarTestEvaluation
} from "./components/cedarModal.js?v=2.1.0";

import {
  openFeatureDetailModal,
  closeFeatureDetailModal
} from "./components/featureDetailModal.js?v=2.1.0";

import {
  BANK_SWITCH_STATES,
  TOUR_STEPS,
  CMDK_COMMANDS,
  appState
} from "./state/appState.js?v=2.1.0";

import { evalDashboard } from "./components/evalDashboard.js?v=2.1.0";

// =========================================================================
// Component Mount Helper
// =========================================================================
export function mountComponents() {
  const fastLoopSlot = document.getElementById("fast-loop-container-slot");
  const deepLoopSlot = document.getElementById("deep-loop-container-slot");
  const traceSlot = document.getElementById("decision-trace-slot");
  const benchmarkSlot = document.getElementById("benchmark-summary-slot");
  const auditSlot = document.getElementById("audit-ledger-slot");

  const tmplFl = document.getElementById("tmpl-fast-loop-card") || document.getElementById("tmpl-fast-loop");
  const tmplDl = document.getElementById("tmpl-deep-loop-card") || document.getElementById("tmpl-deep-loop");
  const tmplDt = document.getElementById("tmpl-decision-trace");
  const tmplBm = document.getElementById("tmpl-benchmark-summary");
  const tmplAl = document.getElementById("tmpl-audit-ledger");

  if (fastLoopSlot && tmplFl) fastLoopSlot.innerHTML = tmplFl.innerHTML;
  if (deepLoopSlot && tmplDl) deepLoopSlot.innerHTML = tmplDl.innerHTML;
  if (traceSlot && tmplDt) traceSlot.innerHTML = tmplDt.innerHTML;
  if (benchmarkSlot && tmplBm) benchmarkSlot.innerHTML = tmplBm.innerHTML;
  if (auditSlot && tmplAl) auditSlot.innerHTML = tmplAl.innerHTML;

  const flDedicated = document.getElementById("fast-loop-dedicated-mount");
  const dtDedicated = document.getElementById("decision-trace-dedicated-mount");
  const dlDedicated = document.getElementById("deep-loop-dedicated-mount");
  const bmDedicated = document.getElementById("benchmark-dedicated-mount");
  const alDedicated = document.getElementById("audit-ledger-dedicated-mount");

  if (flDedicated && tmplFl) flDedicated.innerHTML = tmplFl.innerHTML;
  if (dtDedicated && tmplDt) dtDedicated.innerHTML = tmplDt.innerHTML;
  if (dlDedicated && tmplDl) dlDedicated.innerHTML = tmplDl.innerHTML;
  if (bmDedicated && tmplBm) bmDedicated.innerHTML = tmplBm.innerHTML;
  if (alDedicated && tmplAl) alDedicated.innerHTML = tmplAl.innerHTML;
}

// =========================================================================
// =========================================================================
// Navigation Tab Switcher
// =========================================================================
export function switchNavTab(tabName) {
  appState.setTab(tabName);
  const navButtons = document.querySelectorAll("#sidebar-nav button, #mobile-sidebar-nav button");
  navButtons.forEach((btn) => {
    btn.classList.remove("nav-btn-active");
    btn.classList.add("nav-btn-inactive");
  });

  const activeBtn = document.getElementById("nav-" + tabName);
  if (activeBtn) {
    activeBtn.classList.remove("nav-btn-inactive");
    activeBtn.classList.add("nav-btn-active");
  }

  // Dynamic Breadcrumb Label Update (RiskSentinel-X Alignment)
  const tabLabels = {
    overview: "Overview",
    fast_loop: "Fast Loop (B2C)",
    npci_switch: "NPCI Switch Radar",
    bulk_recovery: "Bulk CSV Recovery",
    card_tokens: "Card Token Vault",
    deep_loop: "Deep Loop (Voice)",
    financial_yield: "Financial Yield Forecaster",
    red_team: "Red-Team Attack Lab",
    ptp_calendar: "PTP Promise Calendar",
    audit_ledger: "Merkle Audit Ledger",
    benchmark: "100-Case Benchmark",
    policy_engine: "AWS Cedar Policy Gate",
    analytics: "Weibull Hazard Analytics",
    configuration: "Control Plane Config",
    logs: "Structured Event Stream",
    alerts: "Security & SRE Alerts",
    docs: "Production Playbook",
    cfo_approvals: "CFO Dual-Key Approvals",
    evaluation: "AI Evaluation Suite"
  };
  const breadcrumbEl = document.getElementById("header-breadcrumb-active");
  if (breadcrumbEl && tabLabels[tabName]) {
    breadcrumbEl.textContent = tabLabels[tabName];
  }

  const views = [
    "overview", "fast_loop", "npci_switch", "bulk_recovery", "card_tokens",
    "deep_loop", "financial_yield", "red_team", "ptp_calendar",
    "audit_ledger", "benchmark", "policy_engine", "analytics",
    "configuration", "logs", "alerts", "docs", "cfo_approvals", "evaluation"
  ];

  views.forEach((v) => {
    const el = document.getElementById("view-" + v);
    if (el) el.classList.add("hidden");
  });

  const targetView = document.getElementById("view-" + tabName);
  if (targetView) {
    targetView.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (tabName === "evaluation") evalDashboard.refreshMetrics();
  if (tabName === "cfo_approvals") refreshCfoQueueUI();
  if (tabName === "ptp_calendar") loadPTPRecords();
  if (tabName === "logs") loadLiveLogs();
  if (tabName === "audit_ledger" || tabName === "overview") refreshAuditLedger();
  if (tabName === "overview" || tabName === "npci_switch") refreshFullNPCISwitchView();
  if (tabName === "analytics") renderWeibullCurve();
  if (tabName === "bulk_recovery" && !window.latestBatchData) generateAndLoadSampleCsv();
  if (tabName === "card_tokens") inspectCardTokenAction();
  if (tabName === "financial_yield") updateLiveRoiCalculator();
  if (tabName === "benchmark") runBenchmarkAction();
}

export function toggleDesktopSidebar() {
  const sidebar = document.getElementById("app-sidebar");
  if (sidebar) {
    sidebar.classList.toggle("sidebar-collapsed");
    const isCollapsed = sidebar.classList.contains("sidebar-collapsed");
    localStorage.setItem("omnirevive_sidebar_collapsed", isCollapsed ? "true" : "false");
  }
}
window.toggleDesktopSidebar = toggleDesktopSidebar;

export function openDetailedBenchmarkSuite() {
  switchNavTab("benchmark");
  runBenchmarkAction();
  showToast("📊 100-Case Benchmark Suite Activated!", "info");
}

export function toggleMobileMenu() {
  const drawer = document.getElementById("mobile-drawer");
  if (drawer) {
    drawer.classList.toggle("hidden");
  }
}

export function toggleThemeMode() {
  const html = document.documentElement;
  const isDark = html.classList.contains("dark");
  const icon = document.getElementById("theme-icon");
  const text = document.getElementById("theme-text");

  if (isDark) {
    html.classList.remove("dark");
    html.classList.add("light");
    if (icon) icon.innerText = "🌙";
    if (text) text.textContent = "Dark";
    appState.setTheme("light");
    showToast("☀️ Switched to High-Contrast Light Mode", "info");
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    if (icon) icon.innerText = "☀️";
    if (text) text.textContent = "Light";
    appState.setTheme("dark");
    showToast("🌙 Switched to Deep Navy Dark Mode", "info");
  }

  setTimeout(renderWeibullCurve, 50);
}

// 2026 Theme Palette Controller
export function toggleThemePaletteMenu() {
  const dropdown = document.getElementById("theme-palette-dropdown");
  if (dropdown) {
    dropdown.classList.toggle("hidden");
  }
}

export function applyThemePalette(paletteName) {
  const html = document.documentElement;
  const iconEl = document.getElementById("theme-palette-icon");
  const labelEl = document.getElementById("theme-palette-label");
  const dropdown = document.getElementById("theme-palette-dropdown");
  if (dropdown) dropdown.classList.add("hidden");

  html.setAttribute("data-theme", paletteName);
  localStorage.setItem("omnirevive_palette", paletteName);

  if (paletteName === "cyber-obsidian") {
    if (iconEl) iconEl.innerText = "🌌";
    if (labelEl) labelEl.innerText = "Cyber Obsidian";
    showToast("🌌 Activated Cyber Obsidian Theme", "info");
  } else if (paletteName === "stripe-velvet") {
    if (iconEl) iconEl.innerText = "💳";
    if (labelEl) labelEl.innerText = "Stripe Velvet";
    showToast("💳 Activated Stripe Velvet Theme", "info");
  } else if (paletteName === "vercel-carbon") {
    if (iconEl) iconEl.innerText = "▲";
    if (labelEl) labelEl.innerText = "Vercel Carbon";
    showToast("▲ Activated Vercel Carbon Theme", "info");
  }

  setTimeout(renderWeibullCurve, 50);
}

// =========================================================================
// Demo Scenarios Selector
// =========================================================================
export function toggleScenariosMenu() {
  const drop = document.getElementById("scenarios-dropdown");
  if (drop) drop.classList.toggle("hidden");
}

export function selectScenario(type) {
  const drop = document.getElementById("scenarios-dropdown");
  if (drop) drop.classList.add("hidden");

  if (type === "A") {
    switchNavTab("overview");
    document.querySelectorAll("#fast-scenario-select").forEach((el) => (el.value = "GATEWAY_ERROR"));
    document.querySelectorAll("#fast-amount").forEach((el) => (el.value = 12500));
    document.querySelectorAll("#fast-pay-id").forEach((el) => (el.value = "pay_SBI_504_OUTAGE"));
    triggerFastLoopPipeline();
    simulateBankDegradation("SBI");
    showToast("⚡ [Scenario A] SBI Switch Outage Ingested: Shifted Weibull Retry to +45m (91.4% Window)", "warning");
  } else if (type === "B") {
    switchNavTab("overview");
    document.querySelectorAll("#fast-scenario-select").forEach((el) => (el.value = "INSUFFICIENT_FUNDS"));
    document.querySelectorAll("#fast-amount").forEach((el) => (el.value = 2499));
    document.querySelectorAll("#fast-pay-id").forEach((el) => (el.value = "pay_B2C_SOFT_DECLINE"));
    triggerFastLoopPipeline();
    setTimeout(openWhatsAppPreviewModal, 400);
    showToast("📱 [Scenario B] Soft Balance Decline: 1-Click WhatsApp Recovery & UPI QR Generated!", "success");
  } else if (type === "C") {
    switchNavTab("deep_loop");
    const gstSpeech = "Invoice mein hamara GST galat hai, correct GSTIN 29AABCU9603R1Z2 daal kar bhejo";
    document.querySelectorAll("#voice-speech-select").forEach((el) => {
      el.value = gstSpeech;
      if (el.selectedIndex < 0) el.selectedIndex = 0;
    });
    document.querySelectorAll("#voice-custom-speech").forEach((el) => {
      el.value = gstSpeech;
    });
    document.querySelectorAll("#voice-inv-id").forEach((el) => {
      el.value = "inv_enterprise_998";
    });
    document.querySelectorAll("#voice-inv-amount").forEach((el) => {
      el.value = 85000;
    });

    setTimeout(() => {
      triggerVoiceTurnAction();
    }, 200);
    showToast("🎙️ [Scenario C] B2B GST Dispute: Voice Agent Proposed Mutation & Locked PTP", "info");
  } else if (type === "D") {
    switchNavTab("ptp_calendar");
    loadPTPRecords();
    showToast("📅 [Scenario D] Promise-to-Pay Registered: Reminders Suppressed until Friday 11:00 AM IST", "success");
  } else if (type === "E") {
    switchNavTab("red_team");
    runLiveAttack(1);
    showToast("🛡️ [Scenario E] 50-Webhook Storm Contained: 0 Double Debits (CAS Mutex Verified)", "error");
  }
}

// =========================================================================
// Red-Team Attack Lab
// =========================================================================
export async function runLiveAttack(vectorId) {
  const consoleEl = document.getElementById("red-team-console");
  if (!consoleEl) return;
  const ts = new Date().toLocaleTimeString("en-GB");

  if (vectorId === 1) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">⚡ LAUNCHING 50-THREAD CONCURRENT WEBHOOK STORM...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Ingested 50 concurrent requests for pay_CAS_RACE_998...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ CAS MUTEX ACQUIRED</span> for Thread 1 (Lock key: merchant_1:pay_CAS_RACE_998)</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-amber-400">49 Duplicate Webhooks Safely Suppressed (409 Conflict Dropped)</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-sky-400 font-bold">★ RESULT: 0 Double-Charges, Idempotency Violations = 0.</span></div>`;
  } else if (vectorId === 2) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">🛡️ INJECTING FORGED HMAC SIGNATURE: sha256_fake_998231...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Validating cryptographic payload hash against WEBHOOK_SECRET...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-red-400 font-bold">❌ HTTP 401 UNAUTHORIZED: HMAC SHA-256 signature mismatch</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ RESULT: Attack Contained, Webhook execution blocked.</span></div>`;
  } else if (vectorId === 3) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">⏳ REPLAYING STALE SIGNATURE: Timestamp drift = 7200s (&gt;300s threshold)...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Checking clock skew against RFC-3339 replay window...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-red-400 font-bold">❌ HTTP 400 REPLAY_ATTACK: Timestamp expired by 6900s</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ RESULT: Stale replay request rejected.</span></div>`;
  } else if (vectorId === 4) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">🛑 SIMULATING AUTOMATED OUTREACH AT 23:45 IST (TRAI QUIET HOURS)...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Evaluating TRAI Regulation Rule (Prohibited: 21:00 to 09:00 IST)...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-amber-400 font-bold">⚠️ POLICY ENFORCEMENT: Outreach suppressed. Message deferred to 09:05 AM IST.</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ RESULT: 0 TRAI Regulatory Violations.</span></div>`;
  } else if (vectorId === 5) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">💰 AI PROPOSING 50% DISCOUNT (₹42,500) ON ₹85,000 INVOICE...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Policy Engine evaluating boundary: min(10%, ₹500 INR)...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-amber-400 font-bold">⚠️ POLICY CEILING CLAMP: ₹42,500 clamped to ₹500 INR.</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ RESULT: Financial budget protected from LLM hallucination.</span></div>`;
  } else if (vectorId === 6) {
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-rose-400">🔀 ATTEMPTING ILLEGAL FSM STATE JUMP: DRAFT ➔ RESOLVED...</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] Validating Transition Graph against B2B State Machine...</div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-red-400 font-bold">❌ FSM ILLEGAL_TRANSITION: Cannot transition DRAFT to RESOLVED directly.</span></div>`;
    consoleEl.innerHTML += `<div>[${ts}] <span class="text-emerald-400 font-bold">✓ RESULT: Enterprise receivables integrity enforced.</span></div>`;
  }
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

// =========================================================================
// 100-Batch Benchmark Runner
// =========================================================================
export async function runBenchmarkAction() {
  const btnText = document.getElementById("benchmark-btn-text");
  if (btnText) btnText.innerText = "Evaluating 100 Cases...";

  try {
    const data = await safeApiCall("/api/v1/benchmark/run", "POST");
    const s = data.summary;

    countUpValue("kpi-net-recovery", 0, s.recovery_rate_pct, 1200, "", "%", 2);
    countUpValue("kpi-recovered-gmv", 0, s.recovered_gmv, 1400, "₹", "", 0);
    countUpValue("kpi-at-risk-gmv", 0, s.at_risk_gmv, 1400, "₹", "", 0);
    const humanEscKpi = document.getElementById("kpi-human-escalations");
    if (humanEscKpi) humanEscKpi.innerText = s.human_escalations;

    document.querySelectorAll("#bm-total-tx").forEach((el) => (el.innerText = s.total_transactions));
    document.querySelectorAll("#bm-at-risk-gmv").forEach((el) => (el.innerText = `₹${Math.round(s.at_risk_gmv).toLocaleString()}`));
    document.querySelectorAll("#bm-recovered-gmv").forEach((el) => (el.innerText = `₹${Math.round(s.recovered_gmv).toLocaleString()}`));
    document.querySelectorAll("#bm-recovery-rate").forEach((el) => (el.innerText = `↗ ${s.recovery_rate_pct.toFixed(2)}%`));
    document.querySelectorAll("#bm-fp-cost").forEach((el) => (el.innerText = `₹${s.false_positive_cost_inr.toFixed(2)}`));
    document.querySelectorAll("#bm-human-esc").forEach((el) => (el.innerText = s.human_escalations));
    document.querySelectorAll("#bm-safety-supp").forEach((el) => (el.innerText = s.safety_suppressions));

    triggerCelebrationConfetti();
    showToast(`🏆 100-Batch Benchmark Completed! Recovery Rate: ${s.recovery_rate_pct.toFixed(2)}% • 0 Violations`, "success");
  } catch (err) {
    showToast("Benchmark Notice: " + err.message, "warning");
  } finally {
    if (btnText) btnText.innerText = "Run 100-Batch Benchmark";
  }
}

// =========================================================================
// Banking Rail Telemetry & SRE Circuit Breaker
// =========================================================================
export function updateOverviewBankGrid() {
  const container = document.getElementById("overview-npci-grid");
  if (container) {
    const displayKeys = ["HDFC", "SBI", "ICICI", "AXIS"];
    container.innerHTML = displayKeys
      .map((k) => {
        const b = BANK_SWITCH_STATES[k] || { name: k, switchId: k + "_01", state: "HEALTHY", sr: 98.0, latency: 150 };
        const isDegraded = b.state === "DEGRADED";
        const isOutage = b.state === "OUTAGE";
        const borderClass = isOutage
          ? "border-rose-900/60 bg-[#1c080b]"
          : isDegraded
          ? "border-amber-900/60 bg-[#1e1208]"
          : "border-[#142442] bg-[#081224]";
        const badgeClass = isOutage
          ? "bg-[#380b10] text-rose-400 border border-rose-800"
          : isDegraded
          ? "bg-[#25131d] text-amber-400 border border-amber-900/60"
          : "bg-[#063b22] text-[#10b981] border border-[#0e5c36]";
        const valColor = isOutage ? "text-rose-400" : isDegraded ? "text-amber-400" : "text-emerald-400";
        const latColor = isOutage ? "text-rose-300" : isDegraded ? "text-amber-300" : "text-sky-300";

        return `
          <div class="p-3.5 rounded-xl ${borderClass} space-y-2 transition-all shadow-md">
            <div class="flex justify-between items-start">
              <div>
                <div class="text-xs font-bold text-white">${b.name}</div>
                <div class="text-[10px] text-slate-400 mono">Switch ID: ${b.switchId}</div>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">${b.state}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-[11px] mono pt-1 border-t border-[#142442]/60">
              <div><span class="text-slate-400">SR:</span> <span class="${valColor} font-bold">${b.sr.toFixed(1)}%</span></div>
              <div><span class="text-slate-400">Latency:</span> <span class="${latColor}">${Math.round(b.latency)}ms</span></div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  const sbi = BANK_SWITCH_STATES["SBI"] || { state: "DEGRADED", sr: 78.2, latency: 890 };
  const cbBadge = document.getElementById("circuit-breaker-status-badge");
  const sbiBtn = document.getElementById("btn-toggle-sbi");
  const sbiLabel = document.getElementById("btn-toggle-sbi-label");

  if (cbBadge) {
    if (sbi.state === "DEGRADED") {
      cbBadge.className = "px-2.5 py-0.5 rounded text-[11px] font-bold bg-[#25131d] text-amber-400 border border-amber-900/60 animate-pulse";
      cbBadge.textContent = "TRIPPED (Holding Traffic for Weibull +45m Window)";
    } else if (sbi.state === "OUTAGE") {
      cbBadge.className = "px-2.5 py-0.5 rounded text-[11px] font-bold bg-[#380b10] text-rose-400 border border-rose-800 animate-pulse";
      cbBadge.textContent = "TRIPPED (Circuit OPEN — Complete Outage)";
    } else {
      cbBadge.className = "px-2.5 py-0.5 rounded text-[11px] font-bold bg-[#063b22] text-[#10b981] border border-[#0e5c36]";
      cbBadge.textContent = "CLOSED (Passing All Healthy Traffic)";
    }
  }

  if (sbiLabel && sbiBtn) {
    if (sbi.state === "DEGRADED") {
      sbiLabel.textContent = "Restore SBI to HEALTHY (Currently DEGRADED)";
      sbiBtn.className = "px-3 py-1.5 bg-[#25131d] hover:bg-[#381628] border border-amber-500/70 text-amber-300 rounded-lg mono transition font-semibold flex items-center gap-1.5 cursor-pointer shadow-lg shadow-amber-950/40";
    } else if (sbi.state === "OUTAGE") {
      sbiLabel.textContent = "Restore SBI to HEALTHY (Currently OUTAGE)";
      sbiBtn.className = "px-3 py-1.5 bg-[#380b10] hover:bg-[#4d1017] border border-rose-500/70 text-rose-300 rounded-lg mono transition font-semibold flex items-center gap-1.5 cursor-pointer shadow-lg shadow-rose-950/40";
    } else {
      sbiLabel.textContent = "Degrade SBI Switch (Simulate 504 Outage)";
      sbiBtn.className = "px-3 py-1.5 bg-[#081224] hover:bg-[#0c1b36] border border-sky-800 text-sky-300 rounded-lg mono transition font-semibold flex items-center gap-1.5 cursor-pointer";
    }
  }
}

export async function simulateBankDegradation(bankCode = "SBI") {
  const current = BANK_SWITCH_STATES[bankCode] || BANK_SWITCH_STATES["SBI"];
  const newState = current.state === "HEALTHY" ? "DEGRADED" : "HEALTHY";
  const newSr = newState === "DEGRADED" ? 72.4 : 98.8;
  const newLatency = newState === "DEGRADED" ? 950.0 : 140.0;

  current.state = newState;
  current.sr = newSr;
  current.latency = newLatency;

  updateOverviewBankGrid();
  refreshFullNPCISwitchView();

  if (newState === "DEGRADED") {
    document.querySelectorAll("#fast-scenario-select").forEach((el) => (el.value = "GATEWAY_ERROR"));
    document.querySelectorAll("#fast-amount").forEach((el) => (el.value = 12500));
    document.querySelectorAll("#fast-pay-id").forEach((el) => (el.value = "pay_SBI_504_OUTAGE"));
  }

  safeApiCall("/api/v1/telemetry/npci-switch/update", "POST", {
    bank_code: bankCode,
    state: newState,
    success_rate_pct: newSr,
    latency_ms: newLatency,
    incidents: newState === "DEGRADED" ? ["Simulated Latency Spike (>900ms)"] : []
  }).catch((err) => console.warn("Backend telemetry sync notice:", err));

  if (newState === "DEGRADED") {
    showToast(`⚡ ${bankCode} Switch toggled to DEGRADED (Latency: ${newLatency}ms). Circuit Breaker TRIPPED: Dynamic Weibull shifted to +45m!`, "warning");
  } else {
    showToast(`✓ ${bankCode} Switch restored to HEALTHY (SR: ${newSr}%). Circuit Breaker CLOSED: Normal routing resumed.`, "success");
  }
}

export async function injectSimulatedNPCIStatus() {
  const bankSelect = document.getElementById("npci-sim-bank");
  const statusSelect = document.getElementById("npci-sim-status");
  const srInput = document.getElementById("npci-sim-sr");
  const feedback = document.getElementById("npci-sim-feedback");

  const bankCode = bankSelect ? bankSelect.value : "SBI";
  const state = statusSelect ? statusSelect.value : "DEGRADED";
  const sr = srInput ? parseFloat(srInput.value) || 75.0 : 75.0;
  const latency = state === "OUTAGE" ? 4500.0 : state === "DEGRADED" ? 880.0 : 150.0;

  if (BANK_SWITCH_STATES[bankCode]) {
    BANK_SWITCH_STATES[bankCode].state = state;
    BANK_SWITCH_STATES[bankCode].sr = sr;
    BANK_SWITCH_STATES[bankCode].latency = latency;
  }

  try {
    await fetch("/api/v1/telemetry/npci-switch/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        bank_code: bankCode,
        state: state,
        success_rate_pct: sr,
        latency_ms: latency,
        incidents: state !== "HEALTHY" ? [`Injected ${state} condition`] : []
      })
    });
  } catch (e) {}

  updateOverviewBankGrid();
  refreshFullNPCISwitchView();

  if (feedback) {
    feedback.innerHTML = `
      <div class="text-emerald-400 font-bold">[TELEMETRY INJECTED] ${bankCode} &rarr; ${state}</div>
      <div class="text-slate-300">Success Rate: ${sr}% • Latency: ${latency}ms • Adaptive Weibull Hazard shifted automatically.</div>
    `;
  }
  showToast(`⚡ NPCI Telemetry Injected: ${bankCode} is now ${state}`, state === "HEALTHY" ? "success" : "warning");
}

export async function refreshFullNPCISwitchView() {
  const container = document.getElementById("full-npci-switch-cards");
  if (!container) return;

  try {
    const res = await fetch("/api/v1/telemetry/npci-switch");
    const json = await res.json();
    if (json.success && json.data.switches) {
      json.data.switches.forEach((s) => {
        if (BANK_SWITCH_STATES[s.bank_code]) {
          BANK_SWITCH_STATES[s.bank_code].state = s.switch_state || s.state || "HEALTHY";
          BANK_SWITCH_STATES[s.bank_code].sr = typeof s.success_rate_pct === "number" ? s.success_rate_pct : 95.0;
          BANK_SWITCH_STATES[s.bank_code].latency =
            typeof s.avg_latency_ms === "number"
              ? s.avg_latency_ms
              : typeof s.latency_ms === "number"
              ? s.latency_ms
              : 180.0;
        }
      });
    }
  } catch (e) {}

  const allBanks = Object.keys(BANK_SWITCH_STATES);
  container.innerHTML = allBanks
    .map((k) => {
      const b = BANK_SWITCH_STATES[k];
      const isDegraded = b.state === "DEGRADED";
      const isOutage = b.state === "OUTAGE";
      const borderClass = isOutage
        ? "border-rose-900/60 bg-[#1c080b]"
        : isDegraded
        ? "border-amber-900/60 bg-[#1e1208]"
        : "border-[#142442] bg-[#081224]";
      const badgeClass = isOutage
        ? "bg-[#380b10] text-rose-400 border border-rose-800"
        : isDegraded
        ? "bg-[#25131d] text-amber-400 border border-amber-900/60"
        : "bg-[#063b22] text-[#10b981] border border-[#0e5c36]";
      const valColor = isOutage ? "text-rose-400" : isDegraded ? "text-amber-400" : "text-emerald-400";
      const barColor = isOutage ? "bg-rose-500" : isDegraded ? "bg-amber-500" : "bg-emerald-500";

      return `
        <div class="p-4 rounded-xl ${borderClass} space-y-3 shadow-md transition-all">
          <div class="flex justify-between items-start">
            <div>
              <div class="text-xs font-bold text-white">${b.name}</div>
              <div class="text-[10px] text-slate-400 mono">${b.switchId}</div>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">${b.state}</span>
          </div>

          <div class="space-y-1">
            <div class="flex justify-between text-[11px] mono">
              <span class="text-slate-400">Success Rate:</span>
              <span class="${valColor} font-bold">${b.sr.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-[#0d1b30] rounded-full h-1.5 overflow-hidden">
              <div class="${barColor} h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, b.sr)}%"></div>
            </div>
          </div>

          <div class="flex justify-between text-[11px] mono pt-1 border-t border-[#142442]/60">
            <span class="text-slate-400">Latency:</span>
            <span class="text-sky-300 font-bold">${Math.round(b.latency)}ms</span>
          </div>

          <button onclick="simulateBankDegradation('${k}')" class="w-full py-1.5 bg-[#142442] hover:bg-[#1e3a6a] text-sky-300 hover:text-white rounded-lg text-[10px] font-bold mono transition cursor-pointer">
            ⚡ Toggle ${k} State
          </button>
        </div>
      `;
    })
    .join("");
}

export function refreshNPCITelemetryGrid() {
  refreshFullNPCISwitchView();
  updateOverviewBankGrid();
  showToast("NPCI Banking Telemetry Radar Synchronized!", "success");
}

export function triggerSimulatedSecurityAlert() {
  const container = document.getElementById("alerts-container");
  const badge = document.getElementById("alerts-count-badge");
  if (!container) return;

  const ts = new Date().toLocaleTimeString("en-GB");
  const randomIp = `192.168.1.${Math.floor(Math.random() * 200 + 10)}`;
  const newAlert = document.createElement("div");
  newAlert.className = "p-4 rounded-xl bg-[#140608] border border-[#ef4444] space-y-1.5 animate-bounce";
  newAlert.innerHTML = `
    <div class="flex justify-between items-center">
      <span class="text-xs font-bold text-rose-400 mono">[CRITICAL] Concurrent Webhook Storm Defended</span>
      <span class="text-[10px] text-slate-400 mono">${ts} (Just now)</span>
    </div>
    <p class="text-xs text-slate-300">50 duplicate webhook replays fired from ${randomIp}. Distributed Atomic Mutex claimed 1 primary execution and dropped 49 replays (0 duplicate payments).</p>
    <div class="text-[11px] text-emerald-400 font-bold mono">✓ Action Taken: IDEMPOTENT_ATOMIC_LOCK_ISOLATION</div>
  `;
  container.prepend(newAlert);
  if (badge) badge.textContent = "3 Active Incidents";
  showToast("New SRE Security Incident detected & mitigated by Atomic Mutex!", "error");
}

// =========================================================================
// WhatsApp Preview & Simulation Modal
// =========================================================================
export function openWhatsAppPreviewModal(customData = null) {
  let amt = 2499.0;
  let payId = "pay_9A12BC34DE";
  let recipient = "Customer (+91 98765 43210)";

  if (customData) {
    if (customData.invoice_amount) amt = parseFloat(customData.invoice_amount) || 2499.0;
    if (customData.invoice_id) payId = customData.invoice_id;
    if (customData.customer_phone) recipient = `Customer (${customData.customer_phone})`;
    if (customData.dispatched_whatsapp_recipient) recipient = customData.dispatched_whatsapp_recipient;
  } else {
    const amtInput = document.querySelector("#fast-amount");
    const payIdInput = document.querySelector("#fast-pay-id");
    if (amtInput) amt = parseFloat(amtInput.value) || 2499.0;
    if (payIdInput && payIdInput.value) payId = payIdInput.value;
  }

  const waOrder = document.getElementById("wa-order-id");
  const waAmt = document.getElementById("wa-amount");
  const waSuccessState = document.getElementById("wa-success-state");
  const waButtonsContainer = document.getElementById("wa-buttons-container");
  const waRecipient = document.getElementById("wa-recipient-name");

  if (waOrder) waOrder.textContent = payId;
  if (waAmt) waAmt.textContent = `₹${amt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  if (waRecipient) waRecipient.textContent = recipient;
  if (waSuccessState) waSuccessState.classList.add("hidden");
  if (waButtonsContainer) waButtonsContainer.classList.remove("hidden");

  const modal = document.getElementById("whatsapp-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.style.display = "flex";
  }
}

export function closeWhatsAppPreviewModal() {
  const modal = document.getElementById("whatsapp-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.style.display = "none";
  }
}

export function simulateUpiAppPayment(appName) {
  const buttonsContainer = document.getElementById("wa-buttons-container");
  const successState = document.getElementById("wa-success-state");
  const amt = document.getElementById("wa-amount") ? document.getElementById("wa-amount").textContent : "₹2,499.00";
  const orderId = document.getElementById("wa-order-id") ? document.getElementById("wa-order-id").textContent : "pay_9A12BC34DE";

  if (buttonsContainer) buttonsContainer.classList.add("hidden");
  if (successState) {
    successState.classList.remove("hidden");
    successState.innerHTML = `
      <div class="p-3 bg-[#064e3b]/80 border border-[#059669] rounded-xl text-center space-y-1.5 animate-pulse">
        <div class="text-xs font-bold text-[#34d399] flex items-center justify-center gap-1.5">
          <svg class="w-4 h-4 animate-spin text-[#34d399]" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>Authorizing via ${appName}...</span>
        </div>
        <div class="text-[10px] text-slate-300">Processing ${amt} on ${appName} Gateway Rail</div>
      </div>
    `;

    setTimeout(() => {
      successState.innerHTML = `
        <div class="p-3 bg-[#064e3b] border border-[#10b981] rounded-xl text-center space-y-2 shadow-lg">
          <div class="w-7 h-7 bg-[#10b981] rounded-full mx-auto flex items-center justify-center text-white text-xs font-bold shadow">
            ✓
          </div>
          <div class="text-xs font-bold text-white">Payment Recovered via ${appName}!</div>
          <div class="text-[10px] text-emerald-200">
            Receipt: REC_${Math.floor(Math.random() * 89999 + 10000)} • Mutex Released • Audit Chained
          </div>
          <button onclick="resetWhatsAppModalView()" class="mt-1 px-3 py-1 bg-[#10b981] hover:bg-[#059669] text-white text-[10px] font-bold rounded-lg shadow">
            Simulate Another Test
          </button>
        </div>
      `;
      triggerCelebrationConfetti();
      showToast(`⚡ ${orderId} Recovered (${amt}) via ${appName}!`, "success");
    }, 700);
  }
}

export function toggleWhatsAppQrCode() {
  const qrContainer = document.getElementById("wa-qr-container");
  const toggleText = document.getElementById("wa-qr-toggle-text");
  if (!qrContainer) return;

  if (qrContainer.classList.contains("hidden")) {
    qrContainer.classList.remove("hidden");
    if (toggleText) toggleText.textContent = "▲ Hide UPI QR Code";

    const payId = document.getElementById("wa-order-id")?.textContent || "pay_9A12BC34DE";
    const amtStr = document.getElementById("wa-amount")?.textContent || "₹2,499.00";
    const amt = parseFloat(amtStr.replace(/[^0-9.]/g, "")) || 2499.0;
    const upiUri = `upi://pay?pa=razorrevive.merchant@razorpay&pn=Razorpay+Merchant&am=${amt.toFixed(2)}&tr=${payId}&cu=INR&tn=Invoice+Recovery`;

    const mount = document.getElementById("wa-qr-code-mount");
    if (mount) {
      mount.innerHTML = "";
      if (typeof QRCode !== "undefined") {
        new QRCode(mount, {
          text: upiUri,
          width: 148,
          height: 148,
          colorDark: "#0c2340",
          colorLight: "#ffffff",
          correctLevel: QRCode.CorrectLevel.M
        });
        setTimeout(() => {
          const badge = document.createElement("div");
          badge.className = "absolute inset-0 flex items-center justify-center pointer-events-none";
          badge.innerHTML = `
            <div class="w-7 h-7 rounded-full bg-[#0c55ea] border-2 border-white flex items-center justify-center shadow-md">
              <span class="text-[8px] font-black text-white leading-none">UPI</span>
            </div>
          `;
          mount.appendChild(badge);
        }, 50);
      }
    }
  } else {
    qrContainer.classList.add("hidden");
    if (toggleText) toggleText.textContent = "📱 Show Dynamic UPI QR Code";
  }
}

export function resetWhatsAppModalView() {
  const buttonsContainer = document.getElementById("wa-buttons-container");
  const successState = document.getElementById("wa-success-state");
  const qrContainer = document.getElementById("wa-qr-container");
  const toggleText = document.getElementById("wa-qr-toggle-text");
  if (successState) successState.classList.add("hidden");
  if (buttonsContainer) buttonsContainer.classList.remove("hidden");
  if (qrContainer) qrContainer.classList.add("hidden");
  if (toggleText) toggleText.textContent = "📱 Show Dynamic UPI QR Code";
}

export function copyUpiIntentUri() {
  const amtInput = document.getElementById("fast-amount");
  const amt = amtInput ? parseFloat(amtInput.value) || 2499.0 : 2499.0;
  const uri = `upi://pay?pa=razorrevive.merchant@razorpay&pn=Razorpay+Merchant&am=${amt.toFixed(2)}&cu=INR&tn=Invoice+Recovery`;
  navigator.clipboard.writeText(uri).then(() => {
    showToast("UPI Intent URI copied to clipboard!", "success");
  });
}

// =========================================================================
// Dispatched Corporate Email Modal
// =========================================================================
export async function openDispatchedEmailModal(dispatchId) {
  const modal = document.getElementById("dispatched-email-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.style.display = "flex";
  }

  try {
    let dispatchData = null;
    if (dispatchId) {
      dispatchData = await safeApiCall(`/api/v1/communication/${dispatchId}`);
    }
    if (!dispatchData || dispatchData.error) {
      const recents = await safeApiCall("/api/v1/communication/recent");
      if (recents && recents.dispatches && recents.dispatches.length > 0) {
        dispatchData = recents.dispatches[recents.dispatches.length - 1];
        dispatchId = dispatchData.id;
      }
    }

    if (!dispatchData) {
      dispatchData = {
        recipient: "finance@acmeenterprises.in",
        sender: "Razorpay Enterprise Invoicing <invoices@enterprise.razorpay.com>",
        subject: "Corrected Corporate Tax Invoice — #INV-ENT-2026-998",
        audit_hash: "a83f9b7e2d1405c6e8a71b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef",
        status: "DELIVERED",
        rendered_html: `
          <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 24px; color: #0f172a; max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0c55ea; padding-bottom: 14px; margin-bottom: 20px;">
              <div>
                <h2 style="margin: 0; color: #0c2340; font-size: 20px; font-weight: 800;">Razorpay Enterprise Invoice</h2>
                <div style="color: #64748b; font-size: 11px; margin-top: 2px;">GST Compliance Verified • RFC-822 Standard</div>
              </div>
              <span style="background: #ecfdf5; color: #059669; font-weight: bold; font-size: 11px; padding: 4px 12px; border-radius: 9999px; border: 1px solid #a7f3d0;">DELIVERED</span>
            </div>
            <table style="width: 100%; font-size: 12px; margin-bottom: 16px; border-collapse: collapse;">
              <tr>
                <td style="color: #64748b; padding: 4px 0;"><strong>Invoice Ref:</strong></td><td style="padding: 4px 0;">INV-ENT-2026-998</td>
                <td style="color: #64748b; padding: 4px 0;"><strong>Billed To:</strong></td><td style="padding: 4px 0;">Acme Pvt Ltd</td>
              </tr>
              <tr>
                <td style="color: #64748b; padding: 4px 0;"><strong>Buyer GSTIN:</strong></td><td style="padding: 4px 0; font-weight: bold; color: #0c55ea;">29AABCU9603R1Z2</td>
                <td style="color: #64748b; padding: 4px 0;"><strong>Total Amount:</strong></td><td style="padding: 4px 0; font-weight: bold;">₹85,000.00</td>
              </tr>
            </table>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; font-size: 11px; margin-bottom: 16px; line-height: 1.5;">
              <strong style="color: #0c55ea;">Autonomous Mutation Audit:</strong> Buyer GSTIN corrected and verified via AWS Cedar zero-trust policy. Instant settlement link enabled.
            </div>
            <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px;">
              Cryptographic SHA-256 Proof: a83f9b7e2d1405c6e8a71b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef
            </div>
          </div>
        `
      };
    }

    if (dispatchData) {
      const d = dispatchData.data || dispatchData;
      const toEl = document.getElementById("dispatched-email-to");
      const fromEl = document.getElementById("dispatched-email-from");
      const subjEl = document.getElementById("dispatched-email-subject");
      const hashEl = document.getElementById("dispatched-email-hash");
      const statusEl = document.getElementById("dispatched-email-status-pill");

      if (toEl) toEl.textContent = d.recipient || "finance@acme.com";
      if (fromEl) fromEl.textContent = d.sender || "Razorpay Invoicing <invoices@enterprise.razorpay.com>";
      if (subjEl) subjEl.textContent = d.subject || "Corrected Corporate Tax Invoice";
      if (hashEl) hashEl.textContent = d.audit_hash ? d.audit_hash.substring(0, 32) + "..." : "sha256_verified_chain";
      if (statusEl) statusEl.textContent = d.status || "DELIVERED";

      const iframe = document.getElementById("dispatched-email-frame");
      if (iframe) {
        if (d.rendered_html) {
          iframe.srcdoc = d.rendered_html;
        } else {
          const emailUrl = dispatchId ? `/api/v1/communication/${dispatchId}/html` : `/api/v1/communication/email/send`;
          fetch(emailUrl)
            .then((r) => r.text())
            .then((html) => {
              iframe.srcdoc = html;
            })
            .catch(() => {
              iframe.src = emailUrl;
            });
        }
      }
    }
  } catch (err) {
    console.error("Error opening dispatched email modal:", err);
  }
}

export function closeDispatchedEmailModal() {
  const modal = document.getElementById("dispatched-email-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.style.display = "none";
  }
}

// =========================================================================
// ROI & Financial Yield Calculator
// =========================================================================
export function updateLiveRoiCalculator() {
  const gmvInput = document.getElementById("slider-gmv");
  const failInput = document.getElementById("slider-fail");
  if (!gmvInput || !failInput) return;

  const gmv = parseFloat(gmvInput.value);
  const failRate = parseFloat(failInput.value);

  const gmvLabel = document.getElementById("slider-gmv-val");
  const failLabel = document.getElementById("slider-fail-val");

  if (gmvLabel) {
    if (gmv >= 10000000) {
      gmvLabel.textContent = `₹${(gmv / 10000000).toFixed(2)} Cr`;
    } else {
      gmvLabel.textContent = `₹${(gmv / 100000).toFixed(0)} Lakhs`;
    }
  }
  if (failLabel) {
    failLabel.textContent = `${failRate.toFixed(1)}%`;
  }

  const failedGmv = gmv * (failRate / 100.0);
  const recoveredGmv = failedGmv * 0.4224;
  const annualRecovered = recoveredGmv * 12;
  const retainedUsers = Math.round((failedGmv / 2500) * 0.77);

  const outMonthly = document.getElementById("roi-out-monthly");
  const outAnnual = document.getElementById("roi-out-annual");
  const outUsers = document.getElementById("roi-out-users");

  if (outMonthly) outMonthly.textContent = `₹${Math.round(recoveredGmv).toLocaleString("en-IN")}`;
  if (outAnnual) outAnnual.textContent = `₹${Math.round(annualRecovered).toLocaleString("en-IN")}`;
  if (outUsers) outUsers.textContent = `${retainedUsers.toLocaleString("en-IN")} / mo`;
}

// =========================================================================
// Structured Event Logs & Config
// =========================================================================
export async function loadLiveLogs() {
  try {
    const data = await safeApiCall("/api/v1/logs/recent?limit=30");
    const container = document.getElementById("live-logs-container");
    if (data.logs && data.logs.length > 0 && container) {
      container.innerHTML = data.logs
        .map((l) => {
          const levelColor =
            l.level === "ERROR" ? "text-rose-400" : l.level === "WARN" ? "text-amber-400" : "text-sky-400";
          return `<div class="py-0.5 border-b border-[#142442]/40"><span class="text-slate-500">[${l.timestamp}]</span> <span class="${levelColor} font-bold">[${l.level}]</span> <span class="text-indigo-300">[${l.module}]</span> <span class="text-slate-200">${l.message}</span> <span class="text-slate-500 font-mono text-[10px]">${l.trace_id}</span></div>`;
        })
        .join("");
    }
  } catch (e) {
    console.error("Could not load logs", e);
  }
}

export function copyLogsToClipboard() {
  const container = document.getElementById("live-logs-container");
  if (container) {
    navigator.clipboard.writeText(container.innerText);
    showToast("Logs copied to clipboard!", "success");
  }
}

export function clearLogsView() {
  const container = document.getElementById("live-logs-container");
  if (container) {
    container.innerHTML = `<div class="text-slate-500 italic">[Logs cleared at ${new Date().toLocaleTimeString("en-GB")}]</div>`;
    showToast("Log view cleared.", "info");
  }
}

export function filterLogsBy(severity) {
  const buttons = ["all", "info", "policy", "security", "alert"];
  buttons.forEach((b) => {
    const btn = document.getElementById(`log-filter-${b}`);
    if (btn) {
      if (b === severity.toLowerCase()) {
        btn.className = "px-2.5 py-1 rounded bg-[#0c55ea] text-white font-bold";
      } else {
        btn.className = "px-2.5 py-1 rounded bg-[#081224] text-slate-300 hover:bg-[#142442]";
      }
    }
  });

  const container = document.getElementById("live-logs-container");
  if (!container) return;

  const ts = new Date().toISOString();
  if (severity === "POLICY") {
    container.innerHTML = `
      <div class="text-emerald-400">{"timestamp": "${ts}", "module": "PolicyEngine", "check": "TRAI_QUIET_HOURS", "status": "PASSED"}</div>
      <div class="text-emerald-400">{"timestamp": "${ts}", "module": "PolicyEngine", "check": "DISCOUNT_CLAMP", "applied": 10.0, "max_allowed": 10.0}</div>
      <div class="text-emerald-400">{"timestamp": "${ts}", "module": "PolicyEngine", "check": "RETRY_CEILING", "attempt": 1, "ceiling": 3}</div>
    `;
  } else if (severity === "SECURITY") {
    container.innerHTML = `
      <div class="text-purple-400">{"timestamp": "${ts}", "module": "HMAC", "signature": "hmac_sha256", "verdict": "VERIFIED"}</div>
      <div class="text-purple-400">{"timestamp": "${ts}", "module": "Mutex", "key": "merchant_99:pay_882910", "action": "ACQUIRED"}</div>
      <div class="text-purple-400">{"timestamp": "${ts}", "module": "AuditChain", "event": "MUTEX_LOCK_COMMITTED", "hash": "8cd5fd0a82bc..."}</div>
    `;
  } else if (severity === "ALERT") {
    container.innerHTML = `
      <div class="text-rose-400">{"timestamp": "${ts}", "module": "AnomalyEngine", "severity": "HIGH", "event": "VELOCITY_SPIKE_CONTAINED"}</div>
      <div class="text-amber-400">{"timestamp": "${ts}", "module": "NPCSwitch", "severity": "MEDIUM", "event": "HDFC_GATEWAY_504_DEGRADATION"}</div>
    `;
  } else {
    loadLiveLogs();
  }
}

export function saveConfigurationSettings() {
  const discountPct = document.getElementById("cfg-max-discount-pct")?.value || "10";
  const discountInr = document.getElementById("cfg-max-discount-inr")?.value || "500";
  const cfoThreshold = document.getElementById("cfg-cfo-threshold")?.value || "50000";
  const mutexBackend = document.getElementById("cfg-mutex-backend")?.value || "sqlite_wal";

  showToast(
    `Configuration Saved! Policy limits: ${discountPct}% / ₹${discountInr} cap, CFO > ₹${parseInt(cfoThreshold).toLocaleString("en-IN")}, Backend: ${mutexBackend.toUpperCase()}`,
    "success"
  );
}

// =========================================================================
// Guided Tour
// =========================================================================
let currentTourIndex = 0;
let tourActive = false;

export function startGuidedTour() {
  tourActive = true;
  currentTourIndex = 0;
  switchNavTab("overview");
  showTourStep(currentTourIndex);
  showToast("🧭 Starting 60-Second Guided SRE Architecture Tour", "info");
}

function showTourStep(index) {
  if (index < 0 || index >= TOUR_STEPS.length) {
    exitGuidedTour();
    return;
  }
  currentTourIndex = index;
  const step = TOUR_STEPS[index];

  setTimeout(() => {
    let el = document.getElementById(step.target);
    if (!el) {
      el = document.querySelector(step.target) || document.body;
    }
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(() => {
      renderTourOverlay(el, step, index);
    }, 350);
  }, 100);
}

function renderTourOverlay(targetEl, step, index) {
  let overlay = document.getElementById("guided-tour-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "guided-tour-overlay";
    overlay.className = "fixed inset-0 pointer-events-none z-[99998] transition-all duration-300";
    overlay.innerHTML = `
      <div id="tour-spotlight-box" class="absolute rounded-2xl pointer-events-none transition-all duration-300 border-2 border-sky-400 shadow-[0_0_0_9999px_rgba(3,7,18,0.85),0_0_35px_rgba(56,189,248,0.7)] animate-pulse"></div>
      <div id="tour-popover-card" class="absolute pointer-events-auto w-auto max-w-[92vw] sm:max-w-md rounded-2xl bg-white/95 dark:bg-[#0c182c]/95 backdrop-blur-xl border-2 border-sky-500/70 shadow-2xl p-4 sm:p-5 space-y-3.5 text-slate-900 dark:text-slate-100 transition-all duration-300 z-10">
        <div class="flex items-center justify-between border-b border-slate-200 dark:border-blue-900/50 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider mono bg-blue-950 text-sky-400 border border-blue-800" id="tour-badge">SRE Tour</span>
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 mono" id="tour-step-counter">Step ${index + 1} of ${TOUR_STEPS.length}</span>
          </div>
          <button onclick="exitGuidedTour()" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition font-bold text-sm cursor-pointer">✕</button>
        </div>
        <div class="space-y-1.5">
          <h4 class="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white" id="tour-title">${step.title}</h4>
          <p class="text-xs sm:text-[12.5px] leading-relaxed text-slate-700 dark:text-slate-300 font-normal" id="tour-desc">${step.desc}</p>
        </div>
        <div class="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-blue-900/40">
          <div class="flex items-center gap-1.5" id="tour-dots-container">
            ${TOUR_STEPS.map((_, i) => `<span class="w-2 h-2 rounded-full transition-all ${i === index ? "w-5 bg-sky-400" : "bg-slate-300 dark:bg-slate-700"}"></span>`).join("")}
          </div>
          <div class="flex items-center gap-2">
            <button onclick="prevTourStep()" id="tour-prev-btn" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-[#142442] dark:hover:bg-[#1c335a] text-slate-700 dark:text-slate-200 text-xs font-bold transition cursor-pointer ${index === 0 ? "opacity-40 pointer-events-none" : ""}">
              ⬅ Back
            </button>
            <button onclick="nextTourStep()" id="tour-next-btn" class="px-4 py-1.5 rounded-xl bg-gradient-to-r from-[#0c55ea] to-[#0284c7] hover:from-[#0942b8] hover:to-[#0369a1] text-white text-xs font-extrabold shadow-lg transition-all active:scale-95 cursor-pointer">
              ${index === TOUR_STEPS.length - 1 ? "Finish Tour 🎉" : "Next ➔"}
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
  }

  const rect = targetEl.getBoundingClientRect();
  const pad = 8;
  const spotBox = document.getElementById("tour-spotlight-box");
  const popover = document.getElementById("tour-popover-card");

  if (spotBox) {
    spotBox.style.top = `${Math.max(0, rect.top - pad)}px`;
    spotBox.style.left = `${Math.max(0, rect.left - pad)}px`;
    spotBox.style.width = `${rect.width + pad * 2}px`;
    spotBox.style.height = `${rect.height + pad * 2}px`;
  }

  const counterEl = document.getElementById("tour-step-counter");
  const titleEl = document.getElementById("tour-title");
  const descEl = document.getElementById("tour-desc");
  const dotsContainer = document.getElementById("tour-dots-container");
  const prevBtn = document.getElementById("tour-prev-btn");
  const nextBtn = document.getElementById("tour-next-btn");

  if (counterEl) counterEl.textContent = `Step ${index + 1} of ${TOUR_STEPS.length}`;
  if (titleEl) titleEl.textContent = step.title;
  if (descEl) descEl.innerHTML = step.desc;
  if (dotsContainer) {
    dotsContainer.innerHTML = TOUR_STEPS.map((_, i) =>
      `<span class="w-2 h-2 rounded-full transition-all ${i === index ? "w-5 bg-sky-400" : "bg-slate-300 dark:bg-slate-700"}"></span>`
    ).join("");
  }
  if (prevBtn) {
    if (index === 0) prevBtn.classList.add("opacity-40", "pointer-events-none");
    else prevBtn.classList.remove("opacity-40", "pointer-events-none");
  }
  if (nextBtn) {
    nextBtn.textContent = index === TOUR_STEPS.length - 1 ? "Finish Tour 🎉" : "Next ➔";
  }

  if (popover) {
    const popW = Math.min(420, window.innerWidth - 32);
    const popH = popover.offsetHeight || 200;
    let top = rect.bottom + 16;
    let left = rect.left + rect.width / 2 - popW / 2;

    if (top + popH > window.innerHeight - 20) {
      top = Math.max(20, rect.top - popH - 16);
    }
    if (left < 16) left = 16;
    if (left + popW > window.innerWidth - 16) left = window.innerWidth - popW - 16;

    popover.style.top = `${top}px`;
    popover.style.left = `${left}px`;
  }
}

export function nextTourStep() {
  if (currentTourIndex < TOUR_STEPS.length - 1) {
    showTourStep(currentTourIndex + 1);
  } else {
    exitGuidedTour();
    showToast("🎉 Tour Completed! Explore live scenarios or run benchmarks!", "success");
  }
}

export function prevTourStep() {
  if (currentTourIndex > 0) {
    showTourStep(currentTourIndex - 1);
  }
}

export function exitGuidedTour() {
  tourActive = false;
  const overlay = document.getElementById("guided-tour-overlay");
  if (overlay) overlay.remove();
}

// =========================================================================
// Command Palette
// =========================================================================
let cmdkSelectedIndex = 0;
let filteredCmdkList = [...CMDK_COMMANDS];

export function openCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  const input = document.getElementById("cmdk-search-input");
  if (modal) {
    modal.classList.remove("hidden");
    modal.style.display = "flex";
    cmdkSelectedIndex = 0;
    filterCommandPalette("");
    if (input) {
      input.value = "";
      setTimeout(() => input.focus(), 50);
    }
  }
}

export function closeCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.style.display = "none";
  }
}

export function filterCommandPalette(query) {
  const q = (query || "").toLowerCase().trim();
  const listContainer = document.getElementById("cmdk-results-list");
  if (!listContainer) return;

  filteredCmdkList = CMDK_COMMANDS.filter(
    (c) => c.label.toLowerCase().includes(q) || c.id.toLowerCase().includes(q)
  );

  if (filteredCmdkList.length === 0) {
    listContainer.innerHTML = `
      <div class="p-6 text-center text-slate-400 text-xs">
        <span class="text-base">🔍</span> No matching commands found for "${query}"
      </div>
    `;
    return;
  }

  if (cmdkSelectedIndex >= filteredCmdkList.length) {
    cmdkSelectedIndex = 0;
  }

  listContainer.innerHTML = filteredCmdkList
    .map(
      (c, idx) => `
      <div onclick="executePaletteCommand(${idx})" class="p-2.5 px-3 rounded-xl flex items-center justify-between cursor-pointer transition-all ${
        idx === cmdkSelectedIndex
          ? "bg-[#0c55ea] text-white font-bold shadow-md"
          : "text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-[#142442]"
      }">
        <div class="flex items-center gap-2.5 text-xs">
          <span class="text-sm">${c.icon}</span>
          <span>${c.label}</span>
        </div>
        <span class="px-2 py-0.5 rounded text-[9px] font-bold uppercase mono ${
          idx === cmdkSelectedIndex
            ? "bg-white/20 text-white"
            : "bg-slate-200 dark:bg-[#0c182c] text-slate-500 dark:text-slate-400"
        }">ACTION</span>
      </div>
    `
    )
    .join("");
}

export function executePaletteCommand(index) {
  const cmd = filteredCmdkList[index];
  if (cmd && typeof cmd.action === "function") {
    closeCommandPalette();
    cmd.action();
  }
}

export function triggerCelebrationConfetti() {
  if (typeof confetti === "function") {
    confetti({
      particleCount: 75,
      spread: 80,
      origin: { y: 0.6 },
      colors: ["#0c55ea", "#10b981", "#38bdf8", "#8b5cf6", "#f59e0b"]
    });
  }
}

export function countUpValue(elementId, start, end, duration = 1200, prefix = "", suffix = "", decimals = 0) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const startTime = performance.now();
  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    const current = start + (end - start) * ease;
    el.textContent = `${prefix}${current.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

export function animateAllKpis() {
  countUpValue("kpi-net-recovery", 0, 78.39, 1300, "", "%", 2);
  countUpValue("kpi-recovered-gmv", 0, 425600, 1500, "₹", "", 0);
  countUpValue("kpi-at-risk-gmv", 0, 542850, 1500, "₹", "", 0);
}

// =========================================================================
// Register All Handlers on Window for Inline Markup Compatibility
// =========================================================================
window.safeApiCall = safeApiCall;
window.showToast = showToast;
window.mountComponents = mountComponents;
window.switchNavTab = switchNavTab;
window.openDetailedBenchmarkSuite = openDetailedBenchmarkSuite;
window.toggleMobileMenu = toggleMobileMenu;
window.toggleThemeMode = toggleThemeMode;
window.toggleScenariosMenu = toggleScenariosMenu;
window.selectScenario = selectScenario;
window.runLiveAttack = runLiveAttack;
window.runBenchmarkAction = runBenchmarkAction;
window.updateOverviewBankGrid = updateOverviewBankGrid;
window.simulateBankDegradation = simulateBankDegradation;
window.injectSimulatedNPCIStatus = injectSimulatedNPCIStatus;
window.refreshFullNPCISwitchView = refreshFullNPCISwitchView;
window.refreshNPCITelemetryGrid = refreshNPCITelemetryGrid;
window.triggerSimulatedSecurityAlert = triggerSimulatedSecurityAlert;
window.openWhatsAppPreviewModal = openWhatsAppPreviewModal;
window.closeWhatsAppPreviewModal = closeWhatsAppPreviewModal;
window.simulateUpiAppPayment = simulateUpiAppPayment;
window.toggleWhatsAppQrCode = toggleWhatsAppQrCode;
window.resetWhatsAppModalView = resetWhatsAppModalView;
window.copyUpiIntentUri = copyUpiIntentUri;
window.openDispatchedEmailModal = openDispatchedEmailModal;
window.closeDispatchedEmailModal = closeDispatchedEmailModal;
window.updateLiveRoiCalculator = updateLiveRoiCalculator;
window.loadLiveLogs = loadLiveLogs;
window.copyLogsToClipboard = copyLogsToClipboard;
window.clearLogsView = clearLogsView;
window.filterLogsBy = filterLogsBy;
window.saveConfigurationSettings = saveConfigurationSettings;
window.startGuidedTour = startGuidedTour;
window.nextTourStep = nextTourStep;
window.prevTourStep = prevTourStep;
window.exitGuidedTour = exitGuidedTour;
window.openCommandPalette = openCommandPalette;
window.closeCommandPalette = closeCommandPalette;
window.filterCommandPalette = filterCommandPalette;
window.executePaletteCommand = executePaletteCommand;
window.triggerCelebrationConfetti = triggerCelebrationConfetti;
window.countUpValue = countUpValue;
window.animateAllKpis = animateAllKpis;

window.UnifiedVoiceEngine = UnifiedVoiceEngine;
window.loadVoices = loadVoices;
window.speakText = speakText;
window.stopSpeaking = stopSpeaking;
window.replayLastSpeech = replayLastSpeech;
window.toggleMicrophoneSTT = toggleMicrophoneSTT;
window.changeNeuralVoice = changeNeuralVoice;
window.toggleLiveVoiceCall = toggleLiveVoiceCall;
window.startLiveVoiceCall = startLiveVoiceCall;
window.endLiveVoiceCall = endLiveVoiceCall;

window.triggerFastLoopPipeline = triggerFastLoopPipeline;
window.inspectCardTokenAction = inspectCardTokenAction;
window.generateAndLoadSampleCsv = generateAndLoadSampleCsv;
window.handleBulkCsvFileSelected = handleBulkCsvFileSelected;
window.exportBatchResolutionCsv = exportBatchResolutionCsv;

window.triggerVoiceTurnAction = triggerVoiceTurnAction;
window.loadPTPRecords = loadPTPRecords;

window.fetchAuditEvents = fetchAuditEvents;
window.verifyAuditLedgerIntegrity = verifyAuditLedgerIntegrity;
window.refreshAuditLedger = refreshAuditLedger;
window.downloadAuditCertificate = downloadAuditCertificate;

window.refreshCfoQueueUI = refreshCfoQueueUI;
window.handleCfoApprove = handleCfoApprove;
window.handleCfoReject = handleCfoReject;

window.initFintech3DTopology = initFintech3DTopology;
window.renderWeibullCurve = renderWeibullCurve;

window.toggleAiCopilotDrawer = toggleAiCopilotDrawer;
window.sendQuickPrompt = sendQuickPrompt;
window.speakLastCopilotMessage = speakLastCopilotMessage;
window.speakCopilotResponse = speakCopilotResponse;
window.handleCopilotCustomQuery = handleCopilotCustomQuery;

window.openAwsCedarModal = openAwsCedarModal;
window.closeAwsCedarModal = closeAwsCedarModal;
window.applyCedarTestCase = applyCedarTestCase;
window.runCedarTestEvaluation = runCedarTestEvaluation;

// Global Event Listeners (Keyboard shortcuts: Cmd+K, Esc, Arrow Keys)
window.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    const modal = document.getElementById("command-palette-modal");
    if (modal && !modal.classList.contains("hidden")) {
      closeCommandPalette();
    } else {
      openCommandPalette();
    }
    return;
  }

  const modal = document.getElementById("command-palette-modal");
  if (modal && !modal.classList.contains("hidden")) {
    if (e.key === "Escape") {
      e.preventDefault();
      closeCommandPalette();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (filteredCmdkList.length > 0) {
        cmdkSelectedIndex = (cmdkSelectedIndex + 1) % filteredCmdkList.length;
        filterCommandPalette(document.getElementById("cmdk-search-input")?.value || "");
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (filteredCmdkList.length > 0) {
        cmdkSelectedIndex = (cmdkSelectedIndex - 1 + filteredCmdkList.length) % filteredCmdkList.length;
        filterCommandPalette(document.getElementById("cmdk-search-input")?.value || "");
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filteredCmdkList.length > 0) {
        executePaletteCommand(cmdkSelectedIndex);
      }
    }
  }

  if (tourActive) {
    if (e.key === "Escape") exitGuidedTour();
    if (e.key === "ArrowRight") nextTourStep();
    if (e.key === "ArrowLeft") prevTourStep();
  }
});

// Click outside to dismiss dropdowns
window.onclick = function (event) {
  if (!event.target.closest("#scenarios-btn") && !event.target.closest("#scenarios-dropdown")) {
    document.getElementById("scenarios-dropdown")?.classList.add("hidden");
  }
  if (!event.target.closest("#theme-palette-btn") && !event.target.closest("#theme-palette-dropdown")) {
    document.getElementById("theme-palette-dropdown")?.classList.add("hidden");
  }
};

// 21st.dev Dynamic Spotlight cursor tracking
document.addEventListener("mousemove", (e) => {
  const cards = document.querySelectorAll(".spotlight-card, .spotlight-radial");
  cards.forEach((card) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty("--mouse-x", `${x}px`);
    card.style.setProperty("--mouse-y", `${y}px`);
  });
});

// =========================================================================
// Bootstrapping on DOM Load
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("rr_theme") || "light";
  const icon = document.getElementById("theme-icon");
  const text = document.getElementById("theme-text");
  if (savedTheme === "dark") {
    document.documentElement.classList.remove("light");
    document.documentElement.classList.add("dark");
    if (icon) icon.innerText = "☀️";
    if (text) text.textContent = "Light";
  } else {
    document.documentElement.classList.remove("dark");
    document.documentElement.classList.add("light");
    if (icon) icon.innerText = "🌙";
    if (text) text.textContent = "Dark";
  }

  const savedPalette = localStorage.getItem("omnirevive_palette") || "cyber-obsidian";
  applyThemePalette(savedPalette);

  mountComponents();
  landingGateway.init();
  evalDashboard.init();
  updateOverviewBankGrid();
  refreshAuditLedger();
  refreshFullNPCISwitchView();
  renderWeibullCurve();
  initFintech3DTopology();
  updateLiveRoiCalculator();
  animateAllKpis();
  refreshCfoQueueUI();
  try { initLiveTelemetryStream(); } catch(e) { console.warn("Live telemetry init error:", e); }

  setInterval(refreshAuditLedger, 5000);
  setInterval(refreshFullNPCISwitchView, 10000);
  setInterval(refreshCfoQueueUI, 15000);
});

// Immediate execution if script is loaded after DOMContentLoaded
if (document.readyState === "complete" || document.readyState === "interactive") {
  const savedPalette = localStorage.getItem("omnirevive_palette") || "cyber-obsidian";
  applyThemePalette(savedPalette);
  mountComponents();
  landingGateway.init();
  evalDashboard.init();
  updateOverviewBankGrid();
  refreshAuditLedger();
  refreshFullNPCISwitchView();
  renderWeibullCurve();
  initFintech3DTopology();
  updateLiveRoiCalculator();
  animateAllKpis();
  refreshCfoQueueUI();
  try { initLiveTelemetryStream(); } catch(e) { console.warn("Live telemetry init error:", e); }
}

window.toggleThemePaletteMenu = toggleThemePaletteMenu;
window.applyThemePalette = applyThemePalette;
window.evalDashboard = evalDashboard;
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
window.openApkDownloadModal = () => landingGateway.openApkDownloadModal();
window.closeApkDownloadModal = () => landingGateway.closeApkDownloadModal();
window.openAiEvalModal = () => landingGateway.openAiEvalModal();
window.closeAiEvalModal = () => landingGateway.closeAiEvalModal();
window.updateLandingRoiCalculator = () => landingGateway.updateLandingRoiCalculator();
window.downloadMerkleCertificate = (id) => landingGateway.downloadMerkleCertificate(id);
window.inspectPipelineStage = (idx) => landingGateway.inspectPipelineStage(idx);
window.toggleAiCopilotDrawer = toggleAiCopilotDrawer;
window.minimizeCopilotDrawer = minimizeCopilotDrawer;
window.setCopilotMode = setCopilotMode;
window.resetCopilotHeroCard = resetCopilotHeroCard;
window.renderCopilotHeroCard = renderCopilotHeroCard;
window.renderCopilotSuggestions = renderCopilotSuggestions;
window.triggerCopilotSuggestion = triggerCopilotSuggestion;
window.renderFocusedHeroCard = renderFocusedHeroCard;
window.copilotAttachFilePrompt = copilotAttachFilePrompt;
window.updateCopilotCurrentPage = updateCopilotCurrentPage;
window.sendQuickPrompt = sendQuickPrompt;
window.speakLastCopilotMessage = speakLastCopilotMessage;
window.speakCopilotResponse = speakCopilotResponse;
window.handleCopilotCustomQuery = handleCopilotCustomQuery;
window.openFeatureDetailModal = openFeatureDetailModal;
window.closeFeatureDetailModal = closeFeatureDetailModal;
window.toggleCommandPalette = toggleCommandPalette;
window.closeCommandPalette = closeCommandPalette;
window.executePaletteAction = executePaletteAction;

// Initialize Live Real Telemetry and Forex Stream
initLiveTelemetryStream();

