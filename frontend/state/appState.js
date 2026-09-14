/**
 * RazorRevive-OS Centralized State Management Store
 * Manages reactive UI state for tabs, bank switches, command palette, and guided tour.
 */

export const BANK_SWITCH_STATES = {
  HDFC: { name: "HDFC Bank UPI", switchId: "HDFC_CORE_01", state: "HEALTHY", sr: 98.4, latency: 145 },
  SBI: { name: "SBI Switch (U30)", switchId: "SBI_INB_04", state: "DEGRADED", sr: 78.2, latency: 890 },
  ICICI: { name: "ICICI Bank Rail", switchId: "ICIC_NODE_02", state: "HEALTHY", sr: 99.1, latency: 110 },
  AXIS: { name: "Axis Bank Mandates", switchId: "UTIB_MANDATE_01", state: "HEALTHY", sr: 97.6, latency: 190 },
  KOTAK: { name: "Kotak Mahindra", switchId: "KKBK_UPI_01", state: "HEALTHY", sr: 96.8, latency: 220 },
  PNB: { name: "Punjab National Bank", switchId: "PUNB_SWITCH_03", state: "HEALTHY", sr: 95.2, latency: 310 },
  YESB: { name: "Yes Bank PSP Hub", switchId: "YESB_HUB_01", state: "HEALTHY", sr: 97.9, latency: 175 }
};

export const TOUR_STEPS = [
  {
    target: "nav-overview",
    title: "1. Mission Control Overview",
    desc: "Welcome to OmniRevive-OS. This universal cockpit orchestrates real-time autonomous revenue recovery across Indian payment rails (Juspay, Cashfree, PhonePe, CRED, Razorpay)."
  },
  {
    target: "nav-fast_loop",
    title: "2. Fast-Loop Micro-Orchestrator",
    desc: "Executes sub-500ms synchronous retries with smart routing across NPCI rails, payment switches, and token remediation."
  },
  {
    target: "nav-card_tokens",
    title: "3. RBI Card Token Remediation",
    desc: "Detects token cryptogram desync, card lifecycle events, and performs zero-downtime card lifecycle provisioning."
  },
  {
    target: "nav-deep_loop",
    title: "4. Deep-Loop AI Voice & WhatsApp Agent",
    desc: "Engages B2B buyers with an autonomous Hinglish voice agent to resolve commercial objections, schedule PTPs, and send UPI links."
  },
  {
    target: "nav-cfo_approvals",
    title: "5. CFO Executive Gating & Zero-Trust",
    desc: "High-value invoice mutations and significant write-downs are gated behind Cedar zero-trust policies and explicit CFO digital sign-offs."
  },
  {
    target: "nav-audit_ledger",
    title: "6. SHA-256 Chained Audit Ledger",
    desc: "Every recovery decision and statutory mutation is cryptographically sealed into a verifiable SHA-256 blockchain ledger."
  },
  {
    target: "nav-benchmark",
    title: "7. 100-Case Production Benchmark Suite",
    desc: "Validates system recovery rate against held-out historical failure distributions with zero CAS or TRAI violations."
  }
];

export const CMDK_COMMANDS = [
  { id: "tab-overview", label: "Go to Mission Control Overview", icon: "📊", action: () => window.switchNavTab("overview") },
  { id: "tab-fast-loop", label: "Open Fast-Loop Sub-Second Engine", icon: "⚡", action: () => window.switchNavTab("fast_loop") },
  { id: "tab-deep-loop", label: "Open Deep-Loop B2B Voice & WhatsApp", icon: "🎙️", action: () => window.switchNavTab("deep_loop") },
  { id: "tab-cfo", label: "Open CFO Executive Approval Queue", icon: "🏛️", action: () => window.switchNavTab("cfo_approvals") },
  { id: "tab-card-tokens", label: "Inspect RBI Card Network Tokens", icon: "💳", action: () => window.switchNavTab("card_tokens") },
  { id: "tab-audit", label: "Verify Cryptographic Audit Ledger", icon: "🛡️", action: () => window.switchNavTab("audit_ledger") },
  { id: "tab-benchmark", label: "Run 100-Case Benchmark Suite", icon: "🎯", action: () => window.openDetailedBenchmarkSuite() },
  { id: "theme-toggle", label: "Toggle Dark / Light Mode", icon: "🌓", action: () => window.toggleThemeMode() },
  { id: "circuit-sbi", label: "Toggle SBI Circuit Breaker / Degraded Rail", icon: "🔌", action: () => window.toggleSbiCircuitBreaker() }
];

class AppStateManager {
  constructor() {
    this.currentTab = "overview";
    this.theme = localStorage.getItem("rr_theme") || "light";
    this.tourActive = false;
    this.currentTourIndex = 0;
    this.cmdkSelectedIndex = 0;
    this.filteredCmdkList = [...CMDK_COMMANDS];
  }

  setTab(tabName) {
    this.currentTab = tabName;
  }

  setTheme(theme) {
    this.theme = theme;
    localStorage.setItem("rr_theme", theme);
  }
}

export const appState = new AppStateManager();
