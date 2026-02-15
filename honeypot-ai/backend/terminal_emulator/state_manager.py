import json
import os
from datetime import datetime
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state_history")

DEFAULT_STATE: Dict[str, Any] = {
    "user": "user",
    "hostname": "internal",
    "current_dir": "/home/user",
    "file_system": {
        "/home/user": ["passwords.txt", "financial_report_2024.pdf", "admin_backup.sql", "private_key.pem"],
        "/": ["home", "etc", "var", "usr"],
        "/etc": ["passwd", "shadow", "hosts"],
        "/var": ["log", "www"],
        "/usr": ["bin", "lib"],
    },
    "last_updated": None,
}


def ensure_state_dir() -> None:
    os.makedirs(STATE_DIR, exist_ok=True)


def get_state_path(session_id: str) -> str:
    ensure_state_dir()
    safe_session = session_id.replace("/", "_")
    return os.path.join(STATE_DIR, f"{safe_session}.json")


def load_state(session_id: str) -> Dict[str, Any]:
    if not session_id:
        return dict(DEFAULT_STATE)

    path = get_state_path(session_id)
    if not os.path.exists(path):
        return dict(DEFAULT_STATE)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _merge_defaults(data)
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(session_id: str, state: Dict[str, Any]) -> None:
    if not session_id:
        return

    ensure_state_dir()
    state["last_updated"] = datetime.utcnow().isoformat()
    path = get_state_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def merge_state(session_id: str, incoming_state: Dict[str, Any]) -> Dict[str, Any]:
    current = load_state(session_id)
    if not incoming_state:
        return current

    for key in ("user", "hostname", "current_dir", "file_system"):
        if key in incoming_state:
            current[key] = incoming_state[key]

    save_state(session_id, current)
    return current


def _merge_defaults(state: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(DEFAULT_STATE)
    for key in merged.keys():
        if key in state:
            merged[key] = state[key]
    return merged
