/**
 * RazorRevive-OS — Executive CFO Approval & Zero-Trust Gating Service
 */

import { safeApiCall, showToast } from "./apiClient.js";
import { formatINR, formatDateIST } from "../utils/formatters.js";

export async function fetchCFOQueue(status = null) {
  const url = status ? `/api/v1/cfo/queue?status=${status}` : "/api/v1/cfo/queue";
  return await safeApiCall(url);
}

export async function approveCFOItem(approvalId, notes = "Approved after executive review") {
  try {
    const res = await safeApiCall("/api/v1/cfo/approve", "POST", {
      approval_id: approvalId,
      notes: notes
    });
    showToast(`✓ Executive Approval Granted for ${approvalId}. Status: EXECUTED`, "success");
    return res;
  } catch (err) {
    showToast(`Failed to approve ${approvalId}: ${err.message}`, "error");
    throw err;
  }
}

export async function rejectCFOItem(approvalId, notes = "Rejected by executive review") {
  try {
    const res = await safeApiCall("/api/v1/cfo/reject", "POST", {
      approval_id: approvalId,
      notes: notes
    });
    showToast(`✕ Approval ${approvalId} Rejected. Action Suppressed.`, "info");
    return res;
  } catch (err) {
    showToast(`Failed to reject ${approvalId}: ${err.message}`, "error");
    throw err;
  }
}

export async function refreshCFOQueueUI() {
  const tableBody = document.getElementById("cfo-queue-table-body");
  const countBadge = document.getElementById("cfo-pending-badge");
  if (!tableBody) return;

  try {
    const data = await fetchCFOQueue();
    const items = data.queue || [];
    const pendingCount = items.filter(i => i.status === "PENDING_APPROVAL").length;

    if (countBadge) {
      countBadge.innerText = `${pendingCount} Pending`;
      countBadge.className = pendingCount > 0 
        ? "px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30"
        : "px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    }

    if (items.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-400">No CFO approval requests pending.</td></tr>`;
      return;
    }

    tableBody.innerHTML = items.map(item => {
      const isPending = item.status === "PENDING_APPROVAL";
      const statusBadge = item.status === "EXECUTED" 
        ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
        : (item.status === "REJECTED" ? "bg-rose-500/20 text-rose-400 border-rose-500/30" : "bg-amber-500/20 text-amber-400 border-amber-500/30");

      return `
        <tr class="border-b border-slate-200 dark:border-[#1e293b] hover:bg-slate-50 dark:hover:bg-[#0c182c]/40 transition text-xs">
          <td class="p-3 font-mono text-sky-400">${item.approval_id}</td>
          <td class="p-3 font-medium text-slate-200">${item.entity_id}</td>
          <td class="p-3 font-mono font-bold text-white">${formatINR(item.amount)}</td>
          <td class="p-3 text-slate-400 max-w-xs truncate" title="${item.reason}">${item.reason}</td>
          <td class="p-3">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${statusBadge}">${item.status}</span>
          </td>
          <td class="p-3 text-right space-x-1.5">
            ${isPending ? `
              <button onclick="window.handleCFOApprove('${item.approval_id}')" class="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] transition shadow-sm cursor-pointer">Approve</button>
              <button onclick="window.handleCFOReject('${item.approval_id}')" class="px-2.5 py-1 rounded bg-rose-600/80 hover:bg-rose-500 text-white font-semibold text-[11px] transition cursor-pointer">Reject</button>
            ` : `<span class="text-slate-500 italic text-[11px]">Decided</span>`}
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("CFO queue refresh error", err);
  }
}

// Aliases for component imports
export const fetchCfoQueue = fetchCFOQueue;
export const approveEscalation = approveCFOItem;
export const rejectEscalation = rejectCFOItem;
export const refreshCfoQueueUI = refreshCFOQueueUI;
