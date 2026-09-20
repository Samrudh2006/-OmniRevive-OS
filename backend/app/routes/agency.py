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


