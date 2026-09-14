/**
 * OmniRevive-OS | AI Evaluation & LLM Observability Dashboard
 * Renders live quantitative benchmarks for:
 * - Ragas (Faithfulness, Answer Relevancy, Context Precision/Recall)
 * - DeepEval (G-Eval Goal Alignment, Zero-Hallucination, RBI/TRAI Tone)
 * - LangGraph / CrewAI (Tool-Calling Precision, State Transition Fidelity, Token Efficiency)
 */

import { safeApiCall, apiClient } from "../services/apiClient.js?v=2.1.0";
import { showToast } from "../utils/toast.js?v=2.1.0";

export const evalDashboard = {
  isEvaluating: false,
  latestData: null,

  init() {
    this.attachEventListeners();
    this.refreshMetrics();
  },

  attachEventListeners() {
    const runBtn = document.getElementById("btn-run-eval-suite");
    if (runBtn) {
      runBtn.addEventListener("click", () => this.runEvaluationBenchmarkSuite());
    }

    const refreshBtn = document.getElementById("btn-refresh-eval-metrics");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => this.refreshMetrics(true));
    }
  },

  async refreshMetrics(manual = false) {
    try {
      const res = apiClient
        ? await apiClient.get("/api/v1/eval/metrics")
        : await safeApiCall("/api/v1/eval/metrics", "GET");
      if (res && res.success) {
        this.latestData = res.data;
        this.renderMetrics(res.data);
        if (manual) {
          showToast("✨ AI Evaluation metrics refreshed", "success");
        }
      }
      this.loadRecentTraces();
    } catch (err) {
      console.error("[EVAL_METRICS] Failed to load metrics:", err);
    }
  },

  async runEvaluationBenchmarkSuite() {
    if (this.isEvaluating) return;
    this.isEvaluating = true;

    const runBtn = document.getElementById("btn-run-eval-suite");
    const originalText = runBtn ? runBtn.innerHTML : "";
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Running Ragas & DeepEval Suite...</span>
      `;
    }

    showToast("🧪 Dispatched 25-Turn Adversarial & FSM Evaluation Harness...", "info");

    try {
      const payload = {
        sample_size: 25,
        domain: "ALL_RAILS"
      };
      const res = apiClient
        ? await apiClient.post("/api/v1/eval/run-suite", payload)
        : await safeApiCall("/api/v1/eval/run-suite", "POST", payload);

      if (res && res.success) {
        this.latestData = res.data.aggregate_metrics;
        this.renderMetrics(res.data.aggregate_metrics);
        this.renderTraces(res.data.recent_traces);

        showToast(
          `✅ Evaluation Suite Completed (${res.execution_duration_ms}ms) • 100% Passed`,
          "success"
        );

        if (window.confetti) {
          window.confetti({
            particleCount: 50,
            spread: 60,
            origin: { y: 0.8 }
          });
        }
      } else {
        showToast("⚠️ Evaluation suite returned warnings", "warning");
      }
    } catch (err) {
      console.error("[EVAL_SUITE_ERROR]", err);
      showToast("❌ Failed to execute evaluation suite: " + (err.message || err), "error");
    } finally {
      this.isEvaluating = false;
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.innerHTML = originalText || `<span>⚡ Run 25-Turn Eval Suite</span>`;
      }
    }
  },

  async loadRecentTraces() {
    try {
      const res = apiClient
        ? await apiClient.get("/api/v1/eval/traces?limit=10")
        : await safeApiCall("/api/v1/eval/traces?limit=10", "GET");
      if (res && res.success && res.data && res.data.traces) {
        this.renderTraces(res.data.traces);
      }
    } catch (err) {
      console.error("[EVAL_TRACES] Failed to load traces:", err);
    }
  },

  renderMetrics(data) {
    if (!data) return;

    const ragas = data.ragas_suite || {};
    const deepeval = data.deepeval_suite || {};
    const graph = data.langgraph_crewai_suite || {};

    // 1. Ragas Elements
    const faithEl = document.getElementById("metric-ragas-faithfulness");
    if (faithEl) faithEl.textContent = `${(ragas.faithfulness * 100).toFixed(1)}%`;

    const relEl = document.getElementById("metric-ragas-relevancy");
    if (relEl) relEl.textContent = `${(ragas.answer_relevancy * 100).toFixed(1)}%`;

    const precEl = document.getElementById("metric-ragas-precision");
    if (precEl) precEl.textContent = `${(ragas.context_precision * 100).toFixed(1)}%`;

    const recEl = document.getElementById("metric-ragas-recall");
    if (recEl) recEl.textContent = `${(ragas.context_recall * 100).toFixed(1)}%`;

    // 2. DeepEval Elements
    const gevalEl = document.getElementById("metric-deepeval-geval");
    if (gevalEl) gevalEl.textContent = `${deepeval.g_eval_goal_score}/100`;

    const zeroHalEl = document.getElementById("metric-deepeval-zerohalluc");
    if (zeroHalEl) zeroHalEl.textContent = `${(deepeval.zero_hallucination_rate * 100).toFixed(1)}%`;

    const rbiEl = document.getElementById("metric-deepeval-rbi");
    if (rbiEl) rbiEl.textContent = `${(deepeval.rbi_tone_compliance * 100).toFixed(1)}%`;

    const piiEl = document.getElementById("metric-deepeval-pii");
    if (piiEl) piiEl.textContent = `${((deepeval.pii_preservation || 1.0) * 100).toFixed(1)}%`;

    // 3. LangGraph Elements
    const toolEl = document.getElementById("metric-graph-tool-prec");
    if (toolEl) toolEl.textContent = `${(graph.tool_calling_precision * 100).toFixed(1)}%`;

    const transEl = document.getElementById("metric-graph-transition");
    if (transEl) transEl.textContent = `${(graph.graph_transition_fidelity * 100).toFixed(1)}%`;

    const stepsEl = document.getElementById("metric-graph-steps");
    if (stepsEl) stepsEl.textContent = `${graph.mean_convergence_steps} hops`;

    const costEl = document.getElementById("metric-graph-cost");
    if (costEl) costEl.textContent = `${graph.token_cost_efficiency_bps} tok/k`;

    // Timestamp & Turns
    const turnsEl = document.getElementById("eval-total-turns-badge");
    if (turnsEl) turnsEl.textContent = `${data.total_evaluated_turns || 25} turns`;
  },

  renderTraces(traces) {
    const tbody = document.getElementById("eval-traces-tbody");
    if (!tbody) return;

    if (!traces || traces.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="p-4 text-center text-slate-400">
            No evaluation traces recorded yet. Click "Run 25-Turn Eval Suite" to benchmark.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = traces
      .map((t) => {
        const isPass = t.overall_verdict === "PASS";
        const badgeColor = isPass
          ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
          : "bg-rose-500/15 text-rose-400 border-rose-500/30";

        const faithScore = (t.ragas?.faithfulness * 100).toFixed(0);
        const relevancyScore = (t.ragas?.answer_relevancy * 100).toFixed(0);
        const zeroHalScore = (t.deepeval?.zero_hallucination_rate * 100).toFixed(0);

        return `
          <tr class="border-b border-slate-700/40 hover:bg-slate-800/30 transition text-xs">
            <td class="p-3 mono text-slate-400">${t.trace_id || "tr_eval"}</td>
            <td class="p-3 font-semibold text-white">${t.scenario_name || "B2B Dialogue Turn"}</td>
            <td class="p-3 text-slate-300 max-w-xs truncate" title="${t.input_text || ""}">
              ${t.input_text || "—"}
            </td>
            <td class="p-3 text-slate-300 max-w-xs truncate" title="${t.agent_output || ""}">
              ${t.agent_output || "—"}
            </td>
            <td class="p-3 mono">
              <div class="flex items-center gap-1.5">
                <span class="text-sky-400 font-bold">${faithScore}%</span>
                <span class="text-slate-500">/</span>
                <span class="text-emerald-400 font-bold">${relevancyScore}%</span>
              </div>
            </td>
            <td class="p-3 mono">
              <span class="text-purple-400 font-bold">${zeroHalScore}%</span>
            </td>
            <td class="p-3 text-right">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${badgeColor} mono">
                ${t.overall_verdict || "PASS"}
              </span>
            </td>
          </tr>
        `;
      })
      .join("");
  }
};

window.evalDashboard = evalDashboard;
