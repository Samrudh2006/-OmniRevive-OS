# OmniRevive-OS Design System Specification (DESIGN.md)
*Version 2.4.0 — Unified 2026 Fintech Engineering Design Spec*
*Conforms to: Google Stitch DTCG Alpha, Anthropic Anti-Slop Directive, Vercel Web Interface Guidelines, Rauno Freiberg Interfaces, Bergside WCAG 2.2 AA, & Refactoring UI.*

---

## 1. Executive Aesthetic Directive: "The Anti-Slop Standard"

OmniRevive-OS is a mission-critical, Tier-1 distributed fintech control plane managing real-time revenue recovery across NPCI UPI 2.0, Juspay HyperSDK, PhonePe, CRED, Cashfree, Neobanks, and Stripe.

### Core Visual Principles
1. **No Generic AI Slop**: Explicitly forbidden are generic purple-indigo gradients, uninspired Inter/Roboto typography pairings, borderless flat cards, and chaotic neon eye-strain.
2. **High-Frequency Engineering Luxury**: Inspired by Linear, Stripe Terminal, and Bloomberg Professional. Deep Obsidian Navy surfaces (`#030712`, `#060b18`, `#0a1528`), razor-sharp 1px border strokes with subtle alpha gradients, electric cyan and emerald telemetry beacons, and tabular monospace data for zero-jitter numeric streams.
3. **Tactile Haptic Feedback**: Every state change produces instantaneous visual and synthesized audio confirmation (Web Audio API micro-ticks and harmonic chords). Zero perceptual feedback lag.
4. **Mathematical Precision**: Spacing adheres strictly to an 8-point geometric scale; elevation shadows utilize multi-layered ambient and directional drop-shadows (Refactoring UI).

---

## 2. Machine-Readable DTCG Design Tokens (Google Stitch Spec)

```yaml
tokens:
  color:
    background:
      canvas:
        dark: "#030712"
        light: "#f8fafc"
      surface_primary:
        dark: "#060d1d"
        light: "#ffffff"
      surface_secondary:
        dark: "#0a162c"
        light: "#f1f5f9"
      surface_elevated:
        dark: "#0e1e3a"
        light: "#ffffff"
    border:
      subtle:
        dark: "rgba(30, 58, 102, 0.4)"
        light: "rgba(226, 232, 240, 0.8)"
      focus:
        dark: "#06b6d4"
        light: "#0284c7"
      active:
        dark: "#10b981"
        light: "#059669"
    accent:
      cyan:
        base: "#06b6d4"
        glow: "rgba(6, 182, 212, 0.25)"
      emerald:
        base: "#10b981"
        glow: "rgba(16, 185, 129, 0.25)"
      amber:
        base: "#f59e0b"
        glow: "rgba(245, 158, 11, 0.25)"
      rose:
        base: "#f43f5e"
        glow: "rgba(244, 63, 94, 0.25)"
      violet:
        base: "#8b5cf6"
        glow: "rgba(139, 92, 246, 0.25)"
  typography:
    family_sans: "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    family_mono: "'JetBrains Mono', monospace"
    scale:
      xs: "clamp(0.7rem, 0.65rem + 0.25vw, 0.75rem)"
      sm: "clamp(0.8rem, 0.75rem + 0.25vw, 0.875rem)"
      base: "clamp(0.9rem, 0.85rem + 0.35vw, 1.0rem)"
      lg: "clamp(1.1rem, 1.0rem + 0.5vw, 1.25rem)"
      xl: "clamp(1.3rem, 1.15rem + 0.75vw, 1.5rem)"
      display: "clamp(1.75rem, 1.4rem + 1.5vw, 2.25rem)"
  motion:
    spring_snappy: "cubic-bezier(0.16, 1, 0.3, 1)"
    spring_bounce: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    duration_instant: "120ms"
    duration_fluid: "240ms"
    duration_smooth: "360ms"
```

---

## 3. Interaction & Correctness Guidelines (Vercel & Rauno Freiberg)

### Keyboard & Focus Accessibility (WCAG 2.2 AA)
- **Visible Focus Rings**: Every interactive element (`<button>`, `<a>`, `<input>`, `<select>`) MUST render a visible 2px focus ring (`ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-900`) when navigated via keyboard.
- **Global Command Palette**: `Cmd+K` / `Ctrl+K` must instantly open the search modal from any screen without layout jitter.
- **Zero Input Freeze**: Form controls and sliders must respond synchronously with optimistic client-side updates while background async API calls execute.

### Motion Rules & Tactile Engineering
- **Reduced Motion**: All animations MUST gracefully collapse to instant opacity fades whenever `@media (prefers-reduced-motion: reduce)` is active.
- **Button Micro-States**:
  - Hover: `transform: translateY(-1px); box-shadow: 0 4px 14px var(--glow);`
  - Active (Press): `transform: scale(0.97) translateY(0);`
- **Dynamic Splitters**: Multi-pane splitters must feature hover grab handles (`cursor: col-resize`), smooth dragging, and persistent size memory.

---

## 4. 3D Cyber-Topology & Network Visualization (Three.js WebGL)

### Spatial Scene Architecture
- **Camera**: Perspective camera at `(0, 0, 800)` with 45° FOV.
- **Constellation Nodes**: 7 regional fintech switch nodes:
  1. `AWS ap-south-1` (Mumbai Primary Core) — Electric Cyan
  2. `AWS ap-south-2` (Hyderabad Disaster Recovery) — Blue Slate
  3. `NPCI Central Switch` (UPI 2.0 National Hub) — Emerald
  4. `Juspay HyperSDK Switch` (Bangalore Low-Latency) — Gold Amber
  5. `PhonePe Yes Bank Switch` (Consumer Intent) — Purple
  6. `CRED CAS Engine` (High-Ticket Mutex) — Rose White
  7. `Stripe US-East-1 / Singapore` (Cross-Border FX) — Indigo
- **Packet Arcs**: Glowing quadratic Bézier curves with moving particle pulses representing live revenue recovery transactions.
- **Performance Guard**: Automatic frame throttler capped at 60 FPS; pauses WebGL render loop when tab is hidden.

---

## 5. Global Load Balancing & Server Reachability Matrix

### Telemetry Matrix Specification
- Continuous latency polling across all 7 regional switches.
- **SLA Thresholds**:
  - Latency `< 5ms`: `OPTIMAL (99.999% SLA)` — Glowing Emerald
  - Latency `5ms – 25ms`: `NOMINAL (99.95% SLA)` — Cyan
  - Latency `> 25ms`: `DEGRADED (Circuit Warning)` — Amber Alert
- **Load Balancer Switch Split**:
  - HDFC: 40%
  - ICICI: 35%
  - Axis: 20%
  - SBI: 5% (Throttled on 504 outage hazards)
- Real-time interactive actions:
  - `Rebalance Switch Weights` (Instant traffic distribution calculation)
  - `Trigger Simulated SBI 504 Outage` (Trips circuit breaker to verify 0.24ms failover)
  - `Ping All Regional Gateways` (Measures true sub-millisecond round trips)

---

## 6. Do's and Don'ts

| Do | Don't |
| :--- | :--- |
| **Use** monospaced numbers (`tabular-nums mono`) for money and metrics to prevent layout wobble. | **Don't** use proportional fonts for changing numeric counters. |
| **Use** multi-layered ambient and directional drop shadows for cards. | **Don't** use flat 1px solid black shadows or muddy blur. |
| **Use** curated OKLCH / HSL palette with high WCAG 2.2 AA contrast ratios. | **Don't** paste generic rainbow gradients or uncalibrated purple overlays. |
| **Use** Web Audio API synthesized micro-sounds for haptic feedback. | **Don't** load heavy external MP3 audio assets over the network. |
| **Use** fluid CSS `clamp()` for responsive typography across mobile and 4K displays. | **Don't** hardcode pixel font sizes (`14px`, `18px`) that break accessibility zoom. |
