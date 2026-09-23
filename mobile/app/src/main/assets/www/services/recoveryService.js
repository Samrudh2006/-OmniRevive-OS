/**
 * OmniRevive-OS — Fast-Loop Recovery & Batch Ingestion Service
 */

import { safeApiCall, showToast } from "./apiClient.js?v=2.1.0";
import { formatINR } from "../utils/formatters.js?v=2.1.0";
import { refreshAuditLedger } from "./auditService.js?v=2.1.0";
import { escapeHtml, sanitizeCsvCell } from "../utils/escapeHtml.js?v=2.1.0";

export async function triggerFastLoopPipeline() {
  const errCode = document.querySelector("#fast-scenario-select")?.value || "GATEWAY_ERROR";
  const amount = parseFloat(document.querySelector("#fast-amount")?.value || 2499);
  const phone = document.querySelector("#fast-phone")?.value || "+91 98765 43210";
  const payId = document.querySelector("#fast-pay-id")?.value || "pay_9A12BC34DE";

  document.querySelectorAll("#fast-loop-btn").forEach(btn => {
    btn.disabled = true;
    btn.innerText = "⚡ Executing Recovery Pipeline...";
  });

  try {
    const data = await safeApiCall("/api/v1/simulate/failure", "POST", {
      payment_id: payId,
      amount: amount,
      error_code: errCode,
      error_description: errCode.replace(/_/g, " ").toLowerCase(),
      customer_phone: phone
    });

    document.querySelectorAll("#res-rec-action").forEach(el => el.innerText = data.recommended_action_label || "Poisson-Window Mandate Retry");
    document.querySelectorAll("#res-retry-at").forEach(el => el.innerText = data.recommended_retry_at || "11:00:24 AM (in 45m)");
    document.querySelectorAll("#res-success-prob").forEach(el => el.innerText = data.success_probability || "82.6%");
    document.querySelectorAll("#res-max-attempts").forEach(el => el.innerText = data.max_attempts || "1 / 3");

    document.querySelectorAll("#dt-failure-class").forEach(el => el.innerText = data.failure_class);
    document.querySelectorAll("#dt-strategy").forEach(el => el.innerText = data.strategy);
    document.querySelectorAll("#dt-confidence").forEach(el => el.innerText = typeof data.confidence === "number" ? data.confidence.toFixed(2) : data.confidence);
    document.querySelectorAll("#dt-policy-result").forEach(el => el.innerText = data.policy_result);
    document.querySelectorAll("#dt-reason").forEach(el => el.innerText = data.reason);
    document.querySelectorAll("#trace-id-display").forEach(el => el.innerText = `(Trace ID: ${data.trace_id})`);

    if (data.decision_trace && data.decision_trace.length > 0) {
      const timelineHtml = data.decision_trace.map(t => `
        <div class="relative">
          <span class="absolute -left-[21px] top-0.5 w-3 h-3 rounded-full bg-[#10b981] flex items-center justify-center text-[8px] text-white">✓</span>
          <div class="text-slate-400 mono text-[10px]">${t.timestamp || '10:15:24'}</div>
          <div class="text-white font-semibold text-xs">${t.title || t.step}</div>
          <div class="text-[11px] text-slate-400">${t.details || ''}</div>
        </div>
      `).join('');
      document.querySelectorAll("#trace-timeline-list").forEach(el => el.innerHTML = timelineHtml);
    }

    refreshAuditLedger();
    showToast(`⚡ Recovery Pipeline Executed for ${payId}`, "success");
  } catch (err) {
    showToast("Pipeline Notice: " + err.message, "warning");
  } finally {
    document.querySelectorAll("#fast-loop-btn").forEach(btn => {
      btn.disabled = false;
      btn.innerText = "🚀 Ingest Webhook & Trigger Recovery Pipeline";
    });
  }
}

export async function inspectCardTokenAction() {
  const tokId = document.getElementById("token-insp-id")?.value || "tok_visa_vts_882910";
  const net = document.getElementById("token-insp-net")?.value || "VISA";
  const state = document.getElementById("token-insp-state")?.value || "CRYPTOGRAM_EXPIRED";

  try {
    const data = await safeApiCall("/api/v1/recovery/card-token/inspect", "POST", {
      token_id: tokId,
      network: net,
      state: state
    });

    const actionEl = document.getElementById("token-res-action");
    const retryEl = document.getElementById("token-res-retry");
    const faEl = document.getElementById("token-res-2fa");
    const outreachEl = document.getElementById("token-res-outreach");
    const descEl = document.getElementById("token-res-desc");
    const nextEl = document.getElementById("token-res-next");

    const action = data.recommended_remediation || data.remediation_action || (state === "ACTIVE" ? "HEALTHY_CRYPTOGRAM_READY" : "AUTOMATIC_TOKEN_REPROVISION");
    const canRetry = data.can_auto_retry !== undefined ? data.can_auto_retry : (data.retry_allowed_on_token !== undefined ? data.retry_allowed_on_token : (state === "ACTIVE" || state === "CRYPTOGRAM_EXPIRED"));
    const stepUp = data.step_up_2fa_required !== undefined ? data.step_up_2fa_required : (action === "STEP_UP_2FA_CONSENT" || state === "SUSPENDED");
    const outreach = data.customer_outreach_action || (state === "ACTIVE" ? "NONE (Token Healthy)" : (canRetry ? "DISPATCH_TOKEN_UPDATE_LINK" : "TRIGGER_WHATSAPP_RECOVERY"));
    const desc = data.remediation_description || data.revocation_reason || (state === "ACTIVE" ? "Card token and cryptogram are verified healthy with active 24h network validity." : "Token cryptogram expired; fresh dynamic cryptogram requested via card network API.");

    let nextActionText = "Acquire New Dynamic CVV";
    if (state === "ACTIVE") nextActionText = "Execute Direct Mandate Debit";
    else if (state === "SUSPENDED") nextActionText = "Prompt Customer for 2FA Step-Up";
    else if (state === "REVOKED") nextActionText = "Initiate Fallback UPI Mandate";
    else if (state === "DELETED") nextActionText = "Dispatch 1-Click Card Re-enrollment Link";

    if (actionEl) actionEl.innerText = action;
    if (retryEl) retryEl.innerText = canRetry ? (state === "ACTIVE" ? "YES (Immediate)" : "YES (Post-Reprovision)") : "NO";
    if (faEl) faEl.innerText = stepUp ? "YES" : "NO";
    if (outreachEl) outreachEl.innerText = outreach;
    if (descEl) descEl.innerText = desc;
    if (nextEl) nextEl.innerText = nextActionText;

    showToast(`💳 Token [${tokId}] Inspected: ${action}`, "success");
  } catch (err) {
    console.error("Token inspection error", err);
    showToast("Token inspection error: " + err.message, "error");
  }
}

export function generateAndLoadSampleCsv() {
  const sampleRows = [
    { payment_id: "pay_bulk_001", amount: 2499.0, customer_phone: "+919876543210", error_code: "GATEWAY_ERROR", bank: "HDFC", customer_name: "Rahul Sharma" },
    { payment_id: "pay_bulk_002", amount: 1499.0, customer_phone: "+919876543211", error_code: "INSUFFICIENT_FUNDS", bank: "SBI", customer_name: "Priya Patel" },
    { payment_id: "pay_bulk_003", amount: 85000.0, customer_phone: "+919876543212", error_code: "CARD_EXPIRED", bank: "ICICI", customer_name: "TechCorp India" },
    { payment_id: "pay_bulk_004", amount: 3200.0, customer_phone: "+919876543213", error_code: "UPI_U30_DEGRADATION", bank: "SBI", customer_name: "Amit Kumar" },
    { payment_id: "pay_bulk_005", amount: 599.0, customer_phone: "+919876543214", error_code: "TOKEN_REVOKED", bank: "AXIS", customer_name: "Sneha Reddy" },
    { payment_id: "pay_bulk_006", amount: 12500.0, customer_phone: "+919876543215", error_code: "GATEWAY_TIMEOUT", bank: "HDFC", customer_name: "Vikram Singh" },
    { payment_id: "pay_bulk_007", amount: 45000.0, customer_phone: "+919876543216", error_code: "INSUFFICIENT_FUNDS", bank: "KOTAK", customer_name: "Nova Logistics" },
    { payment_id: "pay_bulk_008", amount: 1899.0, customer_phone: "+919876543217", error_code: "AUTHENTICATION_FAILED", bank: "PNB", customer_name: "Rohan Verma" },
    { payment_id: "pay_bulk_009", amount: 999.0, customer_phone: "+919876543218", error_code: "GATEWAY_ERROR", bank: "YESB", customer_name: "Deepa Gupta" },
    { payment_id: "pay_bulk_010", amount: 24999.0, customer_phone: "+919876543219", error_code: "CARD_TOKEN_CRYPTOGRAM_INVALID", bank: "HDFC", customer_name: "Aarav Nair" }
  ];

  processBatchJsonItems(sampleRows);
  showToast("⚡ Loaded sample batch CSV (10 transactions)!", "success");
}

export async function handleBulkCsvFileSelected(e) {
  const file = e.target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(evt) {
    const text = evt.target.result;
    const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length < 2) {
      showToast("CSV must have at least 1 data row.", "error");
      return;
    }

    const items = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(",").map(c => c.trim());
      if (cols.length >= 4) {
        items.push({
          payment_id: cols[0] || `pay_batch_${i}`,
          amount: parseFloat(cols[1]) || 1999.0,
          customer_phone: cols[2] || "+919876543210",
          error_code: cols[3] || "GATEWAY_ERROR",
          bank: cols[4] || "HDFC",
          customer_name: cols[5] || `Customer ${i}`
        });
      }
    }

    await processBatchJsonItems(items);
    showToast(`⚡ Processed ${items.length} CSV transactions in batch!`, "success");
  };
  reader.readAsText(file);
}

export async function processBatchJsonItems(items) {
  try {
    const res = await safeApiCall("/api/v1/recovery/batch-json", "POST", { items: items });
    window.latestBatchData = res;
    renderBatchResults(res);
  } catch (err) {
    console.error("Batch processing error", err);
  }
}

export function renderBatchResults(data) {
  const totalEl = document.getElementById("bulk-kpi-total");
  const atRiskEl = document.getElementById("bulk-kpi-at-risk");
  const recEl = document.getElementById("bulk-kpi-recovered");
  const delEl = document.getElementById("bulk-kpi-delayed");
  const linksEl = document.getElementById("bulk-kpi-links");
  const latEl = document.getElementById("bulk-kpi-latency");
  const countEl = document.getElementById("bulk-table-count");

  if (totalEl) totalEl.innerText = data.total_ingested || data.items?.length || 10;
  if (atRiskEl) atRiskEl.innerText = `₹${(data.total_at_risk_gmv || 0).toLocaleString('en-IN')}`;
  if (recEl) recEl.innerText = `₹${(data.expected_recovery_gmv || 0).toLocaleString('en-IN')}`;
  if (delEl) delEl.innerText = data.delayed_retries_scheduled || 0;
  if (linksEl) linksEl.innerText = data.direct_recovery_links_dispatched || 0;
  if (latEl) latEl.innerText = `${(data.processing_time_ms || 2.4).toFixed(1)}ms`;
  if (countEl) countEl.innerText = `Showing ${data.items?.length || 0} diagnosed transactions`;

  const tbody = document.getElementById("bulk-table-body");
  if (tbody && data.items) {
    tbody.innerHTML = data.items.map(item => `
      <tr class="hover:bg-[#081224] transition-colors">
        <td class="p-2.5 text-white font-medium">${escapeHtml(item.payment_id)}</td>
        <td class="p-2.5 text-emerald-400 font-bold">₹${Number(item.amount || 0).toLocaleString('en-IN')}</td>
        <td class="p-2.5 text-slate-300">${escapeHtml(item.bank || 'HDFC')}</td>
        <td class="p-2.5 text-sky-400">${escapeHtml(item.failure_class)}</td>
        <td class="p-2.5 text-slate-200">${escapeHtml(item.strategy)}</td>
        <td class="p-2.5 text-slate-300">${escapeHtml(item.action)}</td>
        <td class="p-2.5 text-purple-300">${escapeHtml(item.scheduled_retry_at || 'Immediate (+0m)')}</td>
        <td class="p-2.5 text-slate-300">${Number(item.confidence || 0).toFixed(2)}</td>
        <td class="p-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#063b22] text-[#10b981]">${escapeHtml(item.policy_result)}</span></td>
      </tr>
    `).join("");
  }
}

export function exportBatchResolutionCsv() {
  if (!window.latestBatchData || !window.latestBatchData.items) {
    showToast("No batch results to export. Load sample or upload CSV first.", "error");
    return;
  }

  const headers = ["payment_id", "amount", "bank", "failure_class", "strategy", "action", "scheduled_retry_at", "confidence", "policy_result"];
  const csvRows = [headers.join(",")];

  window.latestBatchData.items.forEach(it => {
    csvRows.push([
      sanitizeCsvCell(it.payment_id),
      it.amount,
      sanitizeCsvCell(it.bank || "HDFC"),
      sanitizeCsvCell(it.failure_class),
      sanitizeCsvCell(it.strategy),
      sanitizeCsvCell(it.action),
      sanitizeCsvCell(it.scheduled_retry_at || "Immediate"),
      it.confidence,
      sanitizeCsvCell(it.policy_result)
    ].join(","));
  });

  const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `omnirevive_batch_resolution_${Date.now()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("Exported batch resolution results to CSV", "success");
}

