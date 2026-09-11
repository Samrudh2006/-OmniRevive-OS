/**
 * RazorRevive-OS CFO Executive Approval Component
 * Provides UI rendering, approval/rejection actions, and pending badge updates.
 */

import { fetchCFOQueue, approveCFOItem, rejectCFOItem } from "../services/cfoService.js";
const fetchCfoQueue = fetchCFOQueue;
const approveEscalation = approveCFOItem;
const rejectEscalation = rejectCFOItem;
import { formatINR } from "../utils/formatters.js";
import { showToast } from "../utils/toast.js";

export async function refreshCfoQueueUI() {
  const container = document.getElementById("cfo-queue-tbody");
  const badgeEl = document.getElementById("cfo-pending-badge");
  const countEl = document.getElementById("cfo-pending-count");

  try {
    const queue = await fetchCfoQueue("PENDING_APPROVAL");
    
    if (badgeEl) {
      if (queue.length > 0) {
        badgeEl.textContent = queue.length;
        badgeEl.classList.remove("hidden");
      } else {
        badgeEl.classList.add("hidden");
      }
    }
    if (countEl) {
      countEl.textContent = queue.length;
    }

    if (!container) return;

    if (queue.length === 0) {
      container.innerHTML = `
        <tr>
          <td colspan="7" class="py-8 text-center text-slate-500 font-mono text-xs">
            ✓ No pending CFO escalations in queue. Zero-trust ledger intact.
          </td>
        </tr>
      `;
      return;
    }

    container.innerHTML = queue.map((item) => `
      <tr class="border-b border-slate-800/60 hover:bg-slate-800/30 transition text-xs font-mono">
        <td class="py-3 px-3 text-sky-400 font-semibold">${item.escalation_id}</td>
        <td class="py-3 px-3 text-slate-300">${item.invoice_id}</td>
        <td class="py-3 px-3 text-amber-300 font-semibold">${formatINR(item.amount)}</td>
        <td class="py-3 px-3 text-rose-400">-${formatINR(item.margin_loss || 0)}</td>
        <td class="py-3 px-3 text-slate-300 max-w-[200px] truncate" title="${item.reason}">${item.reason}</td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
            item.risk_level === 'CRITICAL' 
              ? 'bg-rose-950 text-rose-300 border border-rose-600/60' 
              : 'bg-amber-950 text-amber-300 border border-amber-600/60'
          }">
            ${item.risk_level || 'HIGH'}
          </span>
        </td>
        <td class="py-3 px-3 flex items-center gap-2">
          <button onclick="handleCfoApprove('${item.escalation_id}')" 
                  class="px-2.5 py-1 rounded bg-emerald-700 hover:bg-emerald-600 text-white text-[11px] font-sans font-semibold transition flex items-center gap-1 shadow-sm">
            <span>✓</span> Approve
          </button>
          <button onclick="handleCfoReject('${item.escalation_id}')" 
                  class="px-2.5 py-1 rounded bg-rose-900/80 hover:bg-rose-800 text-rose-200 text-[11px] font-sans font-semibold transition flex items-center gap-1 border border-rose-700/60">
            <span>✕</span> Reject
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to render CFO queue", err);
    if (container) {
      container.innerHTML = `
        <tr>
          <td colspan="7" class="py-4 text-center text-rose-400 font-mono text-xs">
            Failed to load CFO queue: ${err.message}
          </td>
        </tr>
      `;
    }
  }
}

export async function handleCfoApprove(escalationId) {
  try {
    const res = await approveEscalation(escalationId, "Approved via CFO Executive Cockpit");
    showToast(`✓ Escalation ${escalationId} APPROVED by CFO! Audit block chained.`, "success");
    await refreshCfoQueueUI();
  } catch (err) {
    showToast(`Approval failed: ${err.message}`, "error");
  }
}

export async function handleCfoReject(escalationId) {
  try {
    const res = await rejectEscalation(escalationId, "Rejected via CFO Executive Cockpit");
    showToast(`Escalation ${escalationId} REJECTED. Dunning stopped.`, "warning");
    await refreshCfoQueueUI();
  } catch (err) {
    showToast(`Rejection failed: ${err.message}`, "error");
  }
}
