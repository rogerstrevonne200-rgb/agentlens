import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk" / "python"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.sessions import router as sessions_router
from routes.events import router as events_router
from routes.cost import router as cost_router
from routes.receipt import router as receipt_router

app = FastAPI(title="AgentLens", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(events_router)
app.include_router(cost_router)
app.include_router(receipt_router)


@app.get("/")
def root():
    return {"status": "AgentLens server running", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=7842, reload=True)
