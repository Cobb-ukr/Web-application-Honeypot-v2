import os
from typing import Dict, List, Tuple

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from attacker_profiler.step3_aggregate import sessions_to_dataset


def _model_store_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_store")


def _next_model_path() -> str:
    os.makedirs(_model_store_dir(), exist_ok=True)
    existing = [f for f in os.listdir(_model_store_dir()) if f.startswith("session_model_v") and f.endswith(".pkl")]
    if not existing:
        return os.path.join(_model_store_dir(), "session_model_v1.pkl")
    versions = []
    for f in existing:
        try:
            versions.append(int(f.replace("session_model_v", "").replace(".pkl", "")))
        except ValueError:
            continue
    next_version = max(versions) + 1 if versions else 1
    return os.path.join(_model_store_dir(), f"session_model_v{next_version}.pkl")


def train_models(
    sessions: List[Dict],
    playbook_index: Dict,
    output_path: str = "",
    test_size: float = 0.2,
    seed: int = 42,
) -> Tuple[str, Dict[str, float]]:
    X, y_intent, y_skill, feature_names = sessions_to_dataset(sessions, playbook_index)

    if not output_path:
        output_path = _next_model_path()

    X_train, X_test, y_intent_train, y_intent_test = train_test_split(
        X, y_intent, test_size=test_size, random_state=seed, stratify=y_intent if len(set(y_intent)) > 1 else None
    )
    _, _, y_skill_train, y_skill_test = train_test_split(
        X, y_skill, test_size=test_size, random_state=seed, stratify=y_skill if len(set(y_skill)) > 1 else None
    )

    intent_model = RandomForestClassifier(n_estimators=200, random_state=seed)
    skill_model = RandomForestClassifier(n_estimators=200, random_state=seed)

    intent_model.fit(X_train, y_intent_train)
    skill_model.fit(X_train, y_skill_train)

    intent_pred = intent_model.predict(X_test)
    skill_pred = skill_model.predict(X_test)

    metrics = {
        "intent_accuracy": accuracy_score(y_intent_test, intent_pred) if y_intent_test else 0.0,
        "skill_accuracy": accuracy_score(y_skill_test, skill_pred) if y_skill_test else 0.0,
    }

    bundle = {
        "intent_model": intent_model,
        "skill_model": skill_model,
        "feature_names": feature_names,
        "intent_labels": sorted(set(y_intent)),
        "skill_labels": sorted(set(y_skill)),
    }

    joblib.dump(bundle, output_path)

    return output_path, metrics


def load_model_bundle(path: str) -> Dict:
    return joblib.load(path)
