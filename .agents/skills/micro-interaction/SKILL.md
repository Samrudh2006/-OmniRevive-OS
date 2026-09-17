---
name: micro-interaction
description: UI motion guidance for hover and press feedback, toggles, toasts, drawers, modals, list transitions, and shared-element interactions.
---

# Micro-Interactions & Tactile Feedback

## Press Feedback
All clickable elements must respond immediately on `:active`:
```css
button:active, a.button:active, [role="button"]:active {
  transform: scale(0.97);
  transition: transform 90ms ease-out;
}
```

## Icon Hover
Icons inside buttons or cards should have subtle spatial micro-motion on parent hover:
```css
.card:hover .card-icon {
  transform: translateY(-2px) scale(1.08);
  transition: transform 180ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

## Toast Kinematics (Sonner style)
- Enter: `translateY(12px) scale(0.96) -> translateY(0) scale(1)` with `cubic-bezier(0.16, 1, 0.3, 1)`.
- Exit: `translateY(-12px) scale(0.96)` with opacity fade.
