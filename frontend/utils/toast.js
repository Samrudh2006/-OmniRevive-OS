/**
 * RazorRevive-OS Floating Toast Notification System
 */

export function showToast(message, type = "info") {
  let toastContainer = document.getElementById("rr-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "rr-toast-container";
    toastContainer.className = "fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm pointer-events-none";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.className = `p-3.5 rounded-xl shadow-2xl border text-xs font-semibold flex items-center gap-2.5 transform transition-all duration-300 translate-y-[-10px] opacity-0 pointer-events-auto select-none ${
    type === "success" 
      ? "bg-[#062c1d] border-emerald-500/60 text-emerald-200" 
      : type === "warning" 
        ? "bg-[#2d1b06] border-amber-500/60 text-amber-200" 
        : type === "error" 
          ? "bg-[#2d0a0f] border-rose-500/60 text-rose-200" 
          : "bg-[#081b36] border-sky-500/60 text-sky-200"
  }`;

  const icon = type === "success" 
    ? "✓" 
    : type === "warning" 
      ? "⚡" 
      : type === "error" 
        ? "✕" 
        : "ℹ";

  toast.innerHTML = `
    <span class="w-5 h-5 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
      type === "success" 
        ? "bg-emerald-500 text-black" 
        : type === "warning" 
          ? "bg-amber-400 text-black" 
          : type === "error" 
            ? "bg-rose-500 text-white" 
            : "bg-sky-400 text-black"
    }">${icon}</span>
    <span class="leading-tight">${message}</span>
  `;

  toastContainer.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-[-10px]", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");
  });

  // Animate out & remove
  setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-[-10px]", "opacity-0");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
