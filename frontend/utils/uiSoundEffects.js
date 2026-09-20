/**
 * OmniRevive-OS Modern Web Audio UI Sound Synthesizer
 * Provides subtle, high-frequency micro-interaction audio feedback for buttons, links, toggles & inputs.
 * Zero external audio files required — dynamically synthesizes crisp futuristic sound waves.
 */

let audioCtx = null;
let soundEnabled = true;

// Load stored sound preference (default: true)
try {
  const pref = localStorage.getItem("omni_ui_sounds_enabled");
  if (pref !== null) {
    soundEnabled = pref === "true";
  }
} catch (e) {}

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

export function isUiSoundEnabled() {
  return soundEnabled;
}

export function toggleUiSounds(enable) {
  if (enable === undefined) {
    soundEnabled = !soundEnabled;
  } else {
    soundEnabled = !!enable;
  }
  try {
    localStorage.setItem("omni_ui_sounds_enabled", soundEnabled ? "true" : "false");
  } catch (e) {}
  
  if (soundEnabled) {
    playUiSound("toggle");
  }
  return soundEnabled;
}

/**
 * Synthesizes crisp UI acoustic feedback using Web Audio API oscillators and gain envelopes
 * Types: 'click', 'primary', 'success', 'danger', 'hover', 'toggle', 'tab'
 */
export function playUiSound(type = "click") {
  if (!soundEnabled) return;

  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === "hover") {
      // Extremely subtle, high-pitch soft tick for hover (non-intrusive)
      osc.type = "sine";
      osc.frequency.setValueAtTime(1400, now);
      osc.frequency.exponentialRampToValueAtTime(1800, now + 0.012);
      
      gain.gain.setValueAtTime(0.012, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.012);
      
      osc.start(now);
      osc.stop(now + 0.012);
    } else if (type === "primary" || type === "cta") {
      // Tech-pulse two-tone ascending pop for primary buttons
      osc.type = "triangle";
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.035);
      
      gain.gain.setValueAtTime(0.07, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.035);

      osc.start(now);
      osc.stop(now + 0.035);
    } else if (type === "danger" || type === "reject") {
      // Low pitch subtle click for destructive actions
      osc.type = "sine";
      osc.frequency.setValueAtTime(260, now);
      osc.frequency.exponentialRampToValueAtTime(130, now + 0.045);

      gain.gain.setValueAtTime(0.07, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.045);

      osc.start(now);
      osc.stop(now + 0.045);
    } else if (type === "success") {
      // Bright major interval chime
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.connect(gain2);
      gain2.connect(ctx.destination);

      osc.type = "sine";
      osc2.type = "sine";

      osc.frequency.setValueAtTime(523.25, now); // C5
      osc2.frequency.setValueAtTime(659.25, now + 0.025); // E5

      gain.gain.setValueAtTime(0.05, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

      gain2.gain.setValueAtTime(0.05, now + 0.025);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.075);

      osc.start(now);
      osc.stop(now + 0.05);
      osc2.start(now + 0.025);
      osc2.stop(now + 0.075);
    } else if (type === "toggle" || type === "tab") {
      // Clean springy bubble pop
      osc.type = "sine";
      osc.frequency.setValueAtTime(600, now);
      osc.frequency.exponentialRampToValueAtTime(1200, now + 0.02);

      gain.gain.setValueAtTime(0.04, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);

      osc.start(now);
      osc.stop(now + 0.02);
    } else {
      // Standard clean micro-click
      osc.type = "sine";
      osc.frequency.setValueAtTime(900, now);
      osc.frequency.exponentialRampToValueAtTime(350, now + 0.02);

      gain.gain.setValueAtTime(0.035, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);

      osc.start(now);
      osc.stop(now + 0.02);
    }
  } catch (err) {
    // Silent fail if AudioContext is blocked or unsupported
  }
}

/**
 * Attaches global event delegation for clicks and hover events across ALL buttons, links & interactive controls.
 */
export function initGlobalUiSounds() {
  let lastHoverTime = 0;

  // Unlock AudioContext on first user gesture anywhere on page
  const unlockAudio = () => {
    getAudioContext();
    document.removeEventListener("pointerdown", unlockAudio);
    document.removeEventListener("keydown", unlockAudio);
  };
  document.addEventListener("pointerdown", unlockAudio, { passive: true, once: true });
  document.addEventListener("keydown", unlockAudio, { passive: true, once: true });

  // Global Click Event Listener (Event Delegation)
  document.addEventListener("click", (e) => {
    const target = e.target.closest(
      'button, a, input[type="button"], input[type="submit"], [role="button"], .cursor-pointer, .tab-btn, .btn, .nav-item, .action-btn'
    );
    if (!target) return;

    const classList = target.classList ? Array.from(target.classList).join(" ").toLowerCase() : "";
    const id = target.id ? target.id.toLowerCase() : "";
    const text = target.innerText ? target.innerText.toLowerCase() : "";

    if (classList.includes("bg-rose") || classList.includes("danger") || id.includes("reject") || text.includes("delete") || text.includes("reject")) {
      playUiSound("danger");
    } else if (classList.includes("bg-emerald") || classList.includes("success") || id.includes("approve") || text.includes("approve")) {
      playUiSound("success");
    } else if (classList.includes("bg-[#0c6cf2]") || classList.includes("bg-sky") || classList.includes("bg-indigo") || classList.includes("primary") || classList.includes("btn-primary") || classList.includes("btn-gradient")) {
      playUiSound("primary");
    } else if (classList.includes("tab") || target.tagName === "A" || classList.includes("nav")) {
      playUiSound("tab");
    } else {
      playUiSound("click");
    }
  }, { capture: true, passive: true });

  // Global Mouseover Event Listener for micro hover sound
  document.addEventListener("mouseover", (e) => {
    const target = e.target.closest(
      'button, a, [role="button"], .tab-btn, .btn, .action-btn'
    );
    if (!target) return;

    const now = Date.now();
    if (now - lastHoverTime < 70) return;
    lastHoverTime = now;

    playUiSound("hover");
  }, { capture: true, passive: true });

  // Expose toggle on window object
  window.toggleUiSounds = toggleUiSounds;
  window.playUiSound = playUiSound;
}
