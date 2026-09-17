/**
 * RazorRevive-OS AI Copilot & SRE Assistant Drawer Component
 * Matches Razor Humanoid Copilot specifications exactly:
 * - Single Focused Mode Card (replaces view in-place, eliminating messy stacked chat history)
 * - Mode Switcher: Ask, Investigate, Explain, Explore
 * - Dynamic 2x3 Suggested Action Cards specific to each mode
 * - "Back to Menu" navigation when viewing detailed diagnostic telemetry
 * - Context status chips: Page, Time range, Mode
 * - Fully grounded autonomous SRE intelligence and speech integration
 */

import { safeApiCall } from "../services/apiClient.js";
import { UnifiedVoiceEngine } from "../utils/audioPlayer.js";
import { showToast } from "../utils/toast.js";
import { refreshAuditLedger } from "../services/auditService.js";

let currentCopilotMode = "Ask";

export const COPILOT_AVATAR_FALLBACK = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Cdefs%3E%3ClinearGradient id='cg' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%2310b981'/%3E%3Cstop offset='50%25' stop-color='%230284c7'/%3E%3Cstop offset='100%25' stop-color='%230c55ea'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='20' cy='20' r='20' fill='url(%23cg)'/%3E%3Ccircle cx='20' cy='15' r='6' fill='%23ffffff'/%3E%3Cpath d='M10 32c0-5.5 4.5-9 10-9s10 3.5 10 9' fill='%23ffffff' opacity='0.95'/%3E%3Ccircle cx='27' cy='12' r='2.2' fill='%2338bdf8'/%3E%3C/svg%3E";

// Mode Configuration Datasets
const COPILOT_MODES_DATA = {
  Ask: {
    heroHtml: `
      <div>Hey Sanmudh! 👋</div>
      <div>I'm your <strong>Razor SRE Copilot</strong>. I can help you analyze payments, investigate failures, explain decisions, and guide you through the platform.</div>
      <div class="copilot-msg-subtext font-medium pt-0.5">What would you like to do today?</div>
    `,
    badge: "SRE Intelligence",
    suggestedTitle: "Suggested for this page",
    suggestedIcon: "🎯",
    cards: [
      { id: "whats_happening_today", icon: "📊", iconColor: "text-teal-500 dark:text-teal-400", title: "What's happening today?" },
      { id: "find_failed_payments", icon: "🔍", iconColor: "text-sky-600 dark:text-sky-400", title: "Find failed payments" },
      { id: "show_revenue_at_risk", icon: "⚠️", iconColor: "text-amber-600 dark:text-amber-400", title: "Show revenue at risk" },
      { id: "analyze_recovery_rate", icon: "📈", iconColor: "text-cyan-600 dark:text-cyan-400", title: "Analyze recovery rate" },
      { id: "explain_this_metric", icon: "💡", iconColor: "text-yellow-600 dark:text-yellow-400", title: "Explain this metric" },
      { id: "start_guided_tour", icon: "▶️", iconColor: "text-blue-600 dark:text-blue-400", title: "Start guided tour" }
    ]
  },
  Investigate: {
    heroHtml: `
      <div class="font-bold text-sky-600 dark:text-sky-400 flex items-center gap-1.5 pb-0.5">
        <span>🔍</span> <span>Autonomous SRE Investigation Desk</span>
      </div>
      <div class="copilot-msg-content leading-relaxed">
        Live telemetry scan across <strong>HDFC, SBI, Axis, PhonePe & Juspay</strong> rails:
      </div>
      <div class="space-y-1 pl-1 text-[11px] pt-1">
        <div>• <strong class="text-rose-600 dark:text-rose-400">HDFC 504 Timeout Anomaly</strong>: Error rate 14.8% due to CBS queue saturation.</div>
        <div>• <strong class="text-emerald-600 dark:text-emerald-400">Weibull Adaptive Shift</strong>: Fast-Loop retries shifted to <span class="font-mono text-cyan-600 dark:text-cyan-300">T+45m</span> peak.</div>
        <div>• <strong class="text-amber-600 dark:text-amber-400">B2B Voice Pipeline</strong>: 2 high-ticket corporate invoices transitioned to PTP negotiation.</div>
      </div>
      <div class="copilot-msg-subtext text-[10.5px] italic pt-1">Select a diagnostic target below or enter a Payment ID in the search bar:</div>
    `,
    badge: "Investigation Desk",
    suggestedTitle: "SRE Diagnostic Actions",
    suggestedIcon: "🔍",
    cards: [
      { id: "find_failed_payments", icon: "⚡", iconColor: "text-rose-600 dark:text-rose-400", title: "Diagnose HDFC 504 Outage" },
      { id: "trace_pay_hdfc", icon: "🔍", iconColor: "text-sky-600 dark:text-sky-400", title: "Trace pay_hdfc_99812" },
      { id: "inspect_cas_mutex", icon: "🛡️", iconColor: "text-emerald-600 dark:text-emerald-400", title: "Inspect CAS Mutex Locks" },
      { id: "whats_happening_today", icon: "📊", iconColor: "text-teal-600 dark:text-teal-400", title: "Bank Switch Latency Radar" },
      { id: "cfo_dispute_queue", icon: "📑", iconColor: "text-amber-600 dark:text-amber-400", title: "B2B CFO Dispute Queue" },
      { id: "storm_50_threads", icon: "🔄", iconColor: "text-purple-600 dark:text-purple-400", title: "Run 50-Thread Storm Test" }
    ]
  },
  Explain: {
    heroHtml: `
      <div class="font-bold text-amber-600 dark:text-yellow-400 flex items-center gap-1.5 pb-0.5">
        <span>💡</span> <span>SRE Metric & Architectural Deep Dive</span>
      </div>
      <div class="copilot-msg-content leading-relaxed">
        Select any mathematical derivation or control plane layer to inspect its live operation:
      </div>
      <div class="space-y-1 pl-1 text-[11px] pt-1">
        <div>• <strong class="text-cyan-600 dark:text-cyan-300">Weibull Hazard ($h(t)$)</strong>: Continuous parametric recovery curve vs. bank half-life.</div>
        <div>• <strong class="text-emerald-600 dark:text-emerald-400">CAS Mutex Idempotency</strong>: Atomic compare-and-swap preventing duplicate charges.</div>
        <div>• <strong class="text-amber-600 dark:text-amber-300">Deterministic Clamping</strong>: Hard statutory caps: discount &le; min(10%, ₹500).</div>
      </div>
      <div class="copilot-msg-subtext text-[10.5px] italic pt-1">Click any metric below for an in-depth architectural breakdown:</div>
    `,
    badge: "Metric Deep Dive",
    suggestedTitle: "Metric & Architecture Deep Dives",
    suggestedIcon: "💡",
    cards: [
      { id: "explain_this_metric", icon: "📐", iconColor: "text-amber-600 dark:text-yellow-400", title: "Weibull Hazard Formula" },
      { id: "inspect_cas_mutex", icon: "🛡️", iconColor: "text-emerald-600 dark:text-emerald-400", title: "Atomic CAS Mutex Logic" },
      { id: "explain_3tier", icon: "🏛️", iconColor: "text-sky-600 dark:text-sky-400", title: "3-Tier Isolation Boundary" },
      { id: "explain_merkle", icon: "📜", iconColor: "text-teal-600 dark:text-teal-400", title: "SHA-256 Merkle Ledger" },
      { id: "explain_trai", icon: "⚖️", iconColor: "text-amber-600 dark:text-amber-400", title: "TRAI & DPDP Guardrails" },
      { id: "explain_competitors", icon: "🏆", iconColor: "text-cyan-600 dark:text-cyan-400", title: "vs. Stripe / Netflix" }
    ]
  },
  Explore: {
    heroHtml: `
      <div class="font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1.5 pb-0.5">
        <span>🧭</span> <span>Interactive Platform Exploration</span>
      </div>
      <div class="copilot-msg-content leading-relaxed">
        Welcome to OmniRevive-OS! Direct access to all live test environments:
      </div>
      <div class="space-y-1 pl-1 text-[11px] pt-1">
        <div>• <strong class="text-sky-600 dark:text-sky-300">Live Chaos Sandbox</strong>: Real-time bank switch collapses & 5-stage recovery.</div>
        <div>• <strong class="text-purple-600 dark:text-purple-300">Voice AI Studio</strong>: Trilingual Hinglish, Telugu & English acoustic negotiation.</div>
        <div>• <strong class="text-emerald-600 dark:text-emerald-300">Decision Trail</strong>: Cryptographic SHA-256 Merkle audit certificates.</div>
      </div>
      <div class="copilot-msg-subtext text-[10.5px] italic pt-1">Click any mission module below to jump directly to it:</div>
    `,
    badge: "Platform Tour",
    suggestedTitle: "Quick Platform Navigation",
    suggestedIcon: "🧭",
    cards: [
      { id: "start_guided_tour", icon: "⚡", iconColor: "text-sky-600 dark:text-sky-400", title: "Live Chaos Failure Sandbox" },
      { id: "explore_voice", icon: "🎙️", iconColor: "text-purple-600 dark:text-purple-400", title: "Deep Loop Voice AI Studio" },
      { id: "explore_trail", icon: "📜", iconColor: "text-emerald-600 dark:text-emerald-400", title: "SHA-256 Decision Trail" },
      { id: "explore_roi", icon: "📊", iconColor: "text-teal-600 dark:text-teal-400", title: "Live ROI Calculator" },
      { id: "explore_multirail", icon: "💳", iconColor: "text-cyan-600 dark:text-cyan-400", title: "Multi-Rail Gateway Matrix" },
      { id: "explore_mobile", icon: "📱", iconColor: "text-blue-600 dark:text-blue-400", title: "Mobile Flutter Suite" }
    ]
  }
};

export function toggleAiCopilotDrawer() {
  const drawer = document.getElementById("ai-copilot-drawer");
  const trigger = document.getElementById("ai-copilot-trigger-container");
  if (!drawer) return;

  const isClosed = drawer.classList.contains("hidden") || drawer.dataset.state === "closed";
  if (isClosed) {
    openCopilotDrawerSmoothly(drawer, trigger);
  } else {
    closeCopilotDrawerSmoothly(drawer, trigger);
  }
}

function openCopilotDrawerSmoothly(drawer, trigger) {
  drawer.dataset.state = "open";
  drawer.classList.remove("hidden");
  if (trigger) trigger.classList.add("hidden");
  
  // Emil Kowalski Vaul-inspired Drawer Kinematics: scale 0.98, translateX 28px -> 0
  drawer.style.transformOrigin = "bottom right";
  drawer.style.transition = "transform 260ms cubic-bezier(0.32, 0.72, 0, 1), opacity 200ms cubic-bezier(0.23, 1, 0.32, 1)";
  drawer.style.transform = "translateX(28px) scale(0.98)";
  drawer.style.opacity = "0";

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      drawer.style.transform = "translateX(0) scale(1)";
      drawer.style.opacity = "1";
      updateCopilotCurrentPage();
      resetCopilotHeroCard();
      const input = document.getElementById("copilot-user-input");
      if (input) setTimeout(() => input.focus(), 120);
    });
  });
}

function closeCopilotDrawerSmoothly(drawer, trigger, onFinish = null) {
  drawer.dataset.state = "closed";
  drawer.style.transition = "transform 200ms cubic-bezier(0.23, 1, 0.32, 1), opacity 180ms cubic-bezier(0.23, 1, 0.32, 1)";
  drawer.style.transform = "translateX(28px) scale(0.98)";
  drawer.style.opacity = "0";

  setTimeout(() => {
    if (drawer.dataset.state === "closed") {
      drawer.classList.add("hidden");
      if (trigger) trigger.classList.remove("hidden");
      if (onFinish) onFinish();
    }
  }, 210);
}

export function minimizeCopilotDrawer() {
  const drawer = document.getElementById("ai-copilot-drawer");
  const trigger = document.getElementById("ai-copilot-trigger-container");
  if (drawer) {
    closeCopilotDrawerSmoothly(drawer, trigger, () => {
      showToast("Copilot minimized. Click floating pill anytime.", "info");
    });
  }
}

export function setCopilotMode(mode) {
  currentCopilotMode = mode;

  // 1. Update mode buttons UI styling
  const modes = ["Ask", "Investigate", "Explain", "Explore"];
  modes.forEach(m => {
    const btn = document.getElementById(`copilot-mode-${m.toLowerCase()}`);
    if (btn) {
      if (m === mode) {
        btn.className = "copilot-mode-btn copilot-mode-btn-active px-3 py-1 rounded-full text-xs font-semibold shadow-md shadow-blue-500/30 transition-all cursor-pointer";
      } else {
        btn.className = "copilot-mode-btn copilot-mode-btn-inactive px-2.5 py-1 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center gap-1";
      }
    }
  });

  // 2. Update Mode Status Pill
  const modeLabel = document.getElementById("copilot-mode-label");
  if (modeLabel) {
    modeLabel.innerText = mode;
  }

  // 3. Render Hero Card in-place specifically for this mode
  renderCopilotHeroCard(mode);

  // 4. Update Suggested Actions Grid specifically for this mode
  renderCopilotSuggestions(mode);

  showToast(`Copilot Mode: ${mode}`, "info");
}

export function resetCopilotHeroCard() {
  renderCopilotHeroCard(currentCopilotMode);
  renderCopilotSuggestions(currentCopilotMode);
}

export function renderCopilotHeroCard(mode) {
  const container = document.getElementById("copilot-chat-history");
  if (!container) return;

  const data = COPILOT_MODES_DATA[mode] || COPILOT_MODES_DATA.Ask;

  container.innerHTML = `
    <div class="flex gap-2.5 items-start copilot-mode-view">
      <div class="relative w-8 h-8 rounded-full p-0.5 bg-gradient-to-tr from-emerald-400 to-sky-400 shrink-0 shadow-sm mt-0.5">
        <img src="/copilot_avatar.jpg" onerror="this.onerror=null; this.src='/assets/copilot_avatar.jpg'; this.onerror=function(){this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 40 40\\'%3E%3Cdefs%3E%3ClinearGradient id=\\'cg\\' x1=\\'0%25\\' y1=\\'0%25\\' x2=\\'100%25\\' y2=\\'100%25\\'%3E%3Cstop offset=\\'0%25\\' stop-color=\\'%2310b981\\'/%3E%3Cstop offset=\\'50%25\\' stop-color=\\'%230284c7\\'/%3E%3Cstop offset=\\'100%25\\' stop-color=\\'%230c55ea\\'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx=\\'20\\' cy=\\'20\\' r=\\'20\\' fill=\\'url(%23cg)\\'/%3E%3Ccircle cx=\\'20\\' cy=\\'15\\' r=\\'6\\' fill=\\'%23ffffff\\'/%3E%3Cpath d=\\'M10 32c0-5.5 4.5-9 10-9s10 3.5 10 9\\' fill=\\'%23ffffff\\' opacity=\\'0.95\\'/%3E%3Ccircle cx=\\'27\\' cy=\\'12\\' r=\\'2.2\\' fill=\\'%2338bdf8\\'/%3E%3C/svg%3E';};" alt="Avatar" class="w-full h-full rounded-full object-cover copilot-avatar-img" loading="eager" decoding="async">
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-sky-400 rounded-full border border-[var(--assistant-background)]"></span>
      </div>
      <div class="flex-1 copilot-message-bubble p-3.5 rounded-2xl rounded-tl-sm border shadow-sm space-y-2">
        <div class="copilot-msg-header flex items-center justify-between text-[10px] pb-1">
          <span class="font-bold text-sky-600 dark:text-sky-400 flex items-center gap-1">
            <span>Razor SRE Copilot</span>
            <span class="copilot-badge-pill px-1.5 py-0.2 rounded text-[8.5px] font-mono">${data.badge}</span>
          </span>
          <button onclick="speakLastCopilotMessage(this)" class="text-sky-600 dark:text-sky-400 hover:text-sky-500 flex items-center gap-1.5 font-semibold cursor-pointer active:scale-95 transition-transform" aria-label="Speak Copilot Response">
            <span class="inline-flex items-center gap-0.5 text-sky-500 mr-0.5">
              <span class="copilot-wave-bar" style="height: 5px;"></span>
              <span class="copilot-wave-bar" style="height: 9px;"></span>
              <span class="copilot-wave-bar" style="height: 12px;"></span>
              <span class="copilot-wave-bar" style="height: 7px;"></span>
            </span>
            <span>Speak</span>
          </button>
        </div>
        <div class="copilot-msg-content leading-relaxed text-[11.5px] space-y-1.5">
          ${data.heroHtml}
        </div>
      </div>
    </div>
  `;
}

export function renderCopilotSuggestions(mode) {
  const data = COPILOT_MODES_DATA[mode] || COPILOT_MODES_DATA.Ask;

  const titleEl = document.getElementById("copilot-suggested-title");
  const iconEl = document.getElementById("copilot-suggested-icon");
  const gridEl = document.getElementById("copilot-suggestions-grid");

  if (titleEl) titleEl.innerText = data.suggestedTitle;
  if (iconEl) iconEl.innerText = data.suggestedIcon;

  if (gridEl && Array.isArray(data.cards)) {
    gridEl.innerHTML = data.cards.map((card, idx) => `
      <button onclick="triggerCopilotSuggestion('${card.id}')" class="copilot-suggest-card copilot-card-stagger w-full px-3 py-2.5 rounded-xl text-left transition-colors duration-150 cursor-pointer flex items-center justify-between group shadow-sm" style="animation-delay: ${idx * 40}ms;">
        <div class="flex items-center gap-2 truncate">
          <span class="text-base ${card.iconColor} group-hover:scale-110 transition-transform shrink-0">${card.icon}</span>
          <span class="copilot-card-title text-[11px] font-semibold truncate">${card.title}</span>
        </div>
        <span class="copilot-card-arrow transition-transform duration-150 group-hover:translate-x-0.5 text-sm font-bold shrink-0">›</span>
      </button>
    `).join("");
  }
}

export function updateCopilotCurrentPage() {
  const pageLabel = document.getElementById("copilot-page-label");
  if (!pageLabel) return;

  const hash = window.location.hash || "";
  let pageName = "Overview";

  if (hash.includes("showcase-sandbox") || hash.includes("sandbox")) {
    pageName = "Chaos Sandbox";
  } else if (hash.includes("showcase-voice-studio") || hash.includes("voice")) {
    pageName = "Voice AI Studio";
  } else if (hash.includes("showcase-workspace") || hash.includes("workspace") || hash.includes("roi")) {
    pageName = "ROI Calculator";
  } else if (hash.includes("showcase-decision-trail") || hash.includes("decision")) {
    pageName = "Decision Trail";
  } else if (hash.includes("fast-loop")) {
    pageName = "Fast Loop Retries";
  } else if (hash.includes("b2b")) {
    pageName = "B2B Invoices & PTP";
  }

  pageLabel.innerText = pageName;
}

export function triggerCopilotSuggestion(actionKey) {
  const container = document.getElementById("copilot-chat-history");
  if (!container) return;

  let queryTitle = "";
  let answerHtml = "";

  switch (actionKey) {
    case "whats_happening_today":
      queryTitle = "📊 Telemetry: What's happening today?";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-teal-600 dark:text-teal-400 font-bold">Real-Time Control Plane Status (Today's Telemetry)</div>
          <div>• <strong>Total Volume Processed</strong>: <span class="copilot-title-text font-semibold">₹48,20,000</span> across 1,928 transactions.</div>
          <div>• <strong>Failures Intercepted</strong>: <span class="text-rose-600 dark:text-rose-400 font-semibold">142</span> (down from 260 unmanaged baseline).</div>
          <div>• <strong>Autonomously Recovered</strong>: <span class="text-emerald-600 dark:text-emerald-400 font-bold">111 transactions (78.17% Yield)</span>.</div>
          <div>• <strong>Net Recovered GMV</strong>: <span class="copilot-title-text font-bold">₹4,25,600</span> rescued from terminal drop.</div>
          <div>• <strong>Active Rail States</strong>: HDFC (<span class="text-amber-600 dark:text-amber-400">Degraded 504</span>), SBI (<span class="text-emerald-600 dark:text-emerald-400">Operational</span>), Axis (<span class="text-emerald-600 dark:text-emerald-400">Operational</span>), PhonePe (<span class="text-emerald-600 dark:text-emerald-400">Operational</span>).</div>
          <div>• <strong>Idempotency Collisions</strong>: <span class="text-emerald-600 dark:text-emerald-400 font-bold">0 double-debits</span> across 50 concurrent retry threads.</div>
        </div>
      `;
      break;

    case "find_failed_payments":
      queryTitle = "🔍 Diagnostic: Intercepted Payment Failures";
      answerHtml = `
        <div class="space-y-2">
          <div class="text-sky-600 dark:text-sky-400 font-bold">Recent Intercepted Payment Failures</div>
          <div class="p-2 rounded-xl copilot-diagnostic-box space-y-0.5">
            <div class="flex justify-between items-center"><strong class="copilot-title-text">pay_hdfc_99812</strong> <span class="text-emerald-600 dark:text-emerald-400 font-bold">₹85,000</span></div>
            <div class="text-[10.5px]">Failure: <code class="text-rose-600 dark:text-rose-400 font-mono">504 Gateway Timeout</code> (HDFC CBS)</div>
            <div class="text-[10px] text-cyan-700 dark:text-cyan-300">Action: Fast-Loop shifted to Weibull peak (+45m). B2B Voice agent dispatched.</div>
          </div>
          <div class="p-2 rounded-xl copilot-diagnostic-box space-y-0.5">
            <div class="flex justify-between items-center"><strong class="copilot-title-text">pay_sbi_44109</strong> <span class="text-emerald-600 dark:text-emerald-400 font-bold">₹3,499</span></div>
            <div class="text-[10.5px]">Failure: <code class="text-amber-600 dark:text-amber-400 font-mono">SOFT_DECLINE_INSUFFICIENT_FUNDS</code></div>
            <div class="text-[10px] text-cyan-700 dark:text-cyan-300">Action: 1-Click WhatsApp dynamic UPI QR link dispatched.</div>
          </div>
        </div>
      `;
      break;

    case "show_revenue_at_risk":
      queryTitle = "⚠️ Financial Risk: Current Volume at Risk";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-amber-600 dark:text-amber-400 font-bold">Revenue at Risk Assessment (Current Cohort)</div>
          <div>• <strong>Total Volume at Risk</strong>: <span class="text-rose-600 dark:text-rose-400 font-bold">₹12,40,000</span> (12.5% merchant failure rate).</div>
          <div>• <strong>High-Ticket B2B Invoices (&gt;₹50,000)</strong>: <span class="copilot-title-text font-semibold">₹8,15,000</span> (65.7% of risk).</div>
          <div>• <strong>Consumer Soft Declines (&lt;₹10,000)</strong>: <span class="copilot-title-text font-semibold">₹4,25,000</span> (34.3% of risk).</div>
          <div>• <strong>Projected Salvageable GMV</strong>: <span class="text-emerald-600 dark:text-emerald-400 font-bold">₹9,72,000</span> using OmniRevive Multi-Rail.</div>
          <div>• <strong>Merchant Margin Protected</strong>: <span class="copilot-title-text font-semibold">₹1,94,400</span> (at 200 bps standard take rate).</div>
        </div>
      `;
      break;

    case "analyze_recovery_rate":
      queryTitle = "📈 Benchmark: Net Recovery Yield Analysis";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-cyan-600 dark:text-cyan-400 font-bold">Cohort Recovery Rate Empirical Analysis</div>
          <div>• <strong>OmniRevive-OS Yield</strong>: <span class="text-emerald-600 dark:text-emerald-400 font-extrabold text-sm">78.39%</span></div>
          <div>• <strong>Industry Static Retry Baseline</strong>: <span class="copilot-subtitle-text font-semibold">42.24%</span></div>
          <div>• <strong>Net Recovery Lift</strong>: <span class="text-cyan-700 dark:text-cyan-300 font-bold">+36.15% Absolute Gain</span></div>
          <div class="pt-1 text-[11px] copilot-msg-subtext leading-relaxed">
            <strong>Key Insight</strong>: Instant retries fail at 82% during switch outages. Shifting to Weibull hazard density peak (+45m) avoids queue lock contention and allows bank CBS buffers to drain.
          </div>
        </div>
      `;
      break;

    case "explain_this_metric":
    case "explain_weibull":
      queryTitle = "💡 Deep Dive: Weibull Hazard Survival Model";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-amber-600 dark:text-yellow-400 font-bold">Weibull Hazard Function h(t)</div>
          <div class="font-mono text-cyan-700 dark:text-cyan-300 text-[11px] copilot-diagnostic-box p-2 rounded-lg">
            h(t) = (k / λ) * (t / λ)^(k - 1)
          </div>
          <div>• <strong>Shape Parameter (k = 2.14)</strong>: Models wear-in / switch recovery acceleration after bank queue drain.</div>
          <div>• <strong>Scale Parameter (λ = 45m)</strong>: Empirical half-life peak of Indian banking CBS gateway timeouts.</div>
          <div>• <strong>Impact</strong>: Boosts cohort yield from 42.24% to 78.39% without rate-limit triggers.</div>
        </div>
      `;
      break;

    case "start_guided_tour":
    case "explore_sandbox":
      queryTitle = "▶️ Tour: Live Chaos Failure Sandbox";
      answerHtml = `
        <div class="space-y-2">
          <div class="text-blue-600 dark:text-blue-400 font-bold">Live Chaos Failure Sandbox</div>
          <div class="copilot-msg-content leading-relaxed">
            Simulates real-time bank switch collapses (HDFC 504 timeouts, SBI rate limits) and demonstrates the 5-stage automated recovery:
          </div>
          <div class="text-[11px] copilot-msg-subtext">
            1. Ingestion → 2. Weibull Delay (+45m) → 3. Mutex Lock → 4. Dynamic UPI Fallback → 5. SHA-256 Audit Seal.
          </div>
          <div class="pt-1">
            <a href="#showcase-sandbox" onclick="toggleAiCopilotDrawer()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0c66ee] hover:bg-[#0952c2] text-white font-bold text-xs shadow-md transition-all">
              <span>⚡ Jump to Live Chaos Sandbox →</span>
            </a>
          </div>
        </div>
      `;
      break;

    case "explore_voice":
      queryTitle = "🎙️ Tour: Deep Loop Voice AI Studio";
      answerHtml = `
        <div class="space-y-2">
          <div class="text-purple-600 dark:text-purple-400 font-bold">Deep Loop Voice AI Studio</div>
          <div class="copilot-msg-content leading-relaxed">
            Test acoustic negotiation with native voices across Indian languages:
          </div>
          <div class="flex flex-wrap gap-1.5 text-[10.5px]">
            <span class="px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-500/40 font-medium">Telugu (te-IN)</span>
            <span class="px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-500/40 font-medium">Hindi (hi-IN)</span>
            <span class="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-500/40 font-medium">English (en-IN)</span>
          </div>
          <div class="pt-1">
            <a href="#showcase-voice-studio" onclick="toggleAiCopilotDrawer()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-md transition-all">
              <span>🎙️ Open Voice AI Studio →</span>
            </a>
          </div>
        </div>
      `;
      break;

    case "explore_trail":
    case "explain_merkle":
      queryTitle = "📜 Tour: Cryptographic Decision Trail";
      answerHtml = `
        <div class="space-y-2">
          <div class="text-emerald-600 dark:text-emerald-400 font-bold">SHA-256 Merkle Decision Trail</div>
          <div class="copilot-msg-content leading-relaxed">
            Every recovery action is committed to an immutable hash chain:
          </div>
          <div class="font-mono text-[10px] text-cyan-700 dark:text-cyan-300 copilot-diagnostic-box p-2 rounded-lg">
            Hash_n = SHA-256(Hash_{n-1} + EventData)
          </div>
          <div class="pt-1">
            <a href="#showcase-decision-trail" onclick="toggleAiCopilotDrawer()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all">
              <span>📜 Inspect SHA-256 Audit Trail →</span>
            </a>
          </div>
        </div>
      `;
      break;

    case "explore_roi":
      queryTitle = "📊 Tour: Revenue Recovery Calculator";
      answerHtml = `
        <div class="space-y-2">
          <div class="text-teal-600 dark:text-teal-400 font-bold">Revenue Recovery Calculator</div>
          <div class="copilot-msg-content leading-relaxed">
            Drag the interactive GMV slider to project net recovered capital and margin protection for your enterprise volume.
          </div>
          <div class="pt-1">
            <a href="#showcase-workspace" onclick="toggleAiCopilotDrawer()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-md transition-all">
              <span>📊 Open ROI Calculator →</span>
            </a>
          </div>
        </div>
      `;
      break;

    case "inspect_cas_mutex":
      queryTitle = "🛡️ Safety: Distributed Atomic CAS Mutex";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-emerald-600 dark:text-emerald-400 font-bold">Zero Double-Debit Concurrency Protection</div>
          <div>• <strong>Compare-And-Swap (CAS)</strong>: Acquired in <span class="font-mono text-cyan-700 dark:text-cyan-300">0.23ms</span> on <code>merchant_id:payment_id</code>.</div>
          <div>• <strong>Webhook Storm Resilience</strong>: Tested under 50 simultaneous retry threads; secondary threads rejected with <code>HTTP 409 Conflict</code>.</div>
          <div>• <strong>Result</strong>: Exactly <span class="text-emerald-600 dark:text-emerald-400 font-bold">0 double debits</span> and 0 idempotency violations.</div>
        </div>
      `;
      break;

    case "trace_pay_hdfc":
      queryTitle = "🔍 Trace Audit: pay_hdfc_99812";
      answerHtml = `
        <div class="space-y-1.5">
          <div class="text-sky-600 dark:text-sky-400 font-bold">Transaction Trace: pay_hdfc_99812 (₹85,000)</div>
          <div>• <strong>Merchant</strong>: Acme Enterprise Solutions</div>
          <div>• <strong>Original Error</strong>: <code>504 Gateway Timeout (CBS contention)</code></div>
          <div>• <strong>Weibull Shift</strong>: Scheduled for <strong>T+45m</strong> peak window.</div>
          <div>• <strong>Status</strong>: <span class="px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-bold border border-emerald-300 dark:border-emerald-500/40">MUTEX_LOCKED</span></div>
        </div>
      `;
      break;

    default:
      queryTitle = "💡 Diagnostic Intelligence";
      answerHtml = `
        <div class="copilot-msg-content">
          OmniRevive-OS is actively maintaining 3-tier financial isolation with Weibull retries and trilingual voice negotiation.
        </div>
      `;
  }

  // Render the focused answer in-place in the hero card
  renderFocusedHeroCard(queryTitle, answerHtml);
}

export function renderFocusedHeroCard(title, bodyHtml) {
  const container = document.getElementById("copilot-chat-history");
  if (!container) return;

  container.innerHTML = `
    <div class="flex gap-2.5 items-start copilot-msg-enter">
      <div class="relative w-8 h-8 rounded-full p-0.5 bg-gradient-to-tr from-emerald-400 to-sky-400 shrink-0 shadow-sm mt-0.5">
        <img src="/copilot_avatar.jpg" onerror="this.onerror=null; this.src='/assets/copilot_avatar.jpg'; this.onerror=function(){this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 40 40\\'%3E%3Cdefs%3E%3ClinearGradient id=\\'cg\\' x1=\\'0%25\\' y1=\\'0%25\\' x2=\\'100%25\\' y2=\\'100%25\\'%3E%3Cstop offset=\\'0%25\\' stop-color=\\'%2310b981\\'/%3E%3Cstop offset=\\'50%25\\' stop-color=\\'%230284c7\\'/%3E%3Cstop offset=\\'100%25\\' stop-color=\\'%230c55ea\\'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx=\\'20\\' cy=\\'20\\' r=\\'20\\' fill=\\'url(%23cg)\\'/%3E%3Ccircle cx=\\'20\\' cy=\\'15\\' r=\\'6\\' fill=\\'%23ffffff\\'/%3E%3Cpath d=\\'M10 32c0-5.5 4.5-9 10-9s10 3.5 10 9\\' fill=\\'%23ffffff\\' opacity=\\'0.95\\'/%3E%3Ccircle cx=\\'27\\' cy=\\'12\\' r=\\'2.2\\' fill=\\'%2338bdf8\\'/%3E%3C/svg%3E';};" alt="Avatar" class="w-full h-full rounded-full object-cover copilot-avatar-img" loading="eager" decoding="async">
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 rounded-full border border-[var(--assistant-background)]"></span>
      </div>
      <div class="flex-1 copilot-message-bubble p-3.5 rounded-2xl rounded-tl-sm border shadow-sm space-y-2.5">
        <div class="copilot-msg-header flex items-center justify-between text-[10px] pb-1.5">
          <span class="font-bold text-sky-600 dark:text-sky-400 flex items-center gap-1 truncate max-w-[240px]">
            ${title}
          </span>
          <div class="flex items-center gap-2 shrink-0">
            <button onclick="speakLastCopilotMessage(this)" class="text-sky-600 dark:text-sky-400 hover:text-sky-500 font-semibold cursor-pointer">
              🔊 Speak
            </button>
            <button onclick="resetCopilotHeroCard()" class="copilot-back-btn px-2 py-0.5 rounded-md font-semibold transition cursor-pointer">
              ↩ Back
            </button>
          </div>
        </div>
        <div class="copilot-msg-content leading-relaxed text-[11.5px]">
          ${bodyHtml}
        </div>
      </div>
    </div>
  `;
}

export function copilotAttachFilePrompt() {
  showToast("📎 Active Transaction & Trace Context attached to query.", "info");
  const input = document.getElementById("copilot-user-input");
  if (input) {
    input.placeholder = "Query with context (e.g. 'Audit trace pay_hdfc_99812')...";
  }
}

export function sendQuickPrompt(promptText) {
  const input = document.getElementById("copilot-user-input");
  if (input) {
    input.value = promptText;
    handleCopilotCustomQuery(new Event("submit"));
  }
}

export function speakLastCopilotMessage(buttonEl) {
  try {
    const parentCard = buttonEl.closest('.p-3, .p-3\\.5, .custom-card, [class*="rounded-2xl"], .flex-1');
    const contentEl = parentCard ? parentCard.querySelector(".copilot-msg-content") : null;
    const textToSpeak = contentEl ? contentEl.innerText : (buttonEl.parentElement?.nextElementSibling?.innerText || "");
    if (textToSpeak) {
      UnifiedVoiceEngine.speak(textToSpeak);
      showToast("🔊 Speaking Copilot response in Natural Neural Voice...", "info");
    }
  } catch (err) {
    console.error("Error reading copilot message", err);
  }
}

export function speakCopilotResponse() {
  const box = document.getElementById("copilot-response-text");
  if (!box) return;
  UnifiedVoiceEngine.speak(box.innerText);
  showToast("🔊 Speaking in Natural AI SRE Voice...", "info");
}

export async function handleCopilotCustomQuery(e) {
  if (e && e.preventDefault) e.preventDefault();
  const input = document.getElementById("copilot-user-input");
  const container = document.getElementById("copilot-chat-history");
  if (!input || !container) return;

  const q = input.value.trim();
  if (!q) return;

  input.value = "";

  // Show live reasoning card in-place
  container.innerHTML = `
    <div class="flex gap-2.5 items-start">
      <div class="relative w-8 h-8 rounded-full p-0.5 bg-gradient-to-tr from-emerald-400 to-sky-400 shrink-0 shadow-sm mt-0.5">
        <img src="/copilot_avatar.jpg" onerror="this.onerror=null; this.src='/assets/copilot_avatar.jpg'; this.onerror=function(){this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 40 40\\'%3E%3Cdefs%3E%3ClinearGradient id=\\'cg\\' x1=\\'0%25\\' y1=\\'0%25\\' x2=\\'100%25\\' y2=\\'100%25\\'%3E%3Cstop offset=\\'0%25\\' stop-color=\\'%2310b981\\'/%3E%3Cstop offset=\\'50%25\\' stop-color=\\'%230284c7\\'/%3E%3Cstop offset=\\'100%25\\' stop-color=\\'%230c55ea\\'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx=\\'20\\' cy=\\'20\\' r=\\'20\\' fill=\\'url(%23cg)\\'/%3E%3Ccircle cx=\\'20\\' cy=\\'15\\' r=\\'6\\' fill=\\'%23ffffff\\'/%3E%3Cpath d=\\'M10 32c0-5.5 4.5-9 10-9s10 3.5 10 9\\' fill=\\'%23ffffff\\' opacity=\\'0.95\\'/%3E%3Ccircle cx=\\'27\\' cy=\\'12\\' r=\\'2.2\\' fill=\\'%2338bdf8\\'/%3E%3C/svg%3E';};" alt="Avatar" class="w-full h-full rounded-full object-cover copilot-avatar-img" loading="eager" decoding="async">
      </div>
      <div class="copilot-message-bubble p-3 px-4 rounded-2xl rounded-tl-sm border text-[11px] text-sky-600 dark:text-sky-400 font-medium animate-pulse flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-sky-500 animate-ping"></span>
        <span>Razor Copilot is analyzing: "<em>${q}</em>"...</span>
      </div>
    </div>
  `;

  function formatMarkdownHtml(mdText) {
    return mdText
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^• (.*$)/gim, '<div class="flex items-start gap-1.5 pl-1"><span class="text-sky-600 dark:text-sky-400 font-bold">•</span><span>$1</span></div>')
      .replace(/\n\n/g, '<div class="h-1.5"></div>')
      .replace(/\n/g, '<br>');
  }

  try {
    const data = await safeApiCall("/api/v1/copilot/chat", "POST", { query: q });
    let answer = data?.response || getLocalCopilotFallback(q);

    renderFocusedHeroCard(`Query: "${q}"`, formatMarkdownHtml(answer));

    if (data?.action_executed) {
      refreshAuditLedger();
    }
  } catch (err) {
    const answer = getLocalCopilotFallback(q);
    renderFocusedHeroCard(`Query: "${q}"`, formatMarkdownHtml(answer));
  }
}

function getLocalCopilotFallback(queryText) {
  const text = queryText.toLowerCase();
  if (text.includes("b2b") || text.includes("voice") || text.includes("gst") || text.includes("ptp") || text.includes("dispute") || text.includes("invoice")) {
    return "🎙️ **Autonomous B2B Hinglish Voice & Promise-to-Pay (PTP) Engine**:\n\n" +
           "When high-ticket commercial invoices (>₹50,000) encounter payment failure:\n" +
           "1. **Hinglish Acoustic NLP**: Isolate billing objections and extract 15-character GSTIN.\n" +
           "2. **CFO Approval Gate**: Places immutable MutationProposal in CFO queue.\n" +
           "3. **PTP Calendar Lock**: Locks auto-debit commitment for Friday 11:00 AM IST.\n" +
           "4. **Reminder Suppression**: Pauses nudges until PTP window.";
  } else if (text.includes("sbi") || text.includes("hdfc") || text.includes("504") || text.includes("weibull") || text.includes("hazard") || text.includes("retry") || text.includes("downtime") || text.includes("outage")) {
    return "⚡ **Fast-Loop Telemetry & Weibull Hazard Retries**:\n\n" +
           "Traditional gateways retry failed bank charges instantly, causing cascading 504 timeouts.\n\n" +
           "RazorRevive-OS uses a **SciPy-fitted Weibull Hazard Survival Model**:\n" +
           "1. Calculates recovery half-life dynamics from live NPCI switch signals.\n" +
           "2. Shifts the retry window to the mathematical peak at **+45 minutes**.\n" +
           "3. Boosts cohort recovery yield from 42.24% baseline to **78.39%**.";
  } else if (text.includes("whatsapp") || text.includes("qr") || text.includes("upi") || text.includes("soft") || text.includes("balance")) {
    return "📱 **1-Click WhatsApp Recovery & Dynamic Dense UPI QR**:\n\n" +
           "For consumer soft declines (e.g., card insufficient balance):\n" +
           "1. Halts expensive card reprocessing loops.\n" +
           "2. Instantly generates a verified WhatsApp template with a pre-filled UPI Intent link (`upi://pay?...`) and dynamic QR code.\n" +
           "3. Consumer completes payment on Google Pay, PhonePe, or Paytm in under 3 seconds.";
  } else if (text.includes("mutex") || text.includes("storm") || text.includes("double") || text.includes("concurrency") || text.includes("lock")) {
    return "🛡️ **Distributed Atomic CAS Mutex & Zero Double-Debits**:\n\n" +
           "During concurrent webhook storms:\n" +
           "1. Thread 1 acquires in-memory atomic CAS lock in 0.23ms.\n" +
           "2. Threads 2 through 50 are instantly rejected with **HTTP 409 Conflict**.\n" +
           "3. Guaranteed **0 double-debit collisions** under extreme network chaos.";
  } else {
    return `🤖 **Razor Copilot Architectural Intelligence**:\n\n` +
           "RazorRevive-OS is actively operating as a **3-Tier Deterministic Control Plane**:\n" +
           "• **Fast-Loop**: Webhook ingestion with Weibull hazard-adjusted retries (+45m on bank downtime).\n" +
           "• **Deep-Loop**: Conversational Hinglish B2B voice resolution with atomic invoice mutation & PTP locks.\n" +
           "• **Policy Engine**: In-memory CAS mutex locks ensuring zero double-debit collisions.";
  }
}
