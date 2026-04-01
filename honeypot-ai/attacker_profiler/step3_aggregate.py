import math
import re
from typing import Dict, List, Tuple

from attacker_profiler.step1_playbook import extract_binary


KEYWORDS = re.compile(r"(select|union|insert|delete|update|script|alert|etc|passwd|sudo|curl|wget|nc|base64)", re.IGNORECASE)


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    entropy = 0.0
    length = len(text)
    for x in range(256):
        p_x = float(text.count(chr(x))) / length
        if p_x > 0:
            entropy += -p_x * math.log(p_x, 2)
    return entropy


def extract_command_features(command: str, playbook_index: Dict) -> Dict:
    length = len(command)
    entropy = _entropy(command)
    special_chars = len(re.findall(r"[^a-zA-Z0-9\s]", command))
    keywords = len(KEYWORDS.findall(command))

    chain_semicolon = 1 if ";" in command else 0
    chain_pipe = 1 if "|" in command else 0
    chain_and = 1 if "&&" in command else 0

    binary = extract_binary(command)
    intent = playbook_index.get("binary_intent_map", {}).get(binary, "Unknown")
    complexity = playbook_index.get("binary_complexity_map", {}).get(binary, 1.0)

    return {
        "length": length,
        "entropy": entropy,
        "special_chars": special_chars,
        "keywords": keywords,
        "chain_semicolon": chain_semicolon,
        "chain_pipe": chain_pipe,
        "chain_and": chain_and,
        "binary": binary,
        "intent": intent,
        "complexity": complexity,
    }


def aggregate_session(session: Dict, playbook_index: Dict) -> Tuple[List[float], List[str]]:
    commands = session.get("commands", [])
    command_strings = [c["command"] if isinstance(c, dict) else str(c) for c in commands]

    features = []
    intents = ["Reconnaissance", "RCE", "DataExfiltration", "Persistence", "ToolDeployment", "PrivilegeEscalation", "Unknown"]
    intent_counts = {k: 0 for k in intents}

    lengths = []
    entropies = []
    specials = []
    complexities = []
    chain_total = 0
    binaries = set()

    for cmd in command_strings:
        if not cmd:
            continue
        f = extract_command_features(cmd, playbook_index)
        lengths.append(f["length"])
        entropies.append(f["entropy"])
        specials.append(f["special_chars"])
        complexities.append(f["complexity"])
        chain_total += f["chain_semicolon"] + f["chain_pipe"] + f["chain_and"]
        binaries.add(f["binary"])
        if f["intent"] not in intent_counts:
            intent_counts["Unknown"] += 1
        else:
            intent_counts[f["intent"]] += 1

    total_cmds = max(len(command_strings), 1)
    features.append(total_cmds)
    features.append(len(binaries))
    features.append(chain_total / total_cmds)

    features.extend([
        sum(lengths) / max(len(lengths), 1),
        max(lengths, default=0),
        sum(entropies) / max(len(entropies), 1),
        max(entropies, default=0),
        sum(specials) / max(len(specials), 1),
        max(specials, default=0),
        sum(complexities) / max(len(complexities), 1),
        max(complexities, default=0),
    ])

    for intent in intents:
        features.append(intent_counts[intent])

    feature_names = [
        "total_commands",
        "distinct_binaries",
        "chain_rate",
        "avg_length",
        "max_length",
        "avg_entropy",
        "max_entropy",
        "avg_special_chars",
        "max_special_chars",
        "avg_complexity",
        "max_complexity",
    ] + [f"intent_count_{intent}" for intent in intents]

    return features, feature_names


def sessions_to_dataset(sessions: List[Dict], playbook_index: Dict) -> Tuple[List[List[float]], List[str], List[str], List[str]]:
    X: List[List[float]] = []
    y_intent: List[str] = []
    y_skill: List[str] = []
    feature_names: List[str] = []

    for session in sessions:
        features, names = aggregate_session(session, playbook_index)
        X.append(features)
        y_intent.append(session.get("intent", "Unknown"))
        y_skill.append(session.get("skill", "novice"))
        feature_names = names

    return X, y_intent, y_skill, feature_names
