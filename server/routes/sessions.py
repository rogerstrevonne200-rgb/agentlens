from fastapi import APIRouter, HTTPException, Query

from agentlens.storage import list_sessions, get_session, get_events, init_db, _connect

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
def sessions_list(limit: int = Query(default=50, ge=1, le=500)):
    return list_sessions(limit=limit)


@router.get("/{session_id}")
def session_detail(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    events = get_events(session_id)
    return {**session, "events": events}


@router.delete("/{session_id}")
def session_delete(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    init_db()
    conn = _connect()
    conn.execute("DELETE FROM events WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()
    return {"deleted": session_id}
