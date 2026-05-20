# AgentLens — Project Context

## What this project is
AgentLens is a framework-agnostic Python SDK + local dashboard for AI agent observability.
The core problem: developers cannot answer "what did my agent do, why, what did it cost,
and what was it allowed to do?" after an agent run. We solve this with zero-config tracing.

## Key design principles
- Zero vendor lock-in: works with OpenAI, Anthropic, LangChain, CrewAI, LlamaIndex, raw API calls
- Zero infrastructure: traces stored locally in SQLite by default, no cloud required
- Drop-in: one decorator (@agentlens.trace) is enough to get full visibility
- Framework-agnostic: wraps the underlying LLM HTTP calls, not framework internals
- Open-source core: MIT license, cloud sync is the paid tier

## Tech stack
- SDK: Python 3.10+, zero external dependencies for core tracing
- Storage: SQLite (local), Supabase (cloud sync tier)
- Server: FastAPI + uvicorn
- Dashboard: React 18 + Vite + Tailwind CSS

## Trace data model (JSONL)
Each trace event is one line:
{
  "trace_id": "uuid",
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "event_type": "llm_call" | "tool_call" | "decision" | "error" | "session_start" | "session_end",
  "model": "gpt-4o" | "claude-3-5-sonnet" | etc,
  "input_tokens": int,
  "output_tokens": int,
  "cost_usd": float,
  "tool_name": str | null,
  "tool_input": dict | null,
  "tool_output": dict | null,
  "prompt_preview": str (first 200 chars),
  "response_preview": str (first 200 chars),
  "duration_ms": int,
  "metadata": dict
}

## What NOT to do
- Do not add cloud dependencies to the core SDK
- Do not use LangChain internals
- Do not add authentication to the local dashboard
- Do not use TypeScript

## Current build phase
Phase: Step 0 complete — starting Step 1 next
