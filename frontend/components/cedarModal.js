/**
 * RazorRevive-OS AWS Cloud & Cedar Zero-Trust Security Modal Component
 */

import { safeApiCall } from "../services/apiClient.js";

export async function openAwsCedarModal() {
  const modal = document.getElementById("aws-cedar-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    document.body.style.overflow = "hidden";
  }

  // Fetch live Bedrock status
  try {
    const resp = await safeApiCall("/aws/bedrock/status");
    if (resp && resp.data) {
      const mEl = document.getElementById("aws-modal-model");
      if (mEl) mEl.innerText = resp.data.foundation_model.split("-").slice(0, 3).join(" ") || "Claude 3.5 Sonnet";
    }
  } catch (e) {
    console.warn("Bedrock status fetch failed", e);
  }

  // Fetch live Cedar policies
  try {
    const resp = await safeApiCall("/aws/cedar/policies");
    if (resp && resp.data) {
      const hEl = document.getElementById("aws-modal-hash");
      if (hEl) hEl.innerText = `SHA: ${resp.data.policy_sha256.substring(0, 16)}...`;
      const pEl = document.getElementById("aws-modal-policy-text");
      if (pEl && resp.data.raw_policies) pEl.innerText = resp.data.raw_policies;
    }
  } catch (e) {
    console.warn("Cedar policies fetch failed", e);
  }
}

export function closeAwsCedarModal() {
  const modal = document.getElementById("aws-cedar-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "auto";
  }
}

export function applyCedarTestCase(val) {
  const principalInput = document.getElementById("cedar-input-principal");
  const actionInput = document.getElementById("cedar-input-action");
  const resourceInput = document.getElementById("cedar-input-resource");
  const mfaSelect = document.getElementById("cedar-input-mfa");

  if (val === "sre_allow") {
    if (principalInput) principalInput.value = "Role::SRE_Admin";
    if (actionInput) actionInput.value = "Action::TripCircuitBreaker";
    if (resourceInput) resourceInput.value = "BankingSwitch::SBI";
    if (mfaSelect) mfaSelect.value = "true";
  } else if (val === "dev_deny") {
    if (principalInput) principalInput.value = "Role::Junior_Dev";
    if (actionInput) actionInput.value = "Action::TripCircuitBreaker";
    if (resourceInput) resourceInput.value = "BankingSwitch::SBI";
    if (mfaSelect) mfaSelect.value = "false";
  } else if (val === "gstin_allow") {
    if (principalInput) principalInput.value = "Agent::BedrockVoiceAgent";
    if (actionInput) actionInput.value = "Action::MutateInvoiceGSTIN";
    if (resourceInput) resourceInput.value = "B2BInvoice::inv_enterprise_998";
    if (mfaSelect) mfaSelect.value = "true";
  } else if (val === "audit_forbid") {
    if (principalInput) principalInput.value = "Role::SuperAdmin";
    if (actionInput) actionInput.value = "Action::DeleteAuditRecord";
    if (resourceInput) resourceInput.value = "AuditLog::recovery_audit";
    if (mfaSelect) mfaSelect.value = "true";
  }
  runCedarTestEvaluation();
}

export async function runCedarTestEvaluation() {
  const principal = document.getElementById("cedar-input-principal")?.value || "Role::SRE_Admin";
  const action = document.getElementById("cedar-input-action")?.value || "Action::TripCircuitBreaker";
  const resource = document.getElementById("cedar-input-resource")?.value || "BankingSwitch::SBI";
  const mfa = document.getElementById("cedar-input-mfa")?.value === "true";

  const badge = document.getElementById("cedar-result-badge");
  const details = document.getElementById("cedar-result-details");
  if (badge) {
    badge.innerText = "EVALUATING...";
    badge.className = "px-2 py-0.5 rounded text-[11px] font-bold bg-amber-950 text-amber-300 border border-amber-600 animate-pulse";
  }

  try {
    const resp = await safeApiCall("/aws/cedar/evaluate", "POST", {
      principal,
      action,
      resource,
      context: { mfa_verified: mfa, system_risk_score: 35, proposed_gstin: "29AABCU9603R1Z2", invoice_amount: 125000, regulatory_compliance: "GST_RULE_46" }
    });

    if (resp && resp.data) {
      const d = resp.data;
      if (badge) {
        if (d.decision === "ALLOW") {
          badge.innerText = "ALLOW";
          badge.className = "px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-600";
        } else {
          badge.innerText = "DENY";
          badge.className = "px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-300 border border-rose-600";
        }
      }
      if (details) {
        details.innerText = `Policy: ${d.policy_id} • ${d.diagnostics?.reason || "Verified Cedar evaluation"}`;
      }
    }
  } catch (err) {
    if (badge) {
      badge.innerText = "ERROR";
      badge.className = "px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-300 border border-rose-600";
    }
    if (details) details.innerText = "Evaluation call failed: " + err.message;
  }
}
