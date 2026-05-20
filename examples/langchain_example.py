"""AgentLens as a LangChain callback handler.

Shows how to plug AgentLens into any LangChain chain/agent via callbacks.
No LangChain dependency required to run the demo — the handler class stands
alone and the example simulates the callback lifecycle.
"""

import sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))

import agentlens
from agentlens.tracer import _emit_event


# ---------------------------------------------------------------------------
# AgentLens ↔ LangChain callback handler
# ---------------------------------------------------------------------------
class AgentLensCallbackHandler:
    """Drop-in LangChain callback handler that emits AgentLens trace events.

    Usage with a real LangChain chain:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", callbacks=[AgentLensCallbackHandler()])
    """

    def __init__(self):
        self._timers: dict[str, float] = {}

    # -- LLM callbacks --
    def on_llm_start(self, serialized, prompts, *, run_id=None, **kwargs):
        self._timers[str(run_id)] = time.monotonic()

    def on_llm_end(self, response, *, run_id=None, **kwargs):
        duration_ms = int((time.monotonic() - self._timers.pop(str(run_id), time.monotonic())) * 1000)
        llm_output = getattr(response, "llm_output", {}) or {}
        usage = llm_output.get("token_usage", {})
        model = llm_output.get("model_name", "unknown")

        text = ""
        generations = getattr(response, "generations", [])
        if generations and generations[0]:
            text = getattr(generations[0][0], "text", "")

        _emit_event({
            "event_type": "llm_call",
            "model": model,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "response_preview": text[:200],
            "duration_ms": duration_ms,
        })

    # -- Tool callbacks --
    def on_tool_start(self, serialized, input_str, *, run_id=None, **kwargs):
        self._timers[str(run_id)] = time.monotonic()

    def on_tool_end(self, output, *, run_id=None, **kwargs):
        duration_ms = int((time.monotonic() - self._timers.pop(str(run_id), time.monotonic())) * 1000)
        tool_name = kwargs.get("name", "unknown_tool")
        _emit_event({
            "event_type": "tool_call",
            "tool_name": tool_name,
            "tool_output": {"result": str(output)[:200]},
            "duration_ms": duration_ms,
        })

    # -- Error callback --
    def on_llm_error(self, error, *, run_id=None, **kwargs):
        self._timers.pop(str(run_id), None)
        _emit_event({
            "event_type": "error",
            "metadata": {"error": str(error)},
        })


# ---------------------------------------------------------------------------
# Demo: simulate a LangChain chain calling back into our handler
# ---------------------------------------------------------------------------
class _FakeLLMOutput:
    def __init__(self):
        self.llm_output = {"model_name": "gpt-4o", "token_usage": {"prompt_tokens": 200, "completion_tokens": 60}}

class _FakeGeneration:
    def __init__(self, text):
        self.text = text

class _FakeLLMResult:
    def __init__(self):
        self.llm_output = {"model_name": "gpt-4o", "token_usage": {"prompt_tokens": 200, "completion_tokens": 60}}
        self.generations = [[_FakeGeneration("The capital of France is Paris.")]]


if __name__ == "__main__":
    handler = AgentLensCallbackHandler()

    with agentlens.AgentSession(metadata={"agent": "langchain-demo"}) as session:
        # Simulate LLM call
        run_id = uuid.uuid4()
        handler.on_llm_start({}, ["What is the capital of France?"], run_id=run_id)
        time.sleep(0.05)  # simulate latency
        handler.on_llm_end(_FakeLLMResult(), run_id=run_id)

        # Simulate tool call
        tool_run_id = uuid.uuid4()
        handler.on_tool_start({"name": "wikipedia"}, "Paris", run_id=tool_run_id)
        time.sleep(0.02)
        handler.on_tool_end("Paris is the capital of France.", run_id=tool_run_id, name="wikipedia")

        # Simulate second LLM call
        run_id2 = uuid.uuid4()
        handler.on_llm_start({}, ["Summarize: Paris is the capital of France."], run_id=run_id2)
        time.sleep(0.03)
        handler.on_llm_end(_FakeLLMResult(), run_id=run_id2)

    from agentlens.cost import session_cost_summary, format_cost
    summary = session_cost_summary(session.session_id)
    print(f"LangChain agent traced — {summary['call_count']} LLM calls, cost: {format_cost(summary['total_usd'])}")
    print(f"Dashboard: http://localhost:5173")
