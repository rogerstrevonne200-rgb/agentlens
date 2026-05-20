# AgentLens

**Know what your agent did, why, and what it cost.**

AgentLens is a framework-agnostic Python SDK + local dashboard for AI agent observability. One decorator gives you full visibility into any agent — no cloud required.

## Install

```bash
pip install agentlens
```

Zero dependencies. Python 3.10+.

## Quick start

```python
import agentlens

@agentlens.trace
def decide(prompt):
    return {"action": "respond", "text": f"Handled: {prompt}"}

with agentlens.AgentSession() as session:
    result = decide("What is the weather?")
```

That's it. Every traced call is recorded to a local SQLite database. Start the dashboard to explore your sessions:

```bash
./run.sh
# → Dashboard: http://localhost:5173
# → API:       http://localhost:7842
```

## The 4 questions

Every agent run should answer four questions:

| Question | How AgentLens answers it |
|---|---|
| **What did it do?** | Full trace of every LLM call, tool invocation, and decision |
| **Why did it do it?** | Prompt previews and input/output capture at each step |
| **What did it cost?** | Per-call and per-session cost tracking with model-aware pricing |
| **What was it allowed to do?** | Tool call audit log with inputs and outputs |

## Framework support

Works with any framework — or none at all:

```python
# OpenAI
from agentlens import LLMTracer
client = openai.OpenAI()
LLMTracer.wrap_openai(client)

# Anthropic
client = anthropic.Anthropic()
LLMTracer.wrap_anthropic(client)

# LangChain (callback handler)
from examples.langchain_example import AgentLensCallbackHandler
llm = ChatOpenAI(callbacks=[AgentLensCallbackHandler()])

# Raw HTTP (auto-patches requests)
LLMTracer.wrap_requests()
```

## Comparison

| Feature | AgentLens | LangSmith | Langfuse |
|---|---|---|---|
| **Setup** | `pip install agentlens` | Cloud signup + API key | Self-host or cloud signup |
| **Infrastructure** | None (local SQLite) | Cloud only | Postgres + clickhouse |
| **Framework lock-in** | None | LangChain-first | LangChain-first |
| **Pricing** | Free & open source | Free tier, then paid | Free tier, then paid |
| **Data residency** | Your machine | Their cloud | Your infra or their cloud |
| **Line-of-code to trace** | 1 (`@agentlens.trace`) | 2-5 | 3-10 |
| **Offline use** | Yes | No | Self-host only |
| **Dependencies** | 0 | 5+ | 3+ |

## License
AgentLens is free for personal and non-commercial use.
Commercial use requires a license from Trevonne Rogers.
© 2026 Trevonne Rogers. All rights reserved.
