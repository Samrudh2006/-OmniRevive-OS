/**
 * Godly Motion Engine — OmniRevive-OS
 * Implements:
 * 1. Kinetic Rolling Digit Odometer (inspired by rolling.kitlangton.dev)
 * 2. Lightswind Dynamic Mouse-Follow Spotlight Beam (inspired by lightswind.com)
 * 3. Liquid Glass Tactile Click Ripple (inspired by venganceui.com)
 * 4. GetLayers 3D Depth Card Tilt (inspired by getlayers.ai)
 */

class GodlyMotionEngine {
  constructor() {
    this.isInitialized = false;
    this.mouseCoords = { x: 0, y: 0 };
    this.rafScheduled = false;
  }

  init() {
    if (this.isInitialized || typeof window === 'undefined') return;
    this.isInitialized = true;

    this.bindSpotlightTracker();
    this.bindLiquidRipples();
    this.bind3DTilt();
    this.upgradeExistingCounters();
  }

  /**
   * 1. Lightswind Spotlight Tracker: Updates local card CSS variables on pointermove
   */
  bindSpotlightTracker() {
    document.addEventListener('pointermove', (e) => {
      if (this.rafScheduled) return;
      this.rafScheduled = true;

      requestAnimationFrame(() => {
        this.rafScheduled = false;
        const target = e.target.closest?.('.custom-card, .matrix-card, .spotlight-card, .node-card-surface, .layer-plane-3d');
        if (target) {
          const rect = target.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          target.style.setProperty('--mouse-x', `${x}px`);
          target.style.setProperty('--mouse-y', `${y}px`);
        }
      });
    }, { passive: true });
  }

  /**
   * 2. Liquid Glass Click Ripple: Spawns a fluid glowing ripple on press
   */
  bindLiquidRipples() {
    document.addEventListener('pointerdown', (e) => {
      const btn = e.target.closest?.('.liquid-btn, .btn-primary, .btn-secondary, .btn-danger, #btn-fast-loop-simulate, #btn-trigger-voice, #btn-verify-merkle');
      if (!btn) return;

      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'liquid-ripple';
      
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 550);
    }, { passive: true });
  }

  /**
   * 3. GetLayers 3D Isometric Tilt
   */
  bind3DTilt() {
    document.addEventListener('pointermove', (e) => {
      const card = e.target.closest?.('.layer-plane-3d, .tilt-card');
      if (!card) return;

      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;

      card.style.transform = `perspective(1000px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) translateZ(8px)`;
    }, { passive: true });

    document.addEventListener('pointerleave', (e) => {
      const card = e.target.closest?.('.layer-plane-3d, .tilt-card');
      if (card) {
        card.style.transform = '';
      }
    }, { capture: true, passive: true });
  }

  /**
   * 4. Kinetic Rolling Digit Odometer (Kit Langton standard)
   * Turns static numbers into a mechanical rolling reel:
   * e.g., "₹18,420,950" -> [₹, 1, 8, ,, 4, 2, 0, ,, 9, 5, 0] with rolling vertical reels
   */
  updateOdometer(element, targetText) {
    if (!element) return;
    const str = String(targetText);

    // If first time or structure changed, build reel columns
    if (!element.classList.contains('odometer-wrapper') || element.dataset.lastLen !== String(str.length)) {
      element.classList.add('odometer-wrapper');
      element.dataset.lastLen = String(str.length);
      element.innerHTML = '';

      for (let i = 0; i < str.length; i++) {
        const char = str[i];
        if (/\d/.test(char)) {
          const col = document.createElement('span');
          col.className = 'odometer-digit-col';
          
          const reel = document.createElement('span');
          reel.className = 'odometer-reel';
          reel.dataset.digitIndex = String(i);
          
          for (let d = 0; d <= 9; d++) {
            const digitSpan = document.createElement('span');
            digitSpan.className = 'odometer-char';
            digitSpan.textContent = String(d);
            reel.appendChild(digitSpan);
          }
          
          col.appendChild(reel);
          element.appendChild(col);
        } else {
          const staticChar = document.createElement('span');
          staticChar.className = 'odometer-char';
          staticChar.textContent = char;
          element.appendChild(staticChar);
        }
      }
    }

    // Scroll reels to target digits
    let digitIdx = 0;
    const reels = element.querySelectorAll('.odometer-reel');
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      if (/\d/.test(char)) {
        const val = parseInt(char, 10);
        const reel = reels[digitIdx];
        if (reel) {
          reel.style.transform = `translateY(-${val * 10}%)`;
        }
        digitIdx++;
      }
    }
  }

  upgradeExistingCounters() {
    const metricElements = document.querySelectorAll('[data-odometer], #hero-recovered-amount, #stat-total-recovered, #stat-recovery-rate');
    metricElements.forEach(el => {
      const currentText = el.textContent.trim();
      if (currentText) {
        this.updateOdometer(el, currentText);
      }
    });
  }
}

export const godlyMotion = new GodlyMotionEngine();

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => godlyMotion.init());
  } else {
    godlyMotion.init();
  }
}
