/**
 * RazorRevive-OS 3D Financial Topology & Gateway Mesh Engine
 * Renders real-time interactive 3D node network of payment switches,
 * card networks, NPCI UPI Hub, and dynamic transaction packet flow.
 */

export function initFintech3DTopology() {
  const canvas = document.getElementById("fintech-topology-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function syncSize() {
    if (!canvas || !canvas.parentElement) return;
    const w = canvas.parentElement.clientWidth;
    const h = canvas.parentElement.clientHeight || 224;
    if (w > 0 && (canvas.width !== w || canvas.height !== h)) {
      canvas.width = w;
      canvas.height = h;
    }
  }
  syncSize();
  window.addEventListener("resize", syncSize);

  let mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.targetX = ((e.clientX - rect.left) / canvas.width - 0.5) * 2;
    mouse.targetY = ((e.clientY - rect.top) / canvas.height - 0.5) * 2;
  });

  const nodes = [
    { name: "Razorpay Core", x: 0, y: 0, z: 0, color: "#38bdf8", size: 9, pulse: 0 },
    { name: "HDFC Gateway (504)", x: -140, y: -50, z: 40, color: "#f59e0b", size: 6, pulse: 1 },
    { name: "SBI Switch", x: 130, y: -60, z: -30, color: "#10b981", size: 6, pulse: 2 },
    { name: "ICICI Rail", x: 140, y: 60, z: 50, color: "#06b6d4", size: 6, pulse: 3 },
    { name: "Axis Mandates", x: -120, y: 70, z: -40, color: "#a855f7", size: 6, pulse: 4 },
    { name: "NPCI UPI Hub", x: 0, y: -90, z: 70, color: "#10b981", size: 7, pulse: 0.5 }
  ];

  const packets = [
    { from: 0, to: 1, progress: 0.1, speed: 0.008, color: "#f59e0b" },
    { from: 0, to: 2, progress: 0.5, speed: 0.012, color: "#10b981" },
    { from: 0, to: 3, progress: 0.8, speed: 0.010, color: "#06b6d4" },
    { from: 0, to: 5, progress: 0.3, speed: 0.015, color: "#38bdf8" }
  ];

  let angleY = 0;
  let angleX = 0;

  function render() {
    if (!canvas || !canvas.parentElement || canvas.parentElement.offsetParent === null) {
      requestAnimationFrame(render);
      return;
    }

    syncSize();
    if (canvas.width === 0 || canvas.height === 0) {
      requestAnimationFrame(render);
      return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    angleY += 0.004 + mouse.x * 0.01;
    angleX = mouse.y * 0.4;

    const cosY = Math.cos(angleY),
      sinY = Math.sin(angleY);
    const cosX = Math.cos(angleX),
      sinX = Math.sin(angleX);

    // Project 3D coordinates to 2D screen
    const projected = nodes.map((n) => {
      // Rotate Y
      let x1 = n.x * cosY - n.z * sinY;
      let z1 = n.z * cosY + n.x * sinY;
      // Rotate X
      let y2 = n.y * cosX - z1 * sinX;
      let z2 = z1 * cosX + n.y * sinX;

      const fov = 300;
      const scale = fov / (fov + z2 + 100);
      return {
        name: n.name,
        sx: cx + x1 * scale,
        sy: cy + y2 * scale,
        scale: scale,
        z: z2,
        color: n.color,
        size: n.size * scale,
        pulse: n.pulse
      };
    });

    // Draw Interconnecting 3D Vectors
    for (let i = 1; i < projected.length; i++) {
      const p0 = projected[0];
      const p = projected[i];

      ctx.beginPath();
      ctx.moveTo(p0.sx, p0.sy);
      ctx.lineTo(p.sx, p.sy);
      ctx.strokeStyle = "rgba(56, 189, 248, 0.22)";
      ctx.lineWidth = Math.max(1, p.scale * 1.5);
      ctx.stroke();
    }

    // Draw Cross-Ring Outer Mesh
    ctx.beginPath();
    for (let i = 1; i < projected.length; i++) {
      const next = i === projected.length - 1 ? 1 : i + 1;
      ctx.moveTo(projected[i].sx, projected[i].sy);
      ctx.lineTo(projected[next].sx, projected[next].sy);
    }
    ctx.strokeStyle = "rgba(16, 185, 129, 0.12)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw Flowing Transaction Packets
    packets.forEach((pkt) => {
      pkt.progress += pkt.speed;
      if (pkt.progress > 1) pkt.progress = 0;
      const pFrom = projected[pkt.from];
      const pTo = projected[pkt.to];
      const px = pFrom.sx + (pTo.sx - pFrom.sx) * pkt.progress;
      const py = pFrom.sy + (pTo.sy - pFrom.sy) * pkt.progress;

      ctx.beginPath();
      ctx.arc(px, py, 3 * pFrom.scale, 0, Math.PI * 2);
      ctx.fillStyle = pkt.color;
      ctx.shadowBlur = 8;
      ctx.shadowColor = pkt.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // Draw Nodes sorted by depth
    projected.sort((a, b) => b.z - a.z);
    projected.forEach((p) => {
      p.pulse += 0.05;
      const glow = Math.sin(p.pulse) * 3 + 4;

      // Glowing Outer Halo
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, p.size + glow, 0, Math.PI * 2);
      ctx.fillStyle = p.color + "22";
      ctx.fill();

      // Solid Center Node
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.shadowBlur = 12;
      ctx.shadowColor = p.color;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Node Label
      ctx.font = `${Math.max(9, Math.round(11 * p.scale))}px Inter, sans-serif`;
      ctx.fillStyle = "#e2e8f0";
      ctx.fillText(p.name, p.sx + p.size + 4, p.sy + 3);
    });

    requestAnimationFrame(render);
  }
  render();
}
