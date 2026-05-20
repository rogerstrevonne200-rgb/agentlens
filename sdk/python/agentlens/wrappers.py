import time
import functools

from .tracer import _emit_event, _safe_repr


class LLMTracer:
    @staticmethod
    def wrap_openai(client):
        try:
            original_create = client.chat.completions.create

            @functools.wraps(original_create)
            def patched_create(*args, **kwargs):
                start = time.monotonic()
                response = original_create(*args, **kwargs)
                duration_ms = int((time.monotonic() - start) * 1000)

                try:
                    model = getattr(response, "model", kwargs.get("model", "unknown"))
                    usage = getattr(response, "usage", None)
                    input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
                    output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

                    messages = kwargs.get("messages", [])
                    prompt_preview = ""
                    if messages:
                        content = messages[-1].get("content", "")
                        prompt_preview = str(content)[:200]

                    response_text = ""
                    if hasattr(response, "choices") and response.choices:
                        msg = response.choices[0].message
                        response_text = getattr(msg, "content", "") or ""
                    response_preview = response_text[:200]

                    from . import cost as cost_module

                    cost_usd = cost_module.calculate_cost(model, input_tokens, output_tokens)

                    _emit_event({
                        "event_type": "llm_call",
                        "model": model,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost_usd": cost_usd,
                        "prompt_preview": prompt_preview,
                        "response_preview": response_preview,
                        "duration_ms": duration_ms,
                    })
                except Exception:
                    pass

                return response

            client.chat.completions.create = patched_create
        except Exception:
            pass
        return client

    @staticmethod
    def wrap_anthropic(client):
        try:
            original_create = client.messages.create

            @functools.wraps(original_create)
            def patched_create(*args, **kwargs):
                start = time.monotonic()
                response = original_create(*args, **kwargs)
                duration_ms = int((time.monotonic() - start) * 1000)

                try:
                    model = getattr(response, "model", kwargs.get("model", "unknown"))
                    usage = getattr(response, "usage", None)
                    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
                    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

                    messages = kwargs.get("messages", [])
                    prompt_preview = ""
                    if messages:
                        last = messages[-1]
                        content = last.get("content", "")
                        if isinstance(content, str):
                            prompt_preview = content[:200]
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    prompt_preview = block["text"][:200]
                                    break

                    response_text = ""
                    if hasattr(response, "content") and response.content:
                        for block in response.content:
                            if hasattr(block, "text"):
                                response_text = block.text
                                break
                    response_preview = response_text[:200]

                    from . import cost as cost_module

                    cost_usd = cost_module.calculate_cost(model, input_tokens, output_tokens)

                    _emit_event({
                        "event_type": "llm_call",
                        "model": model,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost_usd": cost_usd,
                        "prompt_preview": prompt_preview,
                        "response_preview": response_preview,
                        "duration_ms": duration_ms,
                    })
                except Exception:
                    pass

                return response

            client.messages.create = patched_create
        except Exception:
            pass
        return client

    @staticmethod
    def wrap_requests():
        try:
            import sys

            requests_mod = sys.modules.get("requests")
            if requests_mod is None:
                try:
                    import requests as requests_mod
                except ImportError:
                    return

            original_request = requests_mod.Session.request
            _API_HOSTS = ("api.openai.com", "api.anthropic.com")

            @functools.wraps(original_request)
            def patched_request(self, method, url, *args, **kwargs):
                is_api_call = any(host in str(url) for host in _API_HOSTS)

                if not is_api_call:
                    return original_request(self, method, url, *args, **kwargs)

                start = time.monotonic()
                response = original_request(self, method, url, *args, **kwargs)
                duration_ms = int((time.monotonic() - start) * 1000)

                try:
                    body = response.json() if hasattr(response, "json") else {}
                    model = body.get("model", "unknown")
                    usage = body.get("usage", {})

                    input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
                    output_tokens = usage.get("completion_tokens") or usage.get("output_tokens") or 0

                    from . import cost as cost_module

                    cost_usd = cost_module.calculate_cost(model, input_tokens, output_tokens)

                    _emit_event({
                        "event_type": "llm_call",
                        "model": model,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost_usd": cost_usd,
                        "duration_ms": duration_ms,
                        "metadata": {"url": str(url), "method": method},
                    })
                except Exception:
                    pass

                return response

            requests_mod.Session.request = patched_request
        except Exception:
            pass


class ToolTracer:
    @staticmethod
    def capture(func=None, *, name=None):
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                tool_name = name or fn.__name__
                start = time.monotonic()
                try:
                    result = fn(*args, **kwargs)
                    duration_ms = int((time.monotonic() - start) * 1000)
                    _emit_event({
                        "event_type": "tool_call",
                        "tool_name": tool_name,
                        "tool_input": {"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)},
                        "tool_output": {"result": _safe_repr(result)},
                        "duration_ms": duration_ms,
                    })
                    return result
                except Exception as e:
                    duration_ms = int((time.monotonic() - start) * 1000)
                    _emit_event({
                        "event_type": "tool_call",
                        "tool_name": tool_name,
                        "tool_input": {"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)},
                        "tool_output": {"error": str(e)},
                        "duration_ms": duration_ms,
                        "metadata": {"error": str(e)},
                    })
                    raise
            return wrapper

        if func is not None:
            return decorator(func)
        return decorator
