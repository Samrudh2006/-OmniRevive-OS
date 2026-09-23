/**
 * RazorRevive-OS Sonner-Grade Toast Notification System
 * Conforms to Emil Kowalski's design engineering standards (ask-sonner & animations.dev)
 */

export function showToast(message, type = "info") {
  let toastContainer = document.getElementById("rr-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "rr-toast-container";
    toastContainer.className = "fixed z-50 flex flex-col gap-2 max-w-sm pointer-events-none";
    toastContainer.setAttribute("role", "region");
    toastContainer.setAttribute("aria-label", "Notifications");
    toastContainer.setAttribute("aria-live", "polite");
    toastContainer.setAttribute("aria-atomic", "true");
    toastContainer.style.top = "max(1rem, env(safe-area-inset-top, 16px))";
    toastContainer.style.right = "max(1rem, env(safe-area-inset-right, 16px))";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.setAttribute("role", type === "error" ? "alert" : "status");
  
  const isDark = document.documentElement.classList.contains("dark");
  toast.className = `p-3.5 rounded-2xl shadow-xl border text-xs font-bold flex items-center gap-2.5 pointer-events-auto select-none backdrop-blur-xl cursor-pointer transition-all`;
  
  if (!isDark) {
    toast.style.background = "#ffffff";
    toast.style.color = "#0f172a";
    toast.style.borderColor = type === "success" ? "#10b981" : type === "warning" ? "#f59e0b" : type === "error" ? "#f43f5e" : "#0ea5e9";
    toast.style.borderWidth = "1.5px";
    toast.style.boxShadow = "0 10px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08)";
  } else {
    toast.style.background = "#0f172a";
    toast.style.color = "#f8fafc";
    toast.style.borderColor = type === "success" ? "rgba(16, 185, 129, 0.4)" : type === "warning" ? "rgba(245, 158, 11, 0.4)" : type === "error" ? "rgba(244, 63, 94, 0.4)" : "rgba(14, 165, 233, 0.4)";
    toast.style.borderWidth = "1.5px";
    toast.style.boxShadow = "0 20px 25px -5px rgba(0, 0, 0, 0.5)";
  }

  // Emil Kowalski Physicality: Initial presentation state (scale 0.96, translateY 12px, opacity 0)
  toast.style.transform = "translateY(12px) scale(0.96)";
  toast.style.opacity = "0";
  toast.style.transition = "transform 220ms cubic-bezier(0.23, 1, 0.32, 1), opacity 200ms cubic-bezier(0.23, 1, 0.32, 1)";
  toast.style.willChange = "transform, opacity";

  const icon = type === "success" 
    ? "✓" 
    : type === "warning" 
      ? "⚡" 
      : type === "error" 
        ? "✕" 
        : "ℹ";

  const badgeBg = type === "success" 
    ? "#10b981" 
    : type === "warning" 
      ? "#f59e0b" 
      : type === "error" 
        ? "#f43f5e" 
        : "#0ea5e9";

  toast.innerHTML = `
    <span style="background: ${badgeBg}; color: #ffffff;" class="w-6 h-6 rounded-full flex items-center justify-center font-black text-xs shrink-0 shadow-sm">${icon}</span>
    <span style="color: ${!isDark ? '#0f172a' : '#f8fafc'};" class="leading-tight flex-1 font-bold text-xs">${message}</span>
  `;

  // Tap or click to dismiss instantly
  toast.addEventListener("click", () => dismissToast(toast));

  toastContainer.appendChild(toast);

  // Smooth entrance using double rAF to guarantee style calculation
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.style.transform = "translateY(0) scale(1)";
      toast.style.opacity = "1";
    });
  });

  // Auto-dismiss after 3.5s
  const timer = setTimeout(() => {
    dismissToast(toast);
  }, 3500);

  function dismissToast(target) {
    clearTimeout(timer);
    target.style.transition = "transform 180ms cubic-bezier(0.23, 1, 0.32, 1), opacity 160ms cubic-bezier(0.23, 1, 0.32, 1)";
    target.style.transform = "translateY(-8px) scale(0.97)";
    target.style.opacity = "0";
    setTimeout(() => {
      if (target.parentNode) {
        target.remove();
      }
    }, 190);
  }
}

