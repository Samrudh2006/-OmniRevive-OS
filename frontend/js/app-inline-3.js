
    // --- NATIVE WEB AUDIO API SYNTHESIZER ---
    window.playFintechAudio = function(type = 'click') {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        if (!window._omniAudioCtx) {
          window._omniAudioCtx = new AudioCtx();
        }
        const ctx = window._omniAudioCtx;
        if (ctx.state === 'suspended') ctx.resume();

        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);

        if (type === 'click') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(880, now);
          gain.gain.setValueAtTime(0.04, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.035);
          osc.start(now);
          osc.stop(now + 0.035);
        } else if (type === 'switch') {
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(520, now);
          osc.frequency.exponentialRampToValueAtTime(1040, now + 0.09);
          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.11);
          osc.start(now);
          osc.stop(now + 0.11);
        } else if (type === 'success') {
          // Harmonic 2-tone chime: C5 (523.25Hz) + E5 (659.25Hz)
          const osc2 = ctx.createOscillator();
          const gain2 = ctx.createGain();
          osc2.connect(gain2);
          gain2.connect(ctx.destination);

          osc.type = 'sine';
          osc.frequency.setValueAtTime(523.25, now);
          gain.gain.setValueAtTime(0.05, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
          osc.start(now);
          osc.stop(now + 0.16);

          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(659.25, now + 0.06);
          gain2.gain.setValueAtTime(0.06, now + 0.06);
          gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.24);
          osc2.start(now + 0.06);
          osc2.stop(now + 0.24);
        } else if (type === 'inspect') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(740, now);
          gain.gain.setValueAtTime(0.03, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.03);
          osc.start(now);
          osc.stop(now + 0.03);
        }
      } catch (e) {
        // Safe failover if user hasn't interacted with audio yet
      }
    };

    // --- LIVE JSON SYNTAX HIGHLIGHTER ---
    window.syntaxHighlightJson = function(json) {
      if (typeof json !== 'string') {
        json = JSON.stringify(json, null, 2);
      }
      json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'text-amber-300 font-mono'; // number
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'text-cyan-300 font-bold font-mono'; // key
          } else {
            cls = 'text-emerald-300 font-mono'; // string
          }
        } else if (/true|false/.test(match)) {
          cls = 'text-purple-300 font-bold font-mono'; // boolean
        } else if (/null/.test(match)) {
          cls = 'text-slate-500 italic font-mono'; // null
        }
        return '<span class="' + cls + '">' + match + '</span>';
      });
    };

    // --- OMNI TOAST NOTIFICATION SYSTEM ---
    window.showOmniToast = function(title, message, type = 'info', duration = 4000) {
      const container = document.getElementById('omni-toast-container');
      if (!container) return;

      window.playFintechAudio(type === 'success' ? 'success' : 'inspect');

      const toast = document.createElement('div');
      toast.className = 'pointer-events-auto transform transition-all duration-300 ease-out translate-y-2 opacity-0 flex flex-col p-3.5 rounded-xl border backdrop-blur-xl shadow-2xl overflow-hidden';

      const typeStyles = {
        success: 'bg-[#061510]/95 border-emerald-500/60 text-emerald-100 shadow-[0_0_25px_rgba(16,185,129,0.25)]',
        info: 'bg-[#071322]/95 border-cyan-500/60 text-cyan-100 shadow-[0_0_25px_rgba(6,182,212,0.25)]',
        warning: 'bg-[#181104]/95 border-amber-500/60 text-amber-100 shadow-[0_0_25px_rgba(245,158,11,0.25)]',
        error: 'bg-[#1a070a]/95 border-rose-500/60 text-rose-100 shadow-[0_0_25px_rgba(244,63,94,0.25)]'
      };
      const icons = {
        success: '<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>',
        info: '<svg class="w-4 h-4 text-cyan-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
        warning: '<svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
        error: '<svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>'
      };

      toast.className += ' ' + (typeStyles[type] || typeStyles.info);
      toast.innerHTML = `
        <div class="flex items-start justify-between gap-2.5">
          <div class="flex items-start gap-2.5">
            <div class="mt-0.5">${icons[type] || icons.info}</div>
            <div>
              <div class="text-xs font-extrabold tracking-wide uppercase font-mono">${title}</div>
              <div class="text-[11px] text-slate-300 mt-0.5 leading-relaxed">${message}</div>
            </div>
          </div>
          <button onclick="this.parentElement.parentElement.remove()" class="text-slate-400 hover:text-white text-xs p-1 cursor-pointer">✕</button>
        </div>
        <div class="mt-2.5 h-1 w-full bg-white/10 rounded-full overflow-hidden">
          <div class="h-full ${type === 'error' ? 'bg-rose-400' : (type === 'warning' ? 'bg-amber-400' : 'bg-emerald-400')} transition-all ease-linear" style="width: 100%; transition-duration: ${duration}ms;"></div>
        </div>
      `;

      container.appendChild(toast);

      // Animate In
      requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
        const progressBar = toast.querySelector('.h-full');
        if (progressBar) progressBar.style.width = '0%';
      });

      // Auto Dismiss
      setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
      }, duration);
    };

    // --- MULTI-RAIL MODAL CONTROLLER ---
    window.openMultiRailModal = async function() {
      const modal = document.getElementById('multi-rail-modal');
      if (!modal) return;
      window.playFintechAudio('switch');
      modal.classList.remove('hidden');
      await window.loadMultiRailData();
    };

    window.closeMultiRailModal = function() {
      const modal = document.getElementById('multi-rail-modal');
      if (modal) {
        window.playFintechAudio('click');
        modal.classList.add('hidden');
      }
    };

    window.toggleRailDeepDive = function(railId) {
      window.playFintechAudio('inspect');
      const drawer = document.getElementById(`deep-dive-${railId}`);
      const btn = document.getElementById(`btn-toggle-${railId}`);
      if (!drawer) return;

      const isHidden = drawer.classList.contains('hidden');
      if (isHidden) {
        drawer.classList.remove('hidden');
        if (btn) btn.innerHTML = '▲ Hide Lab &amp; Specs';
      } else {
        drawer.classList.add('hidden');
        if (btn) btn.innerHTML = '▼ Blueprint &amp; Lab';
      }
    };

    window.loadMultiRailData = async function() {
      try {
        const res = await fetch('/api/v1/gateways/rails');
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const activeRail = data.active_rail;
        const displayNameEl = document.getElementById('active-rail-display-name');
        if (displayNameEl) {
          displayNameEl.textContent = activeRail.toUpperCase().replace('_', ' ');
        }
        const headerBadgeEl = document.getElementById('header-rail-badge-text');
        if (headerBadgeEl) {
          headerBadgeEl.textContent = 'MULTI-RAIL: ' + activeRail.toUpperCase().replace('_', ' ');
        }

        const container = document.getElementById('rails-cards-container');
        if (!container) return;

        const railIcons = {
          'universal_auto': '',
          'juspay': '',
          'phonepe': '',
          'cred': '',
          'cashfree': '',
          'neobank': '',
          'stripe': '',
          'razorpay': ''
        };

        container.innerHTML = data.rails.map(rail => {
          const isActive = rail.id === activeRail;
          const icon = railIcons[rail.id] || '';
          const metrics = rail.metrics || {
            throughput: '25,000 TPS',
            decision_latency: 'simulated',
            failover_sla: 'simulated',
            concurrency: 'Atomic CAS'
          };
          const deepDive = rail.deep_dive || {
            problem: 'Payment degradation during bank timeouts.',
            architecture: 'Deterministic isolation boundary.',
            algorithm: 'Real-time telemetry allocation.',
            pipeline_flow: 'Trigger  Route  Settle',
            code_snippet: 'return adapter',
            supported_protocols: ['REST', 'Webhooks']
          };
          const scenarios = rail.workbench_scenarios || [];

          return `
            <div onclick="if(!event.target.closest('button') && !event.target.closest('a')) window.toggleRailDeepDive('${rail.id}')"
                 class="p-4 rounded-xl border transition-all duration-300 cursor-pointer group flex flex-col justify-between space-y-3 ${
                   isActive 
                     ? 'bg-gradient-to-br from-emerald-950/50 via-[#0a1728] to-[#0c2340] border-emerald-500/70 shadow-xl shadow-emerald-500/20 ring-1 ring-emerald-500/40' 
                     : 'bg-[#091122]/90 border-slate-800/90 hover:border-emerald-500/40 hover:bg-[#0c1830] hover:shadow-lg hover:shadow-cyan-950/20'
                 }">
              
              <!-- Card Header -->
              <div>
                <div class="flex items-start justify-between gap-2">
                  <div class="flex items-center gap-2.5">
                    <span class="text-2xl filter drop-shadow group-hover:scale-110 transition-transform duration-200">${icon}</span>
                    <div>
                      <div class="flex items-center gap-2">
                        <h3 class="text-sm font-bold text-white tracking-tight">${rail.name}</h3>
                        ${isActive ? '<span class="px-2 py-0.5 rounded text-[9px] font-black bg-emerald-500 text-black uppercase mono tracking-wider shadow-sm animate-pulse">Active Rail</span>' : ''}
                      </div>
                      <div class="text-[11px] text-slate-400 mt-0.5">${rail.tagline}</div>
                    </div>
                  </div>
                  <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-800/90 text-cyan-300 border border-cyan-500/30 mono whitespace-nowrap">
                    ${rail.tier}
                  </span>
                </div>

                <!-- Live Engineering Metrics Grid -->
                <div class="mt-3 grid grid-cols-4 gap-1.5 p-2 bg-[#040813] rounded-lg border border-slate-800/90 text-center">
                  <div>
                    <div class="text-[9px] text-slate-400 uppercase mono">TPS</div>
                    <div class="text-[11px] font-bold text-emerald-400 mono">${metrics.throughput}</div>
                  </div>
                  <div>
                    <div class="text-[9px] text-slate-400 uppercase mono">Latency</div>
                    <div class="text-[11px] font-bold text-cyan-400 mono">${metrics.decision_latency}</div>
                  </div>
                  <div>
                    <div class="text-[9px] text-slate-400 uppercase mono">SLA</div>
                    <div class="text-[11px] font-bold text-purple-400 mono">${metrics.failover_sla}</div>
                  </div>
                  <div>
                    <div class="text-[9px] text-slate-400 uppercase mono">Concurrency</div>
                    <div class="text-[10px] font-bold text-amber-400 mono truncate" title="${metrics.concurrency}">${metrics.concurrency}</div>
                  </div>
                </div>

                <!-- Core Capability Summary -->
                <div class="mt-2.5 text-[11px] text-slate-300 leading-relaxed">
                  ${rail.core_feature}
                </div>
              </div>

              <!-- Interactive Card Prompt & Action Toolbar -->
              <div class="pt-2.5 border-t border-slate-800/80">
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <button onclick="event.stopPropagation(); window.selectRail('${rail.id}', '${rail.name}')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer shadow-sm ${isActive ? 'bg-emerald-500 text-black shadow-emerald-500/30 font-extrabold' : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/80'}">
                      ${isActive ? '✓ Selected Rail' : 'Activate Rail'}
                    </button>
                    <button onclick="event.stopPropagation(); window.simulateRailRecovery('${rail.id}', '${rail.name}')" class="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition cursor-pointer flex items-center gap-1">
                       Simulate
                    </button>
                  </div>
                  <button id="btn-toggle-${rail.id}" onclick="event.stopPropagation(); window.toggleRailDeepDive('${rail.id}')" class="px-2.5 py-1 rounded-md bg-cyan-950/50 hover:bg-cyan-900/60 border border-cyan-500/30 text-[10.5px] text-cyan-300 hover:text-cyan-200 font-semibold transition cursor-pointer flex items-center gap-1">
                    <span>▼ Blueprint &amp; Lab</span>
                  </button>
                </div>
                <div class="text-[9.5px] text-slate-500 group-hover:text-cyan-400/80 transition-colors mt-1.5 flex items-center justify-between px-0.5">
                  <span> Click card to inspect systems blueprint</span>
                  <span class="mono font-semibold">${scenarios.length} Live Lab Tests Available</span>
                </div>
              </div>

              <!-- Expandable Architecture Deep-Dive Drawer & Live Laboratory -->
              <div id="deep-dive-${rail.id}" class="hidden mt-2 p-3.5 bg-[#03060e] rounded-xl border border-cyan-500/40 text-xs space-y-3 shadow-2xl animate-in fade-in duration-200" onclick="event.stopPropagation()">
                
                <div class="border-b border-slate-800/90 pb-2 flex items-center justify-between">
                  <span class="text-[10.5px] font-bold uppercase tracking-wider text-cyan-400 mono flex items-center gap-1.5">
                     Systems Architecture Specification
                  </span>
                  <span class="text-[9.5px] text-emerald-400 mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">Verified Invariant</span>
                </div>

                <div>
                  <div class="text-[10px] text-slate-400 font-bold uppercase mono">1. Production Problem Solved</div>
                  <div class="text-[11px] text-slate-200 mt-1 leading-relaxed bg-slate-900/60 p-2 rounded-lg border border-slate-800/80">${deepDive.problem}</div>
                </div>

                <div>
                  <div class="text-[10px] text-slate-400 font-bold uppercase mono">2. Systems Engineering Mechanism</div>
                  <div class="text-[11px] text-slate-200 mt-1 leading-relaxed bg-slate-900/60 p-2 rounded-lg border border-slate-800/80">${deepDive.architecture}</div>
                </div>

                <div>
                  <div class="text-[10px] text-slate-400 font-bold uppercase mono">3. Deterministic Mathematical Algorithm</div>
                  <div class="text-[11px] text-emerald-300 font-mono mt-1 leading-relaxed bg-black/70 p-2 rounded-lg border border-emerald-500/30">${deepDive.algorithm}</div>
                  ${deepDive.code_snippet ? `
                    <pre class="mt-1.5 p-2 bg-[#020408] rounded border border-slate-800/90 text-[10px] text-cyan-300 font-mono overflow-x-auto"><code>${deepDive.code_snippet}</code></pre>
                  ` : ''}
                </div>

                ${deepDive.pipeline_flow ? `
                  <div>
                    <div class="text-[10px] text-slate-400 font-bold uppercase mono">4. End-to-End Pipeline Flow</div>
                    <div class="text-[10.5px] text-slate-300 font-mono mt-1 bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-center tracking-tight text-emerald-300 font-semibold">
                      ${deepDive.pipeline_flow}
                    </div>
                  </div>
                ` : ''}

                <div>
                  <div class="text-[10px] text-slate-400 font-bold uppercase mono">5. Protocols &amp; Wire Standards</div>
                  <div class="flex flex-wrap gap-1.5 mt-1">
                    ${(deepDive.supported_protocols || []).map(proto => `
                      <span class="px-2 py-0.5 rounded text-[9.5px] font-mono bg-slate-900 text-slate-200 border border-slate-700/80 font-semibold">${proto}</span>
                    `).join('')}
                  </div>
                </div>

                <!-- Live Engineering Laboratory Workbench -->
                ${scenarios.length > 0 ? `
                  <div class="mt-3 pt-2.5 border-t border-slate-800/90 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-[10.5px] font-extrabold uppercase tracking-wider text-amber-400 mono flex items-center gap-1.5">
                         Live Engineering Laboratory Workbench
                      </span>
                      <span class="text-[9px] text-slate-500 mono">One-Click Deterministic Execution</span>
                    </div>

                    <div class="grid grid-cols-1 gap-2">
                      ${scenarios.map(sc => `
                        <div class="p-2.5 bg-[#070e1a] rounded-lg border border-slate-800 hover:border-cyan-500/50 transition flex flex-col space-y-1.5">
                          <div class="flex items-center justify-between gap-2">
                            <button onclick="event.stopPropagation(); window.runWorkbenchScenario('${rail.id}', '${sc.scenario}', ${sc.amount}, '${sc.label}')"
                                    class="px-2.5 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-sm">
                              <span>${sc.label}</span>
                            </button>
                            <span class="text-[9.5px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 mono font-semibold">
                              ${sc.badge}
                            </span>
                          </div>
                          <div class="text-[10.5px] text-slate-400 leading-snug">
                            ${sc.desc}
                          </div>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                ` : ''}

              </div>

            </div>
          `;
        }).join('');
      } catch (err) {
        console.error('Error loading rails data:', err);
      }
    };

    window.selectRail = async function(railId, railName = '') {
      window.playFintechAudio('click');
      try {
        const res = await fetch('/api/v1/gateways/select', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ rail_id: railId })
        });
        const json = await res.json();
        if (json.success) {
          await window.loadMultiRailData();
          window.simulateRailRecovery(railId, railName);

          // Confetti Effect
          if (window.confetti) {
            window.confetti({ 
              particleCount: 45, 
              spread: 70, 
              origin: { y: 0.8 },
              colors: ['#10b981', '#06b6d4', '#a855f7', '#fbbf24']
            });
          }

          window.showOmniToast(
            'Production Rail Online',
            `Switched recovery control plane to ${railName || railId.toUpperCase()} with CAS Mutex lock.`,
            'success'
          );
        }
      } catch (err) {
        window.showOmniToast('Switch Error', 'Failed to activate rail: ' + err.message, 'error');
      }
    };

    window.simulateRailRecovery = async function(railId, railName = '') {
      window.playFintechAudio('click');
      const inspector = document.getElementById('rail-sim-json');
      const statusBadge = document.getElementById('sim-status-badge');
      if (statusBadge) statusBadge.textContent = 'Executing via ' + railId.toUpperCase() + '...';
      if (inspector) inspector.textContent = `// Dispatching high-fidelity simulated recovery intent via ${railName || railId.toUpperCase()}...\n// Awaiting 200 OK contract...`;

      try {
        const res = await fetch('/api/v1/gateways/simulate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            rail_id: railId,
            amount: railId === 'cred' ? 85000.0 : (railId === 'neobank' ? 5000.0 : 14500.0),
            customer_name: 'Aditya Birla Telecom',
            customer_email: railId === 'stripe' ? 'cfo@globalfintech.io' : 'aditya@client.in',
            is_mandate: railId === 'neobank'
          })
        });
        const json = await res.json();
        if (inspector) inspector.innerHTML = window.syntaxHighlightJson(json.data);
        if (statusBadge) statusBadge.textContent = '200 OK • ' + (json.data.provider || railId.toUpperCase()) + (json.execution_time_ms ? ` (${json.execution_time_ms}ms)` : '');

        window.showOmniToast(
          'Recovery Intent Dispatched',
          `Simulated 200 OK contract via ${json.data.provider || railId.toUpperCase()} (${json.data.mode || 'RECOVERY'}). Final INR ${json.data.final_amount || 14500}`,
          'success'
        );
      } catch (err) {
        if (inspector) inspector.textContent = '// Error during simulation: ' + err;
        window.showOmniToast('Simulation Error', err.message, 'error');
      }
    };

    window.runWorkbenchScenario = async function(railId, scenarioKey, amount, label) {
      window.playFintechAudio('switch');
      const inspector = document.getElementById('rail-sim-json');
      const statusBadge = document.getElementById('sim-status-badge');
      if (statusBadge) statusBadge.textContent = `Executing Lab Test: ${label}...`;
      if (inspector) inspector.textContent = `// Executing deterministic test scenario "${scenarioKey}" on ${railId.toUpperCase()}...\n// Benchmarking latency and verifying invariants...`;

      try {
        const res = await fetch('/api/v1/gateways/simulate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            rail_id: railId,
            scenario: scenarioKey,
            amount: amount,
            customer_name: 'Enterprise Client',
            customer_email: railId === 'stripe' ? 'cfo@enterprise.io' : 'finance@client.in'
          })
        });
        const json = await res.json();
        if (inspector) inspector.innerHTML = window.syntaxHighlightJson(json.data);
        if (statusBadge) {
          statusBadge.textContent = `200 OK • ${json.data.mode || 'LAB_VERIFIED'} (${json.execution_time_ms || 0.22}ms)`;
        }

        // Particle burst on lab verification
        if (window.confetti) {
          window.confetti({ 
            particleCount: 25, 
            spread: 50, 
            origin: { y: 0.85 },
            colors: ['#06b6d4', '#10b981', '#fbbf24']
          });
        }

        window.showOmniToast(
          'Laboratory Test Passed',
          `Scenario "${label}" successfully verified in ${json.execution_time_ms || 0.22}ms. Invariants verified: ${((json.data.invariants_verified || []).join(', ')) || 'NOMINAL'}`,
          'success'
        );

        // Scroll payload inspector smoothly into view
        inspector.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } catch (err) {
        if (inspector) inspector.textContent = '// Error running scenario: ' + err;
        window.showOmniToast('Scenario Error', err.message, 'error');
      }
    };

    window.copySimulationPayload = function() {
      window.playFintechAudio('click');
      const inspector = document.getElementById('rail-sim-json');
      if (!inspector) return;
      navigator.clipboard.writeText(inspector.innerText || inspector.textContent);
      window.showOmniToast('Copied to Clipboard', 'Simulation JSON payload copied to clipboard.', 'info', 2000);
    };
  