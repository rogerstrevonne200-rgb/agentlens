import sqlite3
import os
import json
from pathlib import Path

_DB_PATH = str(Path.home() / ".agentlens" / "traces.db")
_db_initialized = False


def init_db():
    global _db_initialized
    if _db_initialized:
        return
    try:
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                total_cost_usd REAL DEFAULT 0,
                metadata_json TEXT DEFAULT '{}'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT,
                session_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost_usd REAL,
                tool_name TEXT,
                tool_input_json TEXT,
                tool_output_json TEXT,
                prompt_preview TEXT,
                response_preview TEXT,
                duration_ms INTEGER,
                metadata_json TEXT DEFAULT '{}'
            )
        """)
        conn.commit()
        conn.close()
        _db_initialized = True
    except Exception:
        pass


def _connect():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def write_event(event_dict):
    try:
        init_db()
        conn = _connect()
        conn.execute(
            """INSERT INTO events
               (trace_id, session_id, timestamp, event_type, model,
                input_tokens, output_tokens, cost_usd, tool_name,
                tool_input_json, tool_output_json, prompt_preview,
                response_preview, duration_ms, metadata_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                event_dict.get("trace_id"),
                event_dict.get("session_id"),
                event_dict.get("timestamp"),
                event_dict.get("event_type"),
                event_dict.get("model"),
                event_dict.get("input_tokens"),
                event_dict.get("output_tokens"),
                event_dict.get("cost_usd"),
                event_dict.get("tool_name"),
                json.dumps(event_dict["tool_input"]) if event_dict.get("tool_input") else None,
                json.dumps(event_dict["tool_output"]) if event_dict.get("tool_output") else None,
                event_dict.get("prompt_preview"),
                event_dict.get("response_preview"),
                event_dict.get("duration_ms"),
                json.dumps(event_dict.get("metadata", {})),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def write_session(session_id, started_at, metadata=None):
    try:
        init_db()
        conn = _connect()
        conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, started_at, metadata_json) VALUES (?,?,?)",
            (session_id, started_at, json.dumps(metadata or {})),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def update_session(session_id, ended_at, total_cost_usd):
    try:
        init_db()
        conn = _connect()
        conn.execute(
            "UPDATE sessions SET ended_at=?, total_cost_usd=? WHERE session_id=?",
            (ended_at, total_cost_usd, session_id),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_session(session_id):
    try:
        init_db()
        conn = _connect()
        row = conn.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None


def get_events(session_id):
    try:
        init_db()
        conn = _connect()
        rows = conn.execute(
            "SELECT * FROM events WHERE session_id=? ORDER BY timestamp", (session_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def list_sessions(limit=50):
    try:
        init_db()
        conn = _connect()
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_recent_events(limit=100):
    try:
        init_db()
        conn = _connect()
        rows = conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


init_db()
