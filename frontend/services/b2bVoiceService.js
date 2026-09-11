/**
 * RazorRevive-OS — Deep-Loop B2B Voice & PTP Service
 */

import { safeApiCall, showToast } from "./apiClient.js?v=2.1.0";
import { formatINR, formatDateIST } from "../utils/formatters.js?v=2.1.0";
import { speakText, stopSpeaking } from "../utils/audioPlayer.js?v=2.1.0";
import { refreshAuditLedger } from "./auditService.js?v=2.1.0";

export async function triggerVoiceTurnAction() {
  let customSpeech = "";
  document.querySelectorAll("#voice-custom-speech").forEach(el => {
    if (el.value && el.value.trim()) customSpeech = el.value.trim();
  });
  const selectSpeech = document.querySelector("#voice-speech-select")?.value;
  const speech = customSpeech || selectSpeech || "Invoice mein hamara GST galat hai, correct GSTIN 29AABCU9603R1Z2 daal kar bhejo";
  
  let invId = "inv_enterprise_998";
  document.querySelectorAll("#voice-inv-id").forEach(el => {
    if (el.value && el.value.trim()) invId = el.value.trim();
  });

  let amt = 85000;
  document.querySelectorAll("#voice-inv-amount").forEach(el => {
    if (el.value && !isNaN(parseFloat(el.value))) amt = parseFloat(el.value);
  });

  stopSpeaking();

  document.querySelectorAll("#voice-turn-btn").forEach(btn => {
    btn.disabled = true;
    btn.innerHTML = "<span>⚙️</span> <span>Processing Autonomous Voice Dialogue...</span>";
  });

  const chosenVoice = document.querySelector("#neural-voice-select")?.value || "auto";

  try {
    const data = await safeApiCall("/api/v1/b2b/voice/turn", "POST", {
      call_session_id: "call_" + Math.floor(Math.random() * 8999 + 1000),
      invoice_id: invId,
      customer_speech_text: speech,
      invoice_amount: amt,
      preferred_voice: chosenVoice
    });

    document.querySelectorAll("#voice-agent-speech-transcript").forEach(el => {
      el.innerText = `"${data.agent_speech_response}"`;
    });

    document.querySelectorAll(".mutation-result-banner").forEach(banner => {
      banner.classList.remove("hidden");
      const dispatchBtn = data.dispatch_id ? `
        <button onclick="window.openDispatchedEmailModal('${data.dispatch_id}')" class="px-2.5 py-1 bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow transition-all cursor-pointer">
          <span>📧</span> <span>View Dispatched Email</span>
        </button>
      ` : '';

      if (data.mutation_proposal) {
        const m = data.mutation_proposal;
        banner.innerHTML = `
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-emerald-400 font-bold">✓</span>
              <span class="text-white font-semibold">Structured Mutation Proposed:</span>
              <span class="text-amber-300 mono font-bold">${m.field_to_mutate || 'Tax Line'}</span>
              <span class="text-slate-400 text-[11px]">from</span>
              <span class="text-rose-400 line-through mono text-[11px]">${m.old_value || 'UNREGISTERED'}</span>
              <span class="text-slate-400 text-[11px]">➔</span>
              <span class="text-emerald-400 font-bold mono">${m.new_value || '29AABCU9603R1Z2'}</span>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              ${dispatchBtn}
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 text-emerald-300 border border-emerald-800 mono self-start sm:self-auto">POLICY APPROVED</span>
            </div>
          </div>
        `;
      } else if (data.should_escalate_to_human) {
        banner.innerHTML = `
          <div class="flex items-center justify-between text-xs font-semibold">
            <div class="flex items-center gap-2 text-rose-400 font-bold">
              <span>🚨</span>
              <span>LEGAL DISPUTE FLAGGED: Escalated to Senior Accounts Director & Human CFO</span>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/60 text-rose-300 border border-rose-800 mono">CFO_ESCALATED</span>
          </div>
        `;
      } else {
        banner.innerHTML = `
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-semibold">
            <div class="flex items-center gap-2 text-sky-400">
              <span>📅</span>
              <span class="text-white font-bold">Commitment Registered:</span>
              <span class="text-sky-300">PTP Lock active until Friday 11:00 AM IST (Reminders Suppressed)</span>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              ${dispatchBtn}
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-950/60 text-sky-300 border border-sky-800 mono">PTP_LOCKED</span>
            </div>
          </div>
        `;
      }
    });

    if (data.mutated_invoice_summary && data.mutated_invoice_summary.gstin) {
      document.querySelectorAll("#voice-inv-gstin, .invoice-gstin-val").forEach(el => {
        el.innerText = data.mutated_invoice_summary.gstin;
      });
    }

    // Update the top integrated voice action station
    const statusText = document.getElementById("voice-status-text");
    if (statusText) {
      if (data.dispatch_id) {
        statusText.innerHTML = `Email Dispatched to <strong class="text-white">${data.dispatched_email_recipient || 'finance@acmepvt.com'}</strong> • Status: <span class="text-emerald-400 font-bold">DELIVERED</span>`;
      } else if (data.mutation_proposal) {
        statusText.innerHTML = `Mutation Proposed for <strong class="text-white">${data.mutation_proposal.field_to_mutate}</strong> • Policy Verified`;
      } else {
        statusText.innerText = `Turn Resolved: ${data.intent_detected}`;
      }
    }
    if (data.dispatch_id) {
      const emailBtn = document.getElementById("voice-bar-email-btn");
      if (emailBtn) {
        emailBtn.onclick = () => window.openDispatchedEmailModal(data.dispatch_id);
        emailBtn.classList.add("ring-2", "ring-sky-400", "animate-pulse");
        setTimeout(() => emailBtn.classList.remove("animate-pulse"), 4000);
      }
    }

    speakText(data.agent_speech_response, null, data.recommended_voice);
    showToast(`🎙️ Voice Turn Resolved: ${data.intent_detected}`, "success");
    refreshAuditLedger();
    loadPTPRecords();
  } catch (err) {
    showToast("Voice Turn Error: " + err.message, "error");
  } finally {
    document.querySelectorAll("#voice-turn-btn").forEach(btn => {
      btn.disabled = false;
      btn.innerHTML = "<span>🎙️</span> <span>Process Autonomous Voice Dialogue Turn</span>";
    });
  }
}

export async function loadPTPRecords() {
  try {
    const data = await safeApiCall("/api/v1/ptp/active");
    const records = data.ptp_records || [];
    const container = document.getElementById("ptp-table-rows");
    if (!container) return;

    if (records.length === 0) {
      container.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400 text-xs">No active Promise-to-Pay locks.</td></tr>`;
      return;
    }

    container.innerHTML = records.map(r => `
      <tr class="border-b border-slate-200 dark:border-[#1e293b] hover:bg-slate-50 dark:hover:bg-[#0c182c]/40 transition text-xs">
        <td class="p-3 font-mono text-sky-400 font-semibold">${r.invoice_id}</td>
        <td class="p-3 text-slate-300">${r.customer_contact}</td>
        <td class="p-3 font-mono font-bold text-white">${formatINR(r.amount)}</td>
        <td class="p-3 text-emerald-400 font-medium">${r.promised_window_label}</td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/60 text-emerald-300 border border-emerald-800 mono">${r.status}</span>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Could not load PTP records", err);
  }
}
