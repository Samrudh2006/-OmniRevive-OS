/**
 * RazorRevive-OS — Utility Formatters & Compliance Validators
 * Implements Indian Fintech formatting (INR currency, IST timestamps, PII masking, GSTIN regex)
 */

export function formatINR(val, includeDecimals = true) {
  if (val === null || val === undefined || isNaN(val)) return "₹0.00";
  const num = Number(val);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: includeDecimals ? 2 : 0,
    maximumFractionDigits: includeDecimals ? 2 : 0
  }).format(num);
}

export function formatDateIST(epochOrIso) {
  if (!epochOrIso) return "N/A";
  const date = typeof epochOrIso === "number" ? new Date(epochOrIso * 1000) : new Date(epochOrIso);
  return date.toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  }) + " IST";
}

export function maskPII(str) {
  if (!str) return "N/A";
  if (str.includes("@")) {
    const [user, domain] = str.split("@");
    if (user.length <= 2) return `${user[0]}*@${domain}`;
    return `${user[0]}***${user.slice(-1)}@${domain}`;
  }
  const digits = str.replace(/[^\d+]/g, "");
  if (digits.length >= 10) {
    return `${digits.slice(0, 4)}******${digits.slice(-2)}`;
  }
  return str.slice(0, 2) + "****";
}

export function validateGSTIN(gstin) {
  if (!gstin || gstin.toUpperCase() === "UNREGISTERED") return true;
  const clean = gstin.trim().toUpperCase();
  if (clean.length !== 15) return false;
  const stateCode = parseInt(clean.substring(0, 2), 10);
  if (!((stateCode >= 1 && stateCode <= 37) || stateCode === 97)) return false;
  const regex = /^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
  return regex.test(clean);
}
