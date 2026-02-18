import json
import os
import re
from typing import Dict, List, Tuple

import yaml


FUNCTION_TO_INTENT = {
    "shell": "RCE",
    "file-read": "DataExfiltration",
    "file-write": "Persistence",
    "file-download": "ToolDeployment",
    "suid": "PrivilegeEscalation",
    "sudo": "PrivilegeEscalation",
}

INTENT_KEYWORDS = {
    "PrivilegeEscalation": ["sudo", "suid", "passwd", "shadow", "chmod", "chown"],
    "DataExfiltration": ["cat", "grep", "awk", "base64", "tar", "zip", "/etc"],
    "ToolDeployment": ["curl", "wget", "scp", "ftp"],
    "RCE": ["/bin/sh", "/bin/bash", "python", "perl", "ruby", "bash"],
    "Persistence": ["crontab", "systemctl", "service", ".ssh", "authorized_keys"],
    "Reconnaissance": ["uname", "id", "whoami", "ps", "netstat", "ifconfig", "ip a"],
}


def _base_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _playbook_paths() -> Tuple[str, str]:
    base = _base_dir()
    gtfobins_path = os.path.join(base, "playbook_data", "gtfobins.json")
    atomic_dir = os.path.join(base, "playbook_data", "atomic-red-team")
    return gtfobins_path, atomic_dir


def extract_binary(command: str) -> str:
    if not command:
        return ""
    parts = command.strip().split()
    if not parts:
        return ""
    if parts[0] in {"sudo", "env"} and len(parts) > 1:
        return parts[1]
    return parts[0]


def classify_intent_from_text(text: str) -> str:
    lower = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return intent
    return "Unknown"


def estimate_complexity(command: str, function_type: str = "") -> float:
    score = 1.0
    lower = command.lower()
    if function_type in FUNCTION_TO_INTENT:
        score += 0.5
    if any(token in lower for token in [";", "&&", "|", "||"]):
        score += 1.0
    if any(token in lower for token in ["base64", "python", "perl", "ruby", "awk", "sed"]):
        score += 0.7
    if len(command) > 80:
        score += 0.4
    if re.search(r"[A-Fa-f0-9]{16,}", command):
        score += 0.6
    return round(score, 2)


def load_gtfobins(gtfobins_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(gtfobins_path):
        return []
    with open(gtfobins_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    for binary, variants in data.items():
        for item in variants:
            command = item.get("code", "") or item.get("command", "")
            if not command:
                continue
            function_type = item.get("function", "")
            intent = FUNCTION_TO_INTENT.get(function_type, "Unknown")
            entries.append(
                {
                    "binary": binary,
                    "command": command.strip(),
                    "function": function_type,
                    "intent": intent,
                    "technique": f"GTFOBins:{binary}:{function_type}",
                    "complexity": estimate_complexity(command, function_type),
                    "source": "gtfobins",
                }
            )
    return entries


def _extract_atomic_commands(doc: Dict) -> List[str]:
    commands: List[str] = []
    atomic_tests = doc.get("atomic_tests", []) if isinstance(doc, dict) else []
    for test in atomic_tests:
        executor = test.get("executor", {}) if isinstance(test, dict) else {}
        cmd = executor.get("command")
        if isinstance(cmd, str) and cmd.strip():
            commands.append(cmd.strip())
    return commands


def load_atomic_red_team(atomic_dir: str) -> List[Dict[str, str]]:
    if not os.path.exists(atomic_dir):
        return []
    entries: List[Dict[str, str]] = []
    for root, _, files in os.walk(atomic_dir):
        for fname in files:
            if not fname.endswith(('.yml', '.yaml')):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            except Exception:
                continue

            if not isinstance(doc, dict):
                continue
            technique_id = doc.get("attack_technique", doc.get("technique", "UNKNOWN"))
            technique_name = doc.get("display_name", doc.get("name", "Unknown"))
            commands = _extract_atomic_commands(doc)
            for cmd in commands:
                intent = classify_intent_from_text(f"{technique_name} {cmd}")
                entries.append(
                    {
                        "binary": extract_binary(cmd),
                        "command": cmd,
                        "function": "atomic",
                        "intent": intent,
                        "technique": f"ATTACK:{technique_id}:{technique_name}",
                        "complexity": estimate_complexity(cmd, "atomic"),
                        "source": "atomic-red-team",
                    }
                )
    return entries


def build_playbook_index() -> Dict[str, Dict]:
    gtfobins_path, atomic_dir = _playbook_paths()
    entries = load_gtfobins(gtfobins_path)
    entries.extend(load_atomic_red_team(atomic_dir))

    binary_intent_map: Dict[str, str] = {}
    binary_complexity_map: Dict[str, float] = {}
    binary_techniques: Dict[str, List[str]] = {}

    for entry in entries:
        binary = entry.get("binary") or extract_binary(entry.get("command", ""))
        if not binary:
            continue
        intent = entry.get("intent", "Unknown")
        complexity = float(entry.get("complexity", 1.0))

        binary_techniques.setdefault(binary, [])
        if entry.get("technique") not in binary_techniques[binary]:
            binary_techniques[binary].append(entry.get("technique"))

        if binary not in binary_intent_map:
            binary_intent_map[binary] = intent
            binary_complexity_map[binary] = complexity
        else:
            if binary_intent_map[binary] == "Unknown" and intent != "Unknown":
                binary_intent_map[binary] = intent
            binary_complexity_map[binary] = max(binary_complexity_map[binary], complexity)

    return {
        "entries": entries,
        "binary_intent_map": binary_intent_map,
        "binary_complexity_map": binary_complexity_map,
        "binary_techniques": binary_techniques,
    }
