/**
 * OmniRevive-OS — HTML & CSV Sanitization Utilities
 * Prevents Cross-Site Scripting (XSS) and CSV Formula Injection attacks.
 */

export function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function sanitizeCsvCell(value) {
  if (value === null || value === undefined) return "";
  let str = String(value).trim();
  // Neutralize CSV formula injection characters (=, +, -, @, tab, CR)
  if (/^[=+\-@\t\r]/.test(str)) {
    str = "'" + str;
  }
  // Wrap in quotes if containing comma, newline, or double quote
  if (str.includes(",") || str.includes('"') || str.includes("\n") || str.includes("\r")) {
    str = `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}
