"""Wrap an OpenAI agent with AgentLens tracing.

Requires: pip install openai
Set OPENAI_API_KEY in your environment to make real calls.
Without a key, this demo uses a mock client to show the tracing flow.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

import agentlens
from agentlens import LLMTracer, ToolTracer


# ---------------------------------------------------------------------------
# Mock OpenAI client (so the example runs without an API key)
# ---------------------------------------------------------------------------
class _Usage:
    def __init__(self):
        self.prompt_tokens = 150
        self.completion_tokens = 42

class _Message:
    def __init__(self, content):
        self.content = content
        self.role = "assistant"

class _Choice:
    def __init__(self, content):
        self.message = _Message(content)
        self.index = 0
        self.finish_reason = "stop"

class _Response:
    def __init__(self, content, model):
        self.choices = [_Choice(content)]
        self.model = model
        self.usage = _Usage()
        self.id = "chatcmpl-mock"

class _Completions:
    def create(self, **kwargs):
        model = kwargs.get("model", "gpt-4o")
        msgs = kwargs.get("messages", [])
        last = msgs[-1]["content"] if msgs else ""
        return _Response(f"Mock reply to: {last}", model)

class _Chat:
    def __init__(self):
        self.completions = _Completions()

class MockOpenAIClient:
    def __init__(self):
        self.chat = _Chat()


# ---------------------------------------------------------------------------
# Agent logic
# ---------------------------------------------------------------------------
@ToolTracer.capture
def search_web(query: str) -> dict:
    return {"results": [f"Top result for '{query}'"]}


@agentlens.trace
def run_agent(client, question: str) -> str:
    search = search_web(question)
    context = search["results"][0]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Swap MockOpenAIClient for openai.OpenAI() when you have a key
    client = MockOpenAIClient()
    LLMTracer.wrap_openai(client)

    with agentlens.AgentSession(metadata={"agent": "openai-search"}) as session:
        answer = run_agent(client, "What are the latest AI breakthroughs?")
        print(f"Agent answer: {answer}")

    from agentlens.cost import session_cost_summary, format_cost
    summary = session_cost_summary(session.session_id)
    print(f"\nCost: {format_cost(summary['total_usd'])}  |  LLM calls: {summary['call_count']}")
    print(f"Dashboard: http://localhost:5173")
