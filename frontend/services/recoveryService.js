/**
 * RazorRevive-OS — Fast-Loop Recovery & Batch Ingestion Service
 */

import { safeApiCall, showToast } from "./apiClient.js";
import { formatINR } from "../utils/formatters.js";
import { refreshAuditLedger } from "./auditService.js";

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
