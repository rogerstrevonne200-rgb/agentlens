from fastapi import APIRouter, HTTPException

from agentlens.storage import list_sessions, get_session
from agentlens.cost import session_cost_summary

router = APIRouter(prefix="/api/cost", tags=["cost"])


@router.get("/summary")
def cost_summary():
    sessions = list_sessions(limit=10000)
    total_usd = 0.0
    by_model = {}
    total_calls = 0
    for s in sessions:
        summary = session_cost_summary(s["session_id"])
        total_usd += summary["total_usd"]
        total_calls += summary["call_count"]
        for model, data in summary["by_model"].items():
            if model not in by_model:
                by_model[model] = {"cost_usd": 0.0, "calls": 0}
            by_model[model]["cost_usd"] += data["cost_usd"]
            by_model[model]["calls"] += data["calls"]
    return {"total_usd": total_usd, "by_model": by_model, "total_calls": total_calls}


@router.get("/session/{session_id}")
def cost_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_cost_summary(session_id)
