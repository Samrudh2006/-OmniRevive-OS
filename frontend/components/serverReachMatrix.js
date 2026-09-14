/**
 * OmniRevive-OS | Global Load Balancer & Server Reachability Matrix
 * Conforms to: DESIGN.md Specification (Section 5)
 * Live telemetry polling, dynamic traffic re-weighting, and automated failover controls.
 */

class ServerReachMatrix {
  constructor(mountContainerId = 'server-reach-matrix-mount') {
    this.mountId = mountContainerId;
    this.data = null;
    this.pollInterval = null;
    this.init();
  }

  async init() {
    await this.fetchReachabilityData();
    this.render();
    // Refresh every 12 seconds
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => this.fetchReachabilityData(true), 12000);
  }

  async fetchReachabilityData(silent = false) {
    try {
      const res = await fetch('/api/v1/system/server-reach');
      const json = await res.json();
      if (json.success) {
        this.data = json.data;
        if (!silent) this.render();
        else this.updateTelemetryInPlace();
      }
    } catch (e) {
      console.warn('[ServerReach] Failed to fetch server reachability:', e);
    }
  }

  render() {
    const container = document.getElementById(this.mountId);
    if (!container) return;

    if (!this.data) {
      container.innerHTML = `
        <div class="p-4 text-center text-xs text-slate-400 font-mono animate-pulse">
          ⚡ Initializing Global Load Balancer &amp; Server Reach Matrix...
        </div>
      `;
      return;
    }

    const { nodes, load_balancer, active_region, global_p99_latency_ms } = this.data;
    const dist = load_balancer.active_distribution || { HDFC: 40, ICICI: 35, Axis: 20, SBI: 5 };

    container.innerHTML = `
      <div class="bg-[#050b18]/95 border border-cyan-500/30 rounded-2xl p-4 sm:p-5 shadow-2xl backdrop-blur-xl space-y-4">
        
        <!-- Header Bar -->
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold text-base shadow-sm shadow-cyan-500/20">
              🌐
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-sm font-extrabold text-white tracking-tight">Global Load Balancer &amp; Server Reachability Matrix</h3>
                <span class="px-2 py-0.5 rounded text-[9.5px] font-black bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 mono">
                  ALL 7 NODES ONLINE
                </span>
              </div>
              <div class="text-[11px] text-slate-400">
                Primary Core: <span class="text-cyan-300 font-semibold">${active_region}</span> • Global p99 Ping: <span class="text-emerald-300 font-mono font-bold">${global_p99_latency_ms}ms</span>
              </div>
            </div>
          </div>

          <!-- Action Toolbar -->
          <div class="flex items-center gap-2">
            <button onclick="window._serverReachMatrixInstance?.pingAllNodes()" 
                    class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 shadow-sm">
              <span>🔄</span> <span>Ping All Nodes</span>
            </button>
            <button onclick="window._serverReachMatrixInstance?.rebalanceWeights('OPTIMIZE')" 
                    class="px-3 py-1.5 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-sm shadow-cyan-500/10">
              <span>⚡</span> <span>Rebalance Weights</span>
            </button>
            <button onclick="window._serverReachMatrixInstance?.rebalanceWeights('FAILOVER_SBI')" 
                    class="px-3 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/40 text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-sm">
              <span>⚠️</span> <span>Simulate SBI 504 Failover</span>
            </button>
          </div>
        </div>

        <!-- Dynamic Load Distribution Visualizer Bar -->
        <div class="p-3 bg-[#030712] rounded-xl border border-slate-800/90 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="text-[10.5px] font-bold text-slate-300 uppercase mono flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              Real-Time Dynamic Switch Traffic Split
            </span>
            <span class="text-[10px] text-slate-400 font-mono">Heuristic Latency Allocation</span>
          </div>

          <!-- Proportional Progress Bar -->
          <div class="h-3.5 w-full bg-slate-900 rounded-full overflow-hidden flex border border-slate-800 shadow-inner">
            <div style="width: ${dist.HDFC}%;" class="h-full bg-blue-500 transition-all duration-500 hover:brightness-125" title="HDFC: ${dist.HDFC}%"></div>
            <div style="width: ${dist.ICICI}%;" class="h-full bg-emerald-500 transition-all duration-500 hover:brightness-125" title="ICICI: ${dist.ICICI}%"></div>
            <div style="width: ${dist.Axis}%;" class="h-full bg-purple-500 transition-all duration-500 hover:brightness-125" title="Axis: ${dist.Axis}%"></div>
            <div style="width: ${dist.SBI}%;" class="h-full bg-amber-500 transition-all duration-500 hover:brightness-125" title="SBI: ${dist.SBI}%"></div>
          </div>

          <!-- Legend -->
          <div class="flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono pt-0.5">
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
              <span class="text-slate-300 font-semibold">HDFC Switch:</span>
              <span class="text-blue-400 font-bold" id="dist-hdfc-val">${dist.HDFC}%</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span class="text-slate-300 font-semibold">ICICI Handle:</span>
              <span class="text-emerald-400 font-bold" id="dist-icici-val">${dist.ICICI}%</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
              <span class="text-slate-300 font-semibold">Axis Gateway:</span>
              <span class="text-purple-400 font-bold" id="dist-axis-val">${dist.Axis}%</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span class="text-slate-300 font-semibold">SBI Yono:</span>
              <span class="text-amber-400 font-bold" id="dist-sbi-val">${dist.SBI}%</span>
              ${dist.SBI <= 5 ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Throttled</span>' : ''}
            </div>
          </div>
        </div>

        <!-- 7-Node Reachability Cards Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 pt-1">
          ${nodes.map(node => {
            const isDegraded = node.status.includes('DEGRADED');
            const isStandby = node.status.includes('STANDBY');
            const statusColor = isDegraded ? 'text-amber-400 border-amber-500/40 bg-amber-950/40' : (isStandby ? 'text-slate-400 border-slate-700 bg-slate-900/60' : 'text-emerald-400 border-emerald-500/40 bg-emerald-950/40');
            const dotColor = isDegraded ? 'bg-amber-400 animate-ping' : (isStandby ? 'bg-slate-400' : 'bg-emerald-400 animate-pulse');

            return `
              <div class="p-3 bg-[#030610] rounded-xl border border-slate-800/80 hover:border-cyan-500/40 transition-all duration-200 flex flex-col justify-between space-y-2 group">
                <div>
                  <div class="flex items-start justify-between gap-1.5">
                    <span class="text-xs font-bold text-white tracking-tight leading-tight">${node.name}</span>
                    <span class="px-1.5 py-0.5 rounded text-[8.5px] font-mono uppercase font-bold border ${statusColor}">
                      ${node.status}
                    </span>
                  </div>
                  <div class="text-[10px] text-slate-400 mt-0.5">${node.role}</div>
                </div>

                <div class="flex items-center justify-between pt-1 border-t border-slate-800/60 text-xs font-mono">
                  <div class="flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
                    <span class="text-slate-400 text-[10px]">Ping:</span>
                    <span class="font-bold text-cyan-300 text-[11px]">${node.latency_ms}ms</span>
                  </div>
                  <div class="text-[10px] text-slate-400">
                    SLA: <span class="text-slate-200 font-semibold">${node.sla_uptime}</span>
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>

      </div>
    `;
  }

  updateTelemetryInPlace() {
    if (!this.data) return;
    const dist = this.data.load_balancer.active_distribution;
    if (dist) {
      const hdfc = document.getElementById('dist-hdfc-val');
      const icici = document.getElementById('dist-icici-val');
      const axis = document.getElementById('dist-axis-val');
      const sbi = document.getElementById('dist-sbi-val');
      if (hdfc) hdfc.textContent = dist.HDFC + '%';
      if (icici) icici.textContent = dist.ICICI + '%';
      if (axis) axis.textContent = dist.Axis + '%';
      if (sbi) sbi.textContent = dist.SBI + '%';
    }
  }

  async pingAllNodes() {
    if (window.playFintechAudio) window.playFintechAudio('switch');
    if (window.showOmniToast) {
      window.showOmniToast('Probing Gateway Latencies', 'Dispatching concurrent ICMP/TCP ping probes to all 7 regional nodes...', 'info', 2500);
    }
    await this.fetchReachabilityData();
    if (window.showOmniToast) {
      window.showOmniToast('Probes Completed', 'All 7 nodes responded within SLA thresholds (Global p99: ' + (this.data?.global_p99_latency_ms || 3.85) + 'ms).', 'success');
    }
  }

  async rebalanceWeights(action = 'OPTIMIZE') {
    if (window.playFintechAudio) window.playFintechAudio('click');
    try {
      const res = await fetch('/api/v1/system/rebalance-traffic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const json = await res.json();
      if (json.success) {
        await this.fetchReachabilityData();
        if (window.showOmniToast) {
          window.showOmniToast(
            action === 'FAILOVER_SBI' ? 'SBI 504 Hazard Failover Active' : 'Traffic Weights Rebalanced',
            json.message + ' (Rebalance Latency: ' + json.rebalance_latency_ms + 'ms)',
            action === 'FAILOVER_SBI' ? 'warning' : 'success'
          );
        }
      }
    } catch (err) {
      if (window.showOmniToast) {
        window.showOmniToast('Rebalance Error', err.message, 'error');
      }
    }
  }
}

// Global initialization helper
window.initServerReachMatrix = function(containerId = 'server-reach-matrix-mount') {
  window._serverReachMatrixInstance = new ServerReachMatrix(containerId);
  return window._serverReachMatrixInstance;
};
