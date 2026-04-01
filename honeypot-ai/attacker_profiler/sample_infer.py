import argparse
import json
import os
import sys
from typing import List, Dict, Union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from attacker_profiler.step5_infer import AttackerProfiler


def _load_commands_from_file(path: str) -> List[Union[str, Dict]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "commands" in data:
        return data["commands"]
    if isinstance(data, list):
        return data
    raise ValueError("Unsupported JSON structure. Provide a list or {" + '"commands"' + ": [...]}")


def _load_commands_from_stdin() -> List[str]:
    commands = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            commands.append(line)
    return commands


def _load_commands_from_db(session_id: str) -> List[Dict]:
    from backend.database import SessionLocal, HoneypotSession
    
    db = SessionLocal()
    try:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.session_id == session_id
        ).first()
        
        if not session:
            raise SystemExit(f"Session ID {session_id} not found in database")
        
        try:
            commands = json.loads(session.commands)
        except (json.JSONDecodeError, TypeError):
            commands = []
        
        if not commands:
            raise SystemExit(f"Session {session_id} has no commands")
        
        return commands
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer attacker profile from a command sequence.")
    parser.add_argument("--model", default="", help="Path to session_model_v*.pkl (optional; uses latest)")
    parser.add_argument("--session-id", default="", help="Honeypot session ID to load from database")
    parser.add_argument("--commands-json", default="", help="JSON string: [\"cmd1\", \"cmd2\"]")
    parser.add_argument("--commands-file", default="", help="Path to JSON file with commands")

    args = parser.parse_args()

    if args.session_id:
        commands = _load_commands_from_db(args.session_id)
    elif args.commands_file:
        commands = _load_commands_from_file(args.commands_file)
    elif args.commands_json:
        commands = json.loads(args.commands_json)
    else:
        commands = _load_commands_from_stdin()

    if not commands:
        raise SystemExit("No commands provided. Use --session-id, --commands-json, --commands-file, or stdin.")

    profiler = AttackerProfiler(model_path=args.model)
    result = profiler.analyze_session(commands)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
