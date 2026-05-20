"""Simplest possible AgentLens integration — 5 lines."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

import agentlens

@agentlens.trace
def decide(prompt):
    return {"action": "respond", "text": f"Handled: {prompt}"}

with agentlens.AgentSession(metadata={"example": "minimal"}) as session:
    result = decide("What is the weather?")
    print(f"Result: {result}")

print(f"Session {session.session_id} recorded — open dashboard at http://localhost:5173")
