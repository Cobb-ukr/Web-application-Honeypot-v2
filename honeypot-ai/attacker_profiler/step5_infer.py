import os
from typing import Dict, List, Union

from attacker_profiler.step1_playbook import build_playbook_index
from attacker_profiler.step3_aggregate import aggregate_session
from attacker_profiler.step4_train import load_model_bundle


def _model_store_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_store")


def _latest_model_path() -> str:
    if not os.path.exists(_model_store_dir()):
        return ""
    models = [f for f in os.listdir(_model_store_dir()) if f.startswith("session_model_v") and f.endswith(".pkl")]
    if not models:
        return ""
    versions = []
    for f in models:
        try:
            versions.append(int(f.replace("session_model_v", "").replace(".pkl", "")))
        except ValueError:
            continue
    if not versions:
        return ""
    latest = max(versions)
    return os.path.join(_model_store_dir(), f"session_model_v{latest}.pkl")


def _normalize_commands(commands: List[Union[str, Dict]]) -> List[Dict]:
    normalized = []
    for c in commands:
        if isinstance(c, dict):
            normalized.append({"command": c.get("command", ""), "response": c.get("response", "")})
        else:
            normalized.append({"command": str(c), "response": ""})
    return normalized


class AttackerProfiler:
    def __init__(self, model_path: str = ""):
        self.playbook_index = build_playbook_index()
        if not model_path:
            model_path = _latest_model_path()
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError("No trained session model found in attacker_profiler/model_store")
        self.bundle = load_model_bundle(model_path)

    def analyze_session(self, commands: List[Union[str, Dict]]) -> Dict:
        session = {"commands": _normalize_commands(commands)}
        features, _ = aggregate_session(session, self.playbook_index)

        intent_model = self.bundle["intent_model"]
        skill_model = self.bundle["skill_model"]

        intent = str(intent_model.predict([features])[0])
        skill = str(skill_model.predict([features])[0])

        intent_conf = _predict_confidence(intent_model, features)
        skill_conf = _predict_confidence(skill_model, features)

        return {
            "intent": intent,
            "skill": skill,
            "confidence": round((intent_conf + skill_conf) / 2, 3),
            "intent_confidence": round(intent_conf, 3),
            "skill_confidence": round(skill_conf, 3),
        }


def _predict_confidence(model, features: List[float]) -> float:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([features])
        if proba is not None and len(proba) > 0:
            return float(max(proba[0]))
    return 0.5
