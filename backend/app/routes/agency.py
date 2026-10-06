"""
FastAPI Routes for OmniRevive-OS Continuous Specialized Agency Swarm
Powered by msitarzewski/agency-agents
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from backend.app.agency_swarm import (
    get_agency_swarm_status,
    execute_agency_cycle,
    REGISTERED_AGENTS,
    DIVISION_BREAKDOWN
)

router = APIRouter(prefix="/agency", tags=["Specialized Agency Swarm"])

@router.get("/status")
def agency_status():
    """Get real-time operational status and metrics of the continuous specialized agent swarm."""
    return get_agency_swarm_status()

@router.get("/agents")
def list_agents(
    division: Optional[str] = Query(None, description="Filter agents by division (e.g., engineering, finance, security, product, testing)"),
    search: Optional[str] = Query(None, description="Search agents by name or capability")
):
    """List all registered specialized agents from msitarzewski/agency-agents."""
    agents = REGISTERED_AGENTS
    if division:
        agents = [a for a in agents if a.get("division", "").lower() == division.lower()]
    if search:
        search_lower = search.lower()
        agents = [a for a in agents if search_lower in a.get("name", "").lower() or search_lower in a.get("description", "").lower()]
    
    return {
        "total_count": len(agents),
        "division_filter": division,
        "search_filter": search,
        "agents": [
            {
                "id": a["id"],
                "name": a["name"],
                "division": a["division"],
                "emoji": a.get("emoji", "🤖"),
                "color": a.get("color", "#0c6cf2"),
                "description": a.get("description", ""),
                "vibe": a.get("vibe", ""),
                "evaluations_count": a.get("evaluations_count", 0),
                "status": a.get("status", "ACTIVE")
            }
            for a in agents
        ]
    }

@router.get("/divisions")
def list_divisions():
    """List all agent divisions and their agent counts."""
    return {
        "total_divisions": len(DIVISION_BREAKDOWN),
        "divisions": {
            div: {
                "count": len(ag_list),
                "agents": [a["name"] for a in ag_list]
            }
            for div, ag_list in DIVISION_BREAKDOWN.items()
        }
    }

from backend.app.services.email_report_service import send_daily_email_report
from backend.app.services.autonomous_bug_repair import get_welcome_back_briefing
from backend.app.services.ai_enterprise_suite import generate_ai_executive_board_meeting

@router.post("/run_cycle")
def trigger_manual_cycle():
    """Manually trigger an immediate execution pass across all specialized agents."""
    result = execute_agency_cycle()
    return {
        "message": "Continuous specialized agent swarm cycle executed successfully.",
        "cycle_result": result
    }

@router.post("/send_daily_report")
def send_daily_report(
    email: str = Query(..., description="Target email address to receive the daily project digest report")
):
    """Generates and dispatches a rich executive daily report containing project issues, system health, and agent swarm metrics."""
    result = send_daily_email_report(recipient_email=email)
    return result

@router.get("/welcome_back")
def welcome_back_briefing():
    """Retrieves Samrudh's Welcome Back Executive Briefing detailing autonomous bug fixes and system health."""
    return get_welcome_back_briefing()

@router.get("/enterprise_board")
def enterprise_board_meeting():
    """Retrieves live autonomous AI C-Suite Board meeting decisions (CEO, CTO, CFO, CMO, VP Eng, Legal, VP Ops)."""
    return generate_ai_executive_board_meeting()


@router.post("/c-suite/debate")
def trigger_c_suite_debate(
    amount_inr: float = Query(default=15000.0, description="Dispute or failed transaction amount in INR"),
    bank_issuer: str = Query(default="HDFC", description="Bank issuer"),
    preferred_language: str = Query(default="te-IN", description="Customer language (te-IN, hi-IN, en-IN)"),
    attempt_number: int = Query(default=2, description="Attempt count")
):
    """
    Triggers a live multi-agent executive debate (CEO, CFO, Head of Recovery, SRE Sentinel)
    following the Brahma structured consensus protocol.
    """
    from autonomous_ai_company_os.c_suite import c_suite_swarm_engine
    tx_context = {
        "amount_inr": amount_inr,
        "bank_issuer": bank_issuer,
        "preferred_language": preferred_language,
        "attempt_number": attempt_number
    }
    debate_result = c_suite_swarm_engine.run_executive_debate(tx_context)
    return {
        "success": True,
        "data": debate_result
    }

@router.post("/swarm/stress-test")
@router.post("/api/v1/agency/swarm/stress-test")
def trigger_swarm_stress_test(
    total_transactions: int = Query(default=10000, description="Number of concurrent transactions to simulate"),
    target_bank_rail: str = Query(default="hdfc_switch", description="Target bank rail for catastrophic black-swan outage"),
    outage_severity: float = Query(default=0.95, description="Outage severity (0.0 to 1.0)")
):
    """
    Executes a high-throughput 10,000-TPS Multi-Agent Swarm stress run with acute black-swan failure.
    Validates LinUCB dynamic routing resilience, CAS mutex contention, and CFO quarantine invariants.
    """
    from autonomous_ai_company_os.stress_testing.swarm_stress_simulator import swarm_stress_simulator
    result = swarm_stress_simulator.run_black_swan_simulation(
        total_transactions=total_transactions,
        black_swan_target_rail=target_bank_rail,
        outage_severity=outage_severity
    )
    return {
        "success": True,
        "data": result
    }





