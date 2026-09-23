# 🤖 AGENTS.md
> `Build better, together.`

# Agent Instructions
**Guidelines, operational invariants, and rules for AI coding agents working on OmniRevive-OS.**

---

## 01 Purpose

This document provides strict instructions, context, and operational rules for AI coding agents (Claude, Gemini, Cursor, Copilot, Antigravity) working on OmniRevive-OS. Follow these guidelines to maintain mission-critical stability, zero double-debit guarantees, anti-slop visual quality, and 100% web-mobile parity.

---

## 02 Before You Start

- [x] Read [`PRD.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/PRD.md) to understand product goals, multi-rail routing, and recovery metrics.
- [x] Read [`DESIGN_SYSTEM.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/DESIGN_SYSTEM.md) for color tokens, typography scales, and tactile physics.
- [x] Read [`ARCHITECTURE.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/ARCHITECTURE.md) for system boundaries, dual-speed loops, and Redis CAS mutexes.
- [x] Check existing modular components in `frontend/components/` and services in `backend/app/services/`.
- [x] Run `python cli.py benchmark` to verify the 100-case baseline before making functional edits.

---

## 03 General Rules

- [x] **No AI Slop**: Do NOT introduce generic purple gradients, flat card layouts, or sluggish UI animations. Adhere to the Obsidian Navy palette.
- [x] **Zero Extra Dependencies**: Use standard Python libraries (`FastAPI`, `SciPy`, `NumPy`) and pure Vanilla CSS/JS. Do not install heavy external libraries without necessity.
- [x] **Maintain 100% Web & Mobile Parity**: Any change made in `frontend/index.html` or `frontend/pages/` MUST be replicated into `mobile/app/src/main/assets/www/`.
- [x] **Tabular Numeric Alignment**: All currency streams, metrics, and timestamps MUST use `font-mono tabular-nums` (`font-variant-numeric: tabular-nums`).
- [x] **Write Clean, Modular Code**: Keep functions focused, add descriptive docstrings, and handle all edge cases explicitly.

---

## 04 Code Guidelines

```html
<!-- Example: Standard Tactile Liquid Button -->
<button class="liquid-btn rzp-btn-primary px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2">
  <span>⚡</span>
  <span>Action Name</span>
</button>
```

- [x] **Sub-100ms Tactile Physics**: All interactive buttons, chips, and triggers must have `active:scale-95` or `:active { transform: scale(0.96); }`.
- [x] **Custom Cubic-Bézier Curves**: Use `--ease-out: cubic-bezier(0.16, 1, 0.3, 1)` for snappy UI and `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)` for morphing.
- [x] **Explicit Error Schemas**: All FastAPI route handlers must return structured JSON envelopes with `success`, `data`, and `trace_id`.
- [x] **Safe Media Fallbacks**: When referencing avatars or images, always provide zero-flash SVG data-URI fallbacks (`window.COPILOT_AVATAR_FALLBACK`).

---

## 05 Security & Best Practices

- [x] **Strict 0 Double-Debits Guarantee**: All transaction mutations MUST acquire a Redis Compare-And-Swap (CAS) distributed lock before execution.
- [x] **Constant-Time Cryptography**: Use `hmac.compare_digest()` for API keys, bearer tokens, and webhook signature verification.
- [x] **TRAI Quiet Hours Compliance**: Never execute outbound consumer notifications or retries between 21:00 and 09:00 IST unless customer-initiated.
- [x] **AWS Cedar Policy Guardrails**: Enforce discount bounds (`<=10%`, `<=₹500`) and place high-ticket actions into the CFO dual-key quarantine queue.
- [x] **Merkle Audit Integrity**: Every state-altering action must append a SHA-256 block to the immutable audit ledger.

---

## 06 Useful Commands

```bash
# 1. Run 100-Case Production Benchmark Suite
python cli.py benchmark

# 2. Verify Cryptographic Merkle Audit Chain (15,000+ Blocks)
python cli.py verify-audit

# 3. Run Full Automated Test Suite (Pytest)
pytest tests/ -v

# 4. Start Local Development Server (Port 8080)
python -m http.server 8080 --directory frontend

# 5. Start Backend FastAPI Kernel
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 07 Need Help?

* **Architecture Questions**: Consult [`ARCHITECTURE.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/ARCHITECTURE.md).
* **Design & Styling Tokens**: Consult [`DESIGN_SYSTEM.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/DESIGN_SYSTEM.md).
* **Traffic & Search Indexing**: Consult [`docs/GROWTH_AND_TRAFFIC_ENGINE.md`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/docs/GROWTH_AND_TRAFFIC_ENGINE.md).
* **Benchmark Evidence**: Run `python cli.py benchmark` or inspect `benchmarks/`.

**Let's build something world-class! 🚀**
