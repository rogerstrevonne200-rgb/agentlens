import uuid
import time
import threading
import functools
from datetime import datetime, timezone

from . import storage
from . import cost as cost_module

_thread_local = threading.local()


def _get_current_session():
    return getattr(_thread_local, "session", None)


def _set_current_session(session):
    _thread_local.session = session


def _safe_repr(obj, max_len=200):
    try:
        s = repr(obj)
        return s[:max_len]
    except Exception:
        return "<unrepresentable>"


def _emit_event(event_dict):
    try:
        if "trace_id" not in event_dict:
            event_dict["trace_id"] = str(uuid.uuid4())
        if "timestamp" not in event_dict:
            event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()

        session = _get_current_session()
        if session is None:
            session = AgentSession(_anonymous=True)
            session._start_time = time.monotonic()
            session._started_at = datetime.now(timezone.utc).isoformat()
            _set_current_session(session)
            storage.write_session(session.session_id, session._started_at)
            _emit_event({"event_type": "session_start", "metadata": {}})

        event_dict["session_id"] = session.session_id

        if event_dict.get("model") and event_dict.get("input_tokens") is not None:
            event_dict.setdefault(
                "cost_usd",
                cost_module.calculate_cost(
                    event_dict["model"],
                    event_dict.get("input_tokens", 0),
                    event_dict.get("output_tokens", 0),
                ),
            )

        storage.write_event(event_dict)
    except Exception:
        pass


class AgentSession:
    def __init__(self, metadata=None, _anonymous=False):
        self.session_id = str(uuid.uuid4())
        self.metadata = metadata or {}
        self._anonymous = _anonymous
        self._start_time = None
        self._started_at = None

    def __enter__(self):
        try:
            self._start_time = time.monotonic()
            self._started_at = datetime.now(timezone.utc).isoformat()
            _set_current_session(self)
            storage.write_session(self.session_id, self._started_at, self.metadata)
            _emit_event({"event_type": "session_start", "metadata": self.metadata})
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            duration_ms = int((time.monotonic() - self._start_time) * 1000) if self._start_time else 0
            events = storage.get_events(self.session_id)
            total_cost = sum((e.get("cost_usd") or 0) for e in events)
            ended_at = datetime.now(timezone.utc).isoformat()

            _emit_event({
                "event_type": "session_end",
                "duration_ms": duration_ms,
                "metadata": {"total_cost_usd": total_cost, "duration_ms": duration_ms},
            })

            storage.update_session(self.session_id, ended_at, total_cost)
        except Exception:
            pass
        finally:
            _set_current_session(None)
        return False


def trace(func=None, *, name=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            event_name = name or fn.__name__
            start = time.monotonic()
            try:
                result = fn(*args, **kwargs)
                duration_ms = int((time.monotonic() - start) * 1000)
                _emit_event({
                    "event_type": "decision",
                    "tool_name": event_name,
                    "duration_ms": duration_ms,
                    "metadata": {"args": _safe_repr(args), "kwargs": _safe_repr(kwargs)},
                })
                return result
            except Exception as e:
                duration_ms = int((time.monotonic() - start) * 1000)
                _emit_event({
                    "event_type": "error",
                    "tool_name": event_name,
                    "duration_ms": duration_ms,
                    "metadata": {"error": str(e), "args": _safe_repr(args), "kwargs": _safe_repr(kwargs)},
                })
                raise
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def get_dashboard_url(host="localhost", port=8100):
    return f"http://{host}:{port}"
