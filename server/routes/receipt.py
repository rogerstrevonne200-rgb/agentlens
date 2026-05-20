from fastapi import APIRouter, HTTPException

from agentlens.storage import get_session, get_events
from agentlens.cost import session_cost_summary, format_cost

router = APIRouter(prefix="/api/receipt", tags=["receipt"])


def _generate_receipt(session_id: str) -> str:
    session = get_session(session_id)
    events = get_events(session_id)
    cost = session_cost_summary(session_id)

    lines = [
        f"# Agent Session Receipt",
        f"**Session:** `{session_id}`",
        f"**Started:** {session.get('started_at', 'unknown')}",
        f"**Ended:** {session.get('ended_at', 'unknown')}",
        "",
        f"## Cost Summary",
        f"- **Total cost:** {format_cost(cost['total_usd'])}",
        f"- **Total LLM calls:** {cost['call_count']}",
    ]

    if cost["by_model"]:
        lines.append("")
        lines.append("## Breakdown by Model")
        for model, data in cost["by_model"].items():
            lines.append(f"- **{model}**: {format_cost(data['cost_usd'])} ({data['calls']} calls)")

    llm_calls = [e for e in events if e.get("event_type") == "llm_call"]
    tool_calls = [e for e in events if e.get("event_type") == "tool_call"]
    errors = [e for e in events if e.get("event_type") == "error"]

    lines.append("")
    lines.append("## Activity")
    lines.append(f"- **LLM calls:** {len(llm_calls)}")
    lines.append(f"- **Tool calls:** {len(tool_calls)}")
    lines.append(f"- **Errors:** {len(errors)}")
    lines.append(f"- **Total events:** {len(events)}")

    if tool_calls:
        tool_names = sorted(set(e.get("tool_name", "unknown") for e in tool_calls))
        lines.append("")
        lines.append("## Tools Used")
        for name in tool_names:
            count = sum(1 for e in tool_calls if e.get("tool_name") == name)
            lines.append(f"- `{name}` ({count}x)")

    if errors:
        lines.append("")
        lines.append("## Errors")
        for e in errors:
            meta = e.get("metadata_json", "{}")
            if isinstance(meta, str):
                import json
                meta = json.loads(meta)
            lines.append(f"- `{e.get('tool_name', 'unknown')}`: {meta.get('error', 'unknown error')}")

    return "\n".join(lines)


@router.post("/{session_id}")
def generate_receipt(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    receipt = _generate_receipt(session_id)
    return {"receipt": receipt}
