import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agentlens.storage import get_recent_events

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/recent")
def recent_events():
    return get_recent_events(limit=100)


@router.get("/stream")
async def event_stream():
    async def generate():
        last_seen_id = 0
        while True:
            events = get_recent_events(limit=20)
            new_events = [e for e in events if e.get("id", 0) > last_seen_id]
            if new_events:
                last_seen_id = max(e.get("id", 0) for e in new_events)
                for event in reversed(new_events):
                    yield f"data: {json.dumps(event)}\n\n"
            else:
                yield f"data: {json.dumps({'keepalive': True})}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")
