from . import storage

MODEL_COSTS = {
    "gpt-4o": {"input_per_1m": 2.50, "output_per_1m": 10.00},
    "gpt-4o-mini": {"input_per_1m": 0.15, "output_per_1m": 0.60},
    "gpt-4-turbo": {"input_per_1m": 10.00, "output_per_1m": 30.00},
    "gpt-3.5-turbo": {"input_per_1m": 0.50, "output_per_1m": 1.50},
    "claude-3-5-sonnet-20241022": {"input_per_1m": 3.00, "output_per_1m": 15.00},
    "claude-3-5-haiku-20241022": {"input_per_1m": 0.80, "output_per_1m": 4.00},
    "claude-3-opus-20240229": {"input_per_1m": 15.00, "output_per_1m": 75.00},
    "claude-sonnet-4-5": {"input_per_1m": 3.00, "output_per_1m": 15.00},
    "claude-opus-4-5": {"input_per_1m": 15.00, "output_per_1m": 75.00},
    "gemini-1.5-pro": {"input_per_1m": 1.25, "output_per_1m": 5.00},
    "gemini-1.5-flash": {"input_per_1m": 0.075, "output_per_1m": 0.30},
}


def calculate_cost(model, input_tokens, output_tokens):
    try:
        costs = MODEL_COSTS.get(model)
        if not costs:
            return 0.0
        input_cost = (input_tokens / 1_000_000) * costs["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * costs["output_per_1m"]
        return input_cost + output_cost
    except Exception:
        return 0.0


def format_cost(usd_float):
    try:
        return f"${usd_float:.4f}"
    except Exception:
        return "$0.0000"


def session_cost_summary(session_id):
    try:
        events = storage.get_events(session_id)
        total_usd = 0.0
        by_model = {}
        call_count = 0
        for event in events:
            cost = event.get("cost_usd") or 0.0
            model = event.get("model")
            if model:
                call_count += 1
                total_usd += cost
                if model not in by_model:
                    by_model[model] = {"cost_usd": 0.0, "calls": 0}
                by_model[model]["cost_usd"] += cost
                by_model[model]["calls"] += 1
        return {"total_usd": total_usd, "by_model": by_model, "call_count": call_count}
    except Exception:
        return {"total_usd": 0.0, "by_model": {}, "call_count": 0}
