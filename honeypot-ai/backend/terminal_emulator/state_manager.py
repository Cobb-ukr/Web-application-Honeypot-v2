import json
import os
from datetime import datetime
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state_history")
STATE_FILE = os.path.join(STATE_DIR, "filesystem.json")

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
    "file_contents": {},
    "last_updated": None,
}


def ensure_state_dir() -> None:
    os.makedirs(STATE_DIR, exist_ok=True)


def load_state(session_id: str = "") -> Dict[str, Any]:
    """Load the constant filesystem state. session_id is accepted but ignored."""
    ensure_state_dir()

    if not os.path.exists(STATE_FILE):
        return dict(DEFAULT_STATE)

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _merge_defaults(data)
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(session_id: str = "", state: Dict[str, Any] = None) -> None:
    """Save to the constant filesystem state file. session_id is accepted but ignored."""
    if state is None:
        return

    ensure_state_dir()
    state["last_updated"] = datetime.utcnow().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def merge_state(session_id: str = "", incoming_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """Merge incoming changes into the constant state file."""
    current = load_state()
    if not incoming_state:
        return current

    for key in ("user", "hostname", "current_dir", "file_system", "file_contents"):
        if key in incoming_state:
            current[key] = incoming_state[key]

    save_state(state=current)
    return current


def _merge_defaults(state: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(DEFAULT_STATE)
    for key in merged.keys():
        if key in state:
            merged[key] = state[key]
    return merged
