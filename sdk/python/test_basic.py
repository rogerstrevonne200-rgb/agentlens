import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentlens import AgentSession, trace, ToolTracer
from agentlens.cost import session_cost_summary, format_cost
from agentlens.storage import get_events


@trace
def decide_next_action(context):
    time.sleep(0.01)
    return {"action": "search", "query": context}


@ToolTracer.capture
def web_search(query):
    time.sleep(0.02)
    return {"results": [f"Result for: {query}"], "count": 1}


def main():
    print("=" * 60)
    print("AgentLens SDK — Basic Test")
    print("=" * 60)

    with AgentSession(metadata={"test": True}) as session:
        print(f"\nSession ID: {session.session_id}")

        decision = decide_next_action("find latest AI news")
        print(f"Decision: {decision}")

        results = web_search("latest AI news")
        print(f"Search results: {results}")

        decision2 = decide_next_action("summarize findings")
        print(f"Decision 2: {decision2}")

    print(f"\n{'=' * 60}")
    print("Stored Events:")
    print("=" * 60)
    events = get_events(session.session_id)
    for i, event in enumerate(events):
        print(f"\n--- Event {i + 1} ---")
        print(f"  Type:      {event['event_type']}")
        print(f"  Tool:      {event.get('tool_name') or '-'}")
        print(f"  Model:     {event.get('model') or '-'}")
        print(f"  Duration:  {event.get('duration_ms') if event.get('duration_ms') is not None else '-'}ms")
        cost = event.get("cost_usd")
        print(f"  Cost:      {format_cost(cost) if cost else '-'}")
        if event.get("metadata_json"):
            meta = json.loads(event["metadata_json"]) if isinstance(event["metadata_json"], str) else event["metadata_json"]
            if meta:
                print(f"  Metadata:  {json.dumps(meta)[:200]}")

    print(f"\n{'=' * 60}")
    print("Cost Summary:")
    print("=" * 60)
    summary = session_cost_summary(session.session_id)
    print(f"  Total cost:  {format_cost(summary['total_usd'])}")
    print(f"  Call count:  {summary['call_count']}")
    if summary["by_model"]:
        print("  By model:")
        for model, info in summary["by_model"].items():
            print(f"    {model}: {format_cost(info['cost_usd'])} ({info['calls']} calls)")
    else:
        print("  By model:    (no LLM calls in this test)")

    print(f"\n{'=' * 60}")
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
