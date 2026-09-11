/**
 * RazorRevive-OS Graphify Engine
 * Interactive Directed Acyclic Graph (DAG) & Banking Mesh Topology.
 * Visualizes the real-time autonomous recovery pipeline, particle flow,
 * Cedar policy checkpoints, and chaos outage rerouting.
 */

export function initGraphifyDag(canvasId = "graphify-canvas") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext("2d");

  let activeNode = null;
  let chaosState = "NORMAL"; // "NORMAL", "SBI_504", "HMAC_TAMPER"
  let animationFrameId = null;

  function resize() {
    if (!canvas || !canvas.parentElement) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = rect.width || 800;
    const h = rect.height || 360;

    if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.scale(dpr, dpr);
    }
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
  }
  resize();
  window.addEventListener("resize", resize);

  // Define DAG Nodes layout across normalized coordinates (0..1)
  const nodes = [
    {
      id: "ingest",
      title: "Failure Ingestion",
      subtitle: "Webhook / NPCI Signal",
      nx: 0.10, ny: 0.50,
      color: "#38bdf8",
      icon: "⚡",
      latency: "0.4ms",
      throughput: "1,240 tx/s",
      status: "HEALTHY"
    },
    {
      id: "cedar",
      title: "AWS Cedar Zero-Trust",
      subtitle: "Policy Guardrail & Invariants",
      nx: 0.28, ny: 0.50,
      color: "#10b981",
      icon: "🛡️",
      latency: "1.2ms",
      throughput: "1,240 tx/s",
      status: "ENFORCING"
    },
    {
      id: "weibull",
      title: "Weibull Hazard Engine",
      subtitle: "Survival Probability +45m",
      nx: 0.48, ny: 0.28,
      color: "#a855f7",
      icon: "📈",
      latency: "0.8ms",
      throughput: "380 tx/s",
      status: "OPTIMAL"
    },
    {
      id: "optimizer",
      title: "Route Optimizer",
      subtitle: "Channel Suitability Vector",
      nx: 0.48, ny: 0.72,
      color: "#0284c7",
      icon: "🔀",
      latency: "1.5ms",
      throughput: "860 tx/s",
      status: "ACTIVE"
    },
    {
      id: "rail_upi",
      title: "Dynamic UPI Intent",
      subtitle: "1-Click App Switcher",
      nx: 0.72, ny: 0.20,
      color: "#10b981",
      icon: "📲",
      latency: "180ms",
      throughput: "510 tx/s",
      status: "STANDBY"
    },
    {
      id: "rail_wa",
      title: "WhatsApp Smart Drawer",
      subtitle: "Interactive Invoice Drawer",
      nx: 0.72, ny: 0.50,
      color: "#22c55e",
      icon: "💬",
      latency: "240ms",
      throughput: "240 tx/s",
      status: "ACTIVE"
    },
    {
      id: "rail_voice",
      title: "Multilingual Voice AI",
      subtitle: "Neerja / Shruti Neural FSM",
      nx: 0.72, ny: 0.80,
      color: "#8b5cf6",
      icon: "🎙️",
      latency: "12ms",
      throughput: "110 tx/s",
      status: "READY"
    },
    {
      id: "settlement",
      title: "Auto-Healing & Merkle",
      subtitle: "SHA-256 Ledger Consensus",
      nx: 0.92, ny: 0.50,
      color: "#10b981",
      icon: "💎",
      latency: "2.1ms",
      throughput: "860 tx/s",
      status: "IMMUTABLE"
    }
  ];

  // Define DAG Edges
  const edges = [
    { from: "ingest", to: "cedar" },
    { from: "cedar", to: "weibull" },
    { from: "cedar", to: "optimizer" },
    { from: "weibull", to: "rail_upi" },
    { from: "optimizer", to: "rail_wa" },
    { from: "optimizer", to: "rail_voice" },
    { from: "rail_upi", to: "settlement" },
    { from: "rail_wa", to: "settlement" },
    { from: "rail_voice", to: "settlement" }
  ];

  // Dynamic animated transaction packets traveling along edges
  const packets = [];
  for (let i = 0; i < 18; i++) {
    const edgeIndex = Math.floor(Math.random() * edges.length);
    packets.push({
      edgeIndex: edgeIndex,
      progress: Math.random(),
      speed: 0.006 + Math.random() * 0.008,
      size: 2.5 + Math.random() * 2
    });
  }

  // Mouse interaction for tooltip inspection
  let mouse = { x: -100, y: -100 };
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;

    const w = parseFloat(canvas.style.width);
    const h = parseFloat(canvas.style.height);

    let hovered = null;
    nodes.forEach(n => {
      const x = n.nx * w;
      const y = n.ny * h;
      const dist = Math.hypot(mouse.x - x, mouse.y - y);
      if (dist < 28) hovered = n;
    });
    activeNode = hovered;
    canvas.style.cursor = hovered ? "pointer" : "default";
  });

  canvas.addEventListener("click", () => {
    if (activeNode && window.showToast) {
      window.showToast(`Node ${activeNode.title}: Status ${activeNode.status} (P99: ${activeNode.latency})`, "info");
    }
  });

  function render() {
    const w = parseFloat(canvas.style.width) || canvas.width;
    const h = parseFloat(canvas.style.height) || canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Subtle background grid
    ctx.strokeStyle = "rgba(148, 163, 184, 0.04)";
    ctx.lineWidth = 1;
    const gridSize = 24;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Draw Edges (Glowing Bezier curves)
    edges.forEach((edge, idx) => {
      const fromNode = nodes.find(n => n.id === edge.from);
      const toNode = nodes.find(n => n.id === edge.to);
      if (!fromNode || !toNode) return;

      const x1 = fromNode.nx * w;
      const y1 = fromNode.ny * h;
      const x2 = toNode.nx * w;
      const y2 = toNode.ny * h;
      const cpx1 = x1 + (x2 - x1) * 0.5;
      const cpy1 = y1;
      const cpx2 = x1 + (x2 - x1) * 0.5;
      const cpy2 = y2;

      const isFailureEdge = chaosState === "SBI_504" && (edge.from === "ingest" || edge.from === "cedar");
      const isTamperEdge = chaosState === "HMAC_TAMPER" && edge.from === "cedar";

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.bezierCurveTo(cpx1, cpy1, cpx2, cpy2, x2, y2);

      if (isTamperEdge) {
        ctx.strokeStyle = "rgba(244, 63, 94, 0.8)";
        ctx.lineWidth = 2.5;
      } else if (isFailureEdge) {
        ctx.strokeStyle = "rgba(245, 158, 11, 0.8)";
        ctx.lineWidth = 2.2;
      } else {
        ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
        ctx.lineWidth = 1.6;
      }
      ctx.stroke();
    });

    // Draw Animated Packets along Edges
    packets.forEach(pkt => {
      const edge = edges[pkt.edgeIndex];
      if (!edge) return;
      const fromNode = nodes.find(n => n.id === edge.from);
      const toNode = nodes.find(n => n.id === edge.to);
      if (!fromNode || !toNode) return;

      pkt.progress += pkt.speed;
      if (pkt.progress > 1) {
        pkt.progress = 0;
        pkt.edgeIndex = Math.floor(Math.random() * edges.length);
      }

      const x1 = fromNode.nx * w;
      const y1 = fromNode.ny * h;
      const x2 = toNode.nx * w;
      const y2 = toNode.ny * h;
      const cpx1 = x1 + (x2 - x1) * 0.5;
      const cpy1 = y1;
      const cpx2 = x1 + (x2 - x1) * 0.5;
      const cpy2 = y2;

      // Cubic Bezier interpolation: B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t) t^2 P2 + t^3 P3
      const t = pkt.progress;
      const inv = 1 - t;
      const px = inv * inv * inv * x1 + 3 * inv * inv * t * cpx1 + 3 * inv * t * t * cpx2 + t * t * t * x2;
      const py = inv * inv * inv * y1 + 3 * inv * inv * t * cpy1 + 3 * inv * t * t * cpy2 + t * t * t * y2;

      ctx.beginPath();
      ctx.arc(px, py, pkt.size, 0, Math.PI * 2);
      ctx.fillStyle = chaosState === "HMAC_TAMPER" ? "#f43f5e" : (chaosState === "SBI_504" ? "#fbbf24" : "#38bdf8");
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0; // reset
    });

    // Draw Nodes
    nodes.forEach(n => {
      const x = n.nx * w;
      const y = n.ny * h;
      const isHovered = activeNode && activeNode.id === n.id;
      const isOutage = chaosState === "SBI_504" && (n.id === "ingest" || n.id === "rail_upi");
      const isBlocked = chaosState === "HMAC_TAMPER" && n.id === "cedar";

      // Outer glow pulse
      ctx.beginPath();
      ctx.arc(x, y, isHovered ? 26 : 20, 0, Math.PI * 2);
      let ringColor = n.color;
      if (isOutage) ringColor = "#f43f5e";
      if (isBlocked) ringColor = "#e11d48";
      ctx.fillStyle = isHovered ? `${ringColor}33` : `${ringColor}15`;
      ctx.fill();

      // Node circle border & fill
      ctx.beginPath();
      ctx.arc(x, y, isHovered ? 18 : 14, 0, Math.PI * 2);
      ctx.fillStyle = "#0a1526";
      ctx.fill();
      ctx.strokeStyle = ringColor;
      ctx.lineWidth = isHovered ? 2.5 : 1.8;
      ctx.stroke();

      // Node Icon
      ctx.font = isHovered ? "13px 'Plus Jakarta Sans', sans-serif" : "11px 'Plus Jakarta Sans', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(n.icon, x, y);

      // Node Title Label
      ctx.font = "600 11px 'Plus Jakarta Sans', sans-serif";
      ctx.fillStyle = isHovered ? "#f8fafc" : "#cbd5e1";
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      ctx.fillText(n.title, x, y - 24);

      // Node Subtitle / Metric
      ctx.font = "400 9px 'JetBrains Mono', monospace";
      ctx.fillStyle = isHovered ? "#38bdf8" : "#64748b";
      ctx.textBaseline = "top";
      ctx.fillText(n.latency, x, y + 22);
    });

    // Draw Hover Tooltip if active
    if (activeNode) {
      const x = activeNode.nx * w;
      const y = activeNode.ny * h;
      const tooltipW = 160;
      const tooltipH = 58;
      const tx = Math.min(Math.max(x - tooltipW / 2, 10), w - tooltipW - 10);
      const ty = y > h - 80 ? y - tooltipH - 25 : y + 28;

      ctx.fillStyle = "rgba(12, 24, 44, 0.95)";
      ctx.strokeStyle = activeNode.color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(tx, ty, tooltipW, tooltipH, 8);
      ctx.fill();
      ctx.stroke();

      ctx.textAlign = "left";
      ctx.fillStyle = "#f8fafc";
      ctx.font = "600 10.5px 'Plus Jakarta Sans', sans-serif";
      ctx.fillText(activeNode.title, tx + 10, ty + 18);

      ctx.fillStyle = "#94a3b8";
      ctx.font = "400 9.5px 'Plus Jakarta Sans', sans-serif";
      ctx.fillText(activeNode.subtitle, tx + 10, ty + 33);

      ctx.fillStyle = "#38bdf8";
      ctx.font = "500 9px 'JetBrains Mono', monospace";
      ctx.fillText(`P99: ${activeNode.latency} • ${activeNode.throughput}`, tx + 10, ty + 48);
    }

    animationFrameId = requestAnimationFrame(render);
  }

  render();

  return {
    setChaosState: (state) => {
      chaosState = state;
    },
    destroy: () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resize);
    }
  };
}

if (typeof window !== "undefined") {
  window.initGraphifyDag = initGraphifyDag;
}
