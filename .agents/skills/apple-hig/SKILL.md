---
name: apple-hig
description: Apple Human Interface Guidelines reference with platform-specific design rules, component specs, measurements, and interaction patterns for iOS, iPadOS, macOS, and visionOS.
---

# Apple Human Interface Guidelines (HIG) & Mac-Level Craft

## 1. Materials & Translucency
- **Vibrancy & Frosted Glass**: Use `backdrop-filter: blur(20px) saturate(180%)`.
- **Specular Edge Ring**: Every translucent surface must have a 1px border highlight:
  - Dark mode: `border: 1px solid rgba(255, 255, 255, 0.12); box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15);`
  - Light mode: `border: 1px solid rgba(0, 0, 0, 0.08); box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);`
- **Avoid Muddy Shadows**: Use multi-stop ambient + key shadows:
  `box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08), 0 20px 25px -5px rgba(0,0,0,0.12);`

## 2. Spring Physics & Motion
- Standard Apple Spring Curve: `cubic-bezier(0.32, 0.72, 0, 1)` for drawers and sheets.
- Snappy Modal Pop-in: `cubic-bezier(0.16, 1, 0.3, 1)`.
- Never start from `scale(0)`: Always scale from `scale(0.96) -> scale(1)` with `opacity: 0 -> 1`.
- Haptic Active Press: `:active { transform: scale(0.97); transition: transform 90ms ease-out; }`.

## 3. macOS Window & HUD Controls
- Standard traffic lights: Close (red `#ff5f56`), Minimize (yellow `#ffbd2e`), Expand (green `#27c93f`).
- Pinned toolbars with subtle border separators (`rgba(255, 255, 255, 0.08)`).
- Monospace keyboard badges: `<kbd class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-white/10 border border-white/20">⌘K</kbd>`.
