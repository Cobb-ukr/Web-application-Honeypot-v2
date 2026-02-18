import random
import uuid
from datetime import datetime
from typing import Dict, List

from attacker_profiler.step1_playbook import estimate_complexity, extract_binary


BENIGN_COMMANDS = [
    "ls",
    "pwd",
    "whoami",
    "id",
    "uname -a",
    "cat /etc/hostname",
    "echo test",
    "ls -la",
    "df -h",
]


def _maybe_add_noise(command: str, rng: random.Random) -> str:
    if rng.random() < 0.2:
        return command.replace(" ", "  ")
    if rng.random() < 0.15:
        return f"{command} | base64"
    if rng.random() < 0.15:
        return f"{command} && echo done"
    if rng.random() < 0.1:
        return f"{command} ; echo ok"
    return command


def _sample_intent(intents: List[str], rng: random.Random) -> str:
    return rng.choice(intents)


def _compute_skill(commands: List[str], playbook_index: Dict) -> str:
    binary_complexity = playbook_index.get("binary_complexity_map", {})
    if not commands:
        return "novice"

    total = 0.0
    chain_count = 0
    for cmd in commands:
        binary = extract_binary(cmd)
        total += binary_complexity.get(binary, estimate_complexity(cmd))
        if any(token in cmd for token in [";", "&&", "|", "||"]):
            chain_count += 1

    avg = total / max(len(commands), 1)
    chain_rate = chain_count / max(len(commands), 1)

    score = avg + chain_rate
    if score < 2.2:
        return "novice"
    if score < 3.4:
        return "intermediate"
    return "advanced"


def generate_synthetic_sessions(
    playbook_index: Dict,
    num_sessions: int = 200,
    seed: int = 42,
    min_cmds: int = 3,
    max_cmds: int = 12,
) -> List[Dict]:
    rng = random.Random(seed)
    entries = playbook_index.get("entries", [])
    intents = sorted({e.get("intent", "Unknown") for e in entries})
    intents = [i for i in intents if i and i != "Unknown"]
    if not intents:
        intents = ["Reconnaissance", "RCE", "DataExfiltration", "Persistence", "ToolDeployment"]

    sessions: List[Dict] = []

    for _ in range(num_sessions):
        session_intent = _sample_intent(intents, rng)
        cmd_count = rng.randint(min_cmds, max_cmds)
        candidates = [e for e in entries if e.get("intent") == session_intent]
        if not candidates:
            candidates = entries

        commands = []
        for _ in range(cmd_count):
            if rng.random() < 0.2:
                cmd = rng.choice(BENIGN_COMMANDS)
            else:
                cmd = rng.choice(candidates).get("command", "")
            if cmd:
                commands.append(_maybe_add_noise(cmd, rng))

        skill = _compute_skill(commands, playbook_index)
        sessions.append(
            {
                "session_id": str(uuid.uuid4()),
                "intent": session_intent,
                "skill": skill,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "commands": [{"command": c, "response": ""} for c in commands],
            }
        )

    return sessions
