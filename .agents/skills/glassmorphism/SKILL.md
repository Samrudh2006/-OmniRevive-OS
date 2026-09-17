---
name: glassmorphism
description: Frosted glass UI, Apple liquid glass style, frosted blur cards, translucent glass panel animation, specular highlights, and reduced-transparency fallbacks.
---

# Glassmorphism & Liquid Glass Craft

## Core Recipe
```css
.glass-panel {
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 8px 32px 0 rgba(0, 0, 0, 0.37),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.18);
}
```

## Rules
1. Never blur without saturation boost (`saturate(180%)`) or the background colors look muddy.
2. Inset top highlight (`inset 0 1px 0 rgba(255,255,255,0.18)`) creates the physical glass bevel.
3. Fallback for reduced transparency:
```css
@media (prefers-reduced-transparency: reduce) {
  .glass-panel {
    background: var(--assistant-background);
    backdrop-filter: none;
  }
}
```
