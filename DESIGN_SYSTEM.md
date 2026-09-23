# 🎨 DESIGN_SYSTEM.md
> `Design. Build. Ship. Consistently.`

# Design System Specification
**A consistent and scalable fintech engineering design system for a beautiful, modern, and accessible control plane.**

---

## 01 Brand Identity

Our visual identity reflects mission-critical precision, institutional luxury, and deep mathematical engineering. Inspired by Linear, Stripe Terminal, Bloomberg Professional, and Vercel Interfaces.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚡ OmniRevive-OS               Universal Autonomous AI Revenue Recovery    │
│  High-Frequency Fintech Control Plane • NPCI UPI 2.0 • Juspay • PhonePe      │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Core Aesthetic**: Obsidian Navy surfaces (`#030712`, `#060d1d`), 1px razor-sharp alpha gradient border strokes, specular reflections, and glowing electric cyan/emerald telemetry beacons.
* **Anti-Slop Standard**: Explicitly forbidden are generic purple-indigo gradients, uncalibrated borderless cards, and flickering numeric displays.
* **Tactile Haptic Feedback**: Every state transition produces sub-100ms visual scale response (`scale(0.96)`) and synthesized Web Audio micro-chords.

---

## 02 Color Palette

Use these calibrated semantic design tokens consistently across Web and Mobile:

| Color Name | Token / CSS Variable | Hex Code (Dark) | Hex Code (Light) | Semantic Role |
| :--- | :--- | :--- | :--- | :--- |
| **Canvas Background** | `--background` | `#030712` | `#f4f8fe` | Main viewport canvas |
| **Surface Primary** | `--surface` | `#060d1d` | `#ffffff` | Primary container cards & panels |
| **Surface Elevated** | `--surface-elevated`| `#091427` | `#ffffff` | Elevated modals, drawers, floating HUDs |
| **Surface Muted** | `--surface-muted` | `#101e38` | `#e2efff` | Table headers, chip backgrounds |
| **Border Subtle** | `--border-subtle` | `#0f1c34` | `#d4e5f9` | 1px card separators |
| **Border Highlight** | `--border` | `#101e38` | `#b8daff` | Active border strokes |
| **Brand Blue** | `--color-brand` | `#0c55ea` | `#0c6cf2` | Primary buttons & core brand accents |
| **Electric Cyan** | `--color-cyan` | `#06b6d4` | `#0284c7` | Live network telemetry & active beacons |
| **Emerald Green** | `--color-emerald` | `#10b981` | `#059669` | Recovered revenue, success states |
| **Amber Gold** | `--color-amber` | `#f59e0b` | `#d97706` | Circuit warnings, pending retry queues |
| **Rose Crimson** | `--color-rose` | `#f43f5e` | `#dc2626` | Failed transactions, attack detections |
| **Violet Purple** | `--color-purple` | `#8b5cf6` | `#7c3aed` | Cryptographic audit blocks, AI agents |
| **Text Primary** | `--text-primary` | `#f8fafc` | `#0c2340` | Headings, hero titles, active labels |
| **Text Secondary** | `--text-secondary` | `#cbd5e1` | `#1b3152` | Body descriptions, table text |
| **Text Muted** | `--text-muted` | `#94a3b8` | `#475569` | Metadata, timestamps, subtitles |

---

## 03 Typography

We use **Plus Jakarta Sans** for crisp institutional UI typography and **JetBrains Mono** for tabular numbers, code terminals, and cryptographic hashes.

```
Plus Jakarta Sans   Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz
JetBrains Mono      0123456789  ₹  $  €  £  %  +  -  =  _  /  #  [  ]  {  }
```

### Font Scale & Hierarchy:

| Token / Style | Font Size | Line Height | Font Weight | CSS Utility | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display / H1** | `clamp(2.0rem, 1.5rem + 2vw, 3.25rem)` | `1.1` | **900 (Black)** | `text-4xl sm:text-5xl font-black` | Hero headlines, landing titles |
| **H2** | `clamp(1.5rem, 1.25rem + 1vw, 2.25rem)` | `1.2` | **800 (ExtraBold)** | `text-2xl sm:text-3xl font-extrabold` | Section headers, major modal titles |
| **H3** | `clamp(1.2rem, 1.0rem + 0.5vw, 1.5rem)` | `1.3` | **700 (Bold)** | `text-lg sm:text-xl font-bold` | Card titles, sub-section headers |
| **H4** | `clamp(0.95rem, 0.9rem + 0.25vw, 1.15rem)`| `1.4` | **600 (SemiBold)** | `text-sm sm:text-base font-semibold` | Widget headers, table group labels |
| **Body** | `clamp(0.875rem, 0.85rem + 0.2vw, 1.0rem)` | `1.6` | **400 / 500 (Regular/Medium)** | `text-xs sm:text-sm font-normal` | Paragraphs, documentation text |
| **Caption** | `clamp(0.75rem, 0.7rem + 0.15vw, 0.85rem)` | `1.5` | **500 (Medium)** | `text-[11px] sm:text-xs text-slate-400` | Micro-copy, metadata, footnotes |
| **Monospace** | `clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)` | `1.4` | **600 (SemiBold)** | `font-mono tabular-nums` | ₹ amounts, latencies, hashes |

---

## 04 Spacing Scale

Adheres strictly to an 8-point geometric spatial scale for harmonious visual balance:

```
[4px]   [8px]     [16px]       [24px]         [32px]           [48px]             [64px]
 0.5     1.0       2.0          3.0            4.0              6.0                8.0
```

| Spacing Token | Pixels | Tailwind Class | Application |
| :--- | :--- | :--- | :--- |
| **3xs** | `2px` | `gap-0.5`, `p-0.5` | Micro-pill badges, indicator dots |
| **2xs** | `4px` | `gap-1`, `p-1` | Tight chip lists, icon-text gap |
| **xs** | `8px` | `gap-2`, `p-2` | Button inner padding, grid mini gaps |
| **sm** | `12px` | `gap-3`, `p-3` | Compact card padding, form inputs |
| **md** | `16px` | `gap-4`, `p-4` | Standard card body padding, stack gap |
| **lg** | `24px` | `gap-6`, `p-6` | Major dashboard grid spacing |
| **xl** | `32px` | `gap-8`, `p-8` | Section container separation |
| **2xl** | `48px` | `gap-12`, `py-12` | Landing showcase vertical spacing |
| **3xl** | `64px` | `gap-16`, `py-16` | Hero viewport padding |

---

## 05 Border Radius

```
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ╭───────╮
│  4px  │   │  8px  │   │ 12px  │   │ 16px  │   │ 24px  │   │ Full  │
└───────┘   └───────┘   └───────┘   └───────┘   └───────┘   ╰───────╯
```

* **`rounded-sm` (4px)**: Code tags, miniature telemetry dots.
* **`rounded-md` (8px)**: Table rows, dropdown menu items, compact buttons.
* **`rounded-lg` (12px)**: Form inputs, action buttons, alert boxes.
* **`rounded-xl` (16px)**: Standard cards, widgets, console terminals.
* **`rounded-2xl` (24px)**: Major hero containers, modal dialogs, drawer panels.
* **`rounded-full` (9999px)**: Navigation capsules, status pills, avatar rings.

---

## 06 Reusable UI Components

### A. Primary Action Buttons
```html
<button class="liquid-btn rzp-btn-primary px-4.5 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2">
  <span>⚡</span>
  <span>Run Fast-Loop Recovery</span>
</button>
```
* **Hover**: Specular light sweep across button surface (`transition: left 700ms var(--ease-out)`).
* **Active Press**: `transform: scale(0.96) translateY(1px);` with glowing liquid ripple.

### B. Lightswind Dynamic Spotlight Cards
```html
<div class="custom-card lightswind-spotlight p-6 rounded-2xl">
  <!-- Interactive card content that tracks cursor (x, y) with radial light sheen -->
</div>
```

### C. Kinetic Rolling Digit Odometer
```html
<span class="odometer-wrapper font-mono text-emerald-400 font-bold" data-odometer>
  ₹4,15,450.31
</span>
```
* Smooth vertical rolling reels for zero layout jitter on numeric updates.

### D. Input Fields & Form Controls
```html
<div class="relative">
  <input type="text" class="w-full px-4 py-2.5 rounded-xl bg-[#060d1d] border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 text-xs font-mono">
</div>
```

---

## 07 Iconography & Visual Assets

We use crisp, geometric SVG vector icons with glowing alpha highlights:

* ⚡ **Lightning Bolt**: Fast-Loop sub-50ms autonomous recovery.
* 🛡️ **Shield Guard**: AWS Cedar Zero-Trust policy gatekeeper.
* 📈 **Chart Curve**: SciPy continuous Weibull hazard survival peak.
* 🎙️ **Microphone / Waveform**: Trilingual neural voice negotiation FSM.
* 📜 **Chained Scroll**: Immutable SHA-256 Merkle audit ledger.
* 🪐 **Hex-Cube / Constellation**: Multi-rail fintech topology switch matrix.

---

## 08 Responsive Breakpoints

| Breakpoint | Target Screen Width | Layout Strategy |
| :--- | :--- | :--- |
| **Mobile (`<640px`)** | `320px – 639px` | Single-column stack, bottom drawer action sheet, 16px minimum input font size to prevent iOS zoom. |
| **Tablet (`sm / md`)** | `640px – 1023px` | 2-column card grid, collapsible sidebar navigation. |
| **Laptop (`lg / xl`)** | `1024px – 1439px` | Multi-pane split view, compact single-line navigation capsule, zero navbar overlap. |
| **Desktop (`2xl`)** | `1440px – 1535px` | Full 12-column engineering control plane with real-time telemetry sidebar. |
| **Ultra-Wide (`3xl`)** | `≥1536px` | 1536px max-width container, live USD/INR forex ticker & IST clock pill. |
