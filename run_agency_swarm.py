"""
OmniRevive-OS Continuous Specialized Agency Swarm Runner
=========================================================
Standalone terminal daemon that runs all 300+ specialized agents from msitarzewski/agency-agents
continuously in real-time with SRE Telemetry & Cyberpunk status board.
"""

import os
import sys
import time
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app.agency_swarm import (
    get_agency_swarm_status,
    execute_agency_cycle,
    REGISTERED_AGENTS,
    DIVISION_BREAKDOWN
)

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
========================================================================================
   ____                       ____            _            ____   _____ 
  |  _ \ __ _ _______  _ __  |  _ \ _____   _(_)_   _____ / __ \ / ____|
  | |_) / _` |_  / _ \| '__| | |_) / _ \ \ / / \ \ / / _ \ |  | | (___  
  |  _ < (_| |/ / (_) | |    |  _ <  __/\ V /| |\ V /  __/ |  | |\___ \ 
  |_| \_\__,_/___\___/|_|    |_| \_\___| \_/ |_| \_/ \___| \____/|_____/ 
          CONTINUOUS SPECIALIZED AGENCY AGENTS SWARM DAEMON v2.0
========================================================================================{RESET}
{DIM}[SOURCE] msitarzewski/agency-agents  |  [AGENTS] {len(REGISTERED_AGENTS)}  |  [DIVISIONS] {len(DIVISION_BREAKDOWN)}{RESET}
"""

def main():
    print(BANNER)
    print(f"{GREEN}{BOLD}>>> Launching Continuous 300+ Specialized Agency Swarm Daemon...{RESET}\n")

    print(f"{YELLOW}{BOLD}[DIVISION BREAKDOWN]{RESET}")
    for div, ag_list in DIVISION_BREAKDOWN.items():
        icon = ag_list[0].get("emoji", "🤖") if ag_list else "🤖"
        print(f"  {DIM}•{RESET} {icon} {BOLD}{div.upper():<20}{RESET}: {GREEN}{len(ag_list):>3d} Specialized Agents{RESET}")
    print("\n" + f"{DIM}" + "="*88 + f"{RESET}\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            result = execute_agency_cycle()
            status = get_agency_swarm_status()

            print(f"{CYAN}⚡ [AGENCY CYCLE #{cycle:04d}]{RESET} | Active Agents: {GREEN}{status['active_agents']}/{status['total_agents']}{RESET} | Total Evals: {BOLD}{status['total_evaluations']:,}{RESET} | Status: {GREEN}HEALTHY{RESET}")
            
            # Print recent agent events
            if status.get("recent_agent_events"):
                latest = status["recent_agent_events"][0]
                emoji = latest.get("emoji", "🤖")
                print(f"   {DIM}• Last Executed:{RESET} {emoji} {BOLD}{latest['agent_name']}{RESET} [{latest['division']}] -> {GREEN}{latest['status']}{RESET}")

            time.sleep(1.5)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}🛑 Stopping Agency Swarm Daemon. Exiting safely.{RESET}")

if __name__ == "__main__":
    main()
