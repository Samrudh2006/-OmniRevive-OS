/**
 * RazorRevive-OS Weibull Hazard Curve & Analytics Component
 * Consolidates Weibull PDF canvas plotting with parametric hazard sliders (k, lambda, age)
 * and overview SVG curve bank presets.
 */

export function renderWeibullSvgCurve() {
  const bank = document.getElementById("weibull-bank-select")?.value || "HDFC";
  const pathEl = document.getElementById("weibull-path");
  const peakPt = document.getElementById("weibull-peak-pt");
  const optimalLabel = document.getElementById("weibull-optimal-label");

  if (!pathEl || !peakPt) return;

  if (bank === "HDFC") {
    pathEl.setAttribute("d", "M 0 110 Q 120 10 220 30 T 500 80");
    peakPt.setAttribute("cx", "180");
    peakPt.setAttribute("cy", "20");
    if (optimalLabel) optimalLabel.innerText = "★ Optimal: +45m (91.4% Recovery)";
  } else if (bank === "SBI") {
    pathEl.setAttribute("d", "M 0 110 Q 180 20 280 40 T 500 90");
    peakPt.setAttribute("cx", "250");
    peakPt.setAttribute("cy", "28");
    if (optimalLabel) optimalLabel.innerText = "★ Optimal: +60m (84.2% Recovery)";
  } else if (bank === "ICICI") {
    pathEl.setAttribute("d", "M 0 110 Q 80 8 160 22 T 500 75");
    peakPt.setAttribute("cx", "125");
    peakPt.setAttribute("cy", "14");
    if (optimalLabel) optimalLabel.innerText = "★ Optimal: +30m (93.1% Recovery)";
  } else if (bank === "AXIS") {
    pathEl.setAttribute("d", "M 0 110 Q 130 15 230 35 T 500 85");
    peakPt.setAttribute("cx", "180");
    peakPt.setAttribute("cy", "24");
    if (optimalLabel) optimalLabel.innerText = "★ Optimal: +45m (87.5% Recovery)";
  }
}

export function renderWeibullCanvasChart() {
  const kInput = document.getElementById("weibull-k");
  const lambdaInput = document.getElementById("weibull-lambda");
  const ageInput = document.getElementById("weibull-age");
  const canvas = document.getElementById("weibullCanvas");
  if (!kInput || !lambdaInput || !canvas) return;

  const k = parseFloat(kInput.value);
  const lambda = parseFloat(lambdaInput.value);
  const age = ageInput ? parseFloat(ageInput.value) : 15.0;

  const kValEl = document.getElementById("weibull-k-val");
  const lambdaValEl = document.getElementById("weibull-lambda-val");
  const ageValEl = document.getElementById("weibull-age-val");
  const targetEl = document.getElementById("weibull-optimal-target");
  const yieldEl = document.getElementById("weibull-yield-pct");

  if (kValEl) kValEl.textContent = k.toFixed(2);
  if (lambdaValEl) lambdaValEl.textContent = `${lambda.toFixed(0)}m`;
  if (ageValEl) ageValEl.textContent = `${age.toFixed(0)}m`;

  // Mode / Peak calculation: lambda * ((k - 1) / k)^(1 / k)
  let optimalDelta = k > 1 ? lambda * Math.pow((k - 1) / k, 1 / k) : lambda * 0.35;
  optimalDelta = Math.max(5, Math.round(optimalDelta));

  if (targetEl) targetEl.textContent = `+${optimalDelta} mins (Optimal Window)`;
  if (yieldEl) yieldEl.textContent = `${Math.min(94.5, 75 + k * 6.5).toFixed(1)}%`;

  // Canvas Rendering
  const ctx = canvas.getContext("2d");
  const w = canvas.parentElement.clientWidth || 400;
  const h = canvas.parentElement.clientHeight || 200;
  canvas.width = w;
  canvas.height = h;

  ctx.clearRect(0, 0, w, h);

  const isLight = document.documentElement.classList.contains("light");

  // Grid Lines
  ctx.strokeStyle = isLight ? "#e2e8f0" : "#142442";
  ctx.lineWidth = 1;
  for (let x = 40; x < w; x += 60) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h - 25);
    ctx.stroke();
  }
  for (let y = 20; y < h - 25; y += 35) {
    ctx.beginPath();
    ctx.moveTo(40, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Compute Weibull PDF: f(t) = (k/lambda) * (t/lambda)^(k-1) * exp(-(t/lambda)^k)
  const maxTime = lambda * 2.8;
  const points = [];
  let maxPdf = 0;

  for (let t = 0.5; t <= maxTime; t += maxTime / 100) {
    const z = t / lambda;
    const pdf = (k / lambda) * Math.pow(z, k - 1) * Math.exp(-Math.pow(z, k));
    if (pdf > maxPdf) maxPdf = pdf;
    points.push({ t, pdf });
  }

  if (maxPdf === 0) maxPdf = 0.01;

  // Draw Gradient Fill
  const grad = ctx.createLinearGradient(0, 0, 0, h - 25);
  if (isLight) {
    grad.addColorStop(0, "rgba(2, 132, 199, 0.25)");
    grad.addColorStop(1, "rgba(2, 132, 199, 0.01)");
  } else {
    grad.addColorStop(0, "rgba(56, 189, 248, 0.4)");
    grad.addColorStop(1, "rgba(56, 189, 248, 0.02)");
  }

  ctx.beginPath();
  ctx.moveTo(40, h - 25);
  points.forEach((pt, idx) => {
    const px = 40 + (pt.t / maxTime) * (w - 60);
    const py = h - 25 - (pt.pdf / maxPdf) * (h - 60);
    if (idx === 0) ctx.lineTo(px, py);
    else ctx.lineTo(px, py);
  });
  ctx.lineTo(w - 20, h - 25);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Draw Curve Stroke
  ctx.beginPath();
  points.forEach((pt, idx) => {
    const px = 40 + (pt.t / maxTime) * (w - 60);
    const py = h - 25 - (pt.pdf / maxPdf) * (h - 60);
    if (idx === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  });
  ctx.strokeStyle = isLight ? "#0284c7" : "#38bdf8";
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Mark Optimal Peak Point
  const peakX = 40 + (optimalDelta / maxTime) * (w - 60);
  ctx.beginPath();
  ctx.setLineDash([4, 4]);
  ctx.moveTo(peakX, 10);
  ctx.lineTo(peakX, h - 25);
  ctx.strokeStyle = isLight ? "#059669" : "#10b981";
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.beginPath();
  ctx.arc(peakX, 20, 5, 0, Math.PI * 2);
  ctx.fillStyle = isLight ? "#047857" : "#10b981";
  ctx.fill();

  // Axis Labels
  ctx.fillStyle = isLight ? "#475569" : "#94a3b8";
  ctx.font = "bold 10px Inter, monospace";
  ctx.fillText("0m", 35, h - 10);
  ctx.fillText(`+${Math.round(lambda)}m`, 40 + (lambda / maxTime) * (w - 60) - 10, h - 10);
  ctx.fillText(`+${Math.round(maxTime)}m`, w - 40, h - 10);
  ctx.fillText(`Peak Target (+${optimalDelta}m)`, peakX - 35, 12);
}

/**
 * Canonical unified renderWeibullCurve function
 * Safely updates both SVG and Canvas representations if they exist in DOM.
 */
export function renderWeibullCurve() {
  if (document.getElementById("weibull-path")) {
    renderWeibullSvgCurve();
  }
  if (document.getElementById("weibullCanvas")) {
    renderWeibullCanvasChart();
  }
}
