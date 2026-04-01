import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from attacker_profiler.step1_playbook import build_playbook_index
from attacker_profiler.step2_generate import generate_synthetic_sessions
from attacker_profiler.step4_train import train_models
from attacker_profiler.step5_infer import AttackerProfiler


REAL_SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "real_sessions")
TRAINING_LOG_PATH = os.path.join(os.path.dirname(__file__), "training_log.json")


def _ensure_dirs():
    os.makedirs(REAL_SESSIONS_DIR, exist_ok=True)


def _log_training_event(event: Dict):
    _ensure_dirs()
    log = []
    if os.path.exists(TRAINING_LOG_PATH):
        with open(TRAINING_LOG_PATH, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    log.append(event)
    with open(TRAINING_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def save_real_session(session_id: str, commands: List[Dict], ip_address: str = "") -> str:
    _ensure_dirs()
    
    session_data = {
        "session_id": session_id,
        "ip_address": ip_address,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "commands": commands,
        "labeled": False,
        "intent": None,
        "skill": None,
    }
    
    session_file = os.path.join(REAL_SESSIONS_DIR, f"{session_id}.json")
    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)
    
    return session_file


def auto_label_session(session_id: str, confidence_threshold: float = 0.70) -> bool:
    session_file = os.path.join(REAL_SESSIONS_DIR, f"{session_id}.json")
    if not os.path.exists(session_file):
        return False
    
    with open(session_file, "r") as f:
        session_data = json.load(f)
    
    if session_data.get("labeled"):
        return True
    
    try:
        profiler = AttackerProfiler()
        result = profiler.analyze_session(session_data["commands"])
        
        if result["confidence"] >= confidence_threshold:
            session_data["intent"] = result["intent"]
            session_data["skill"] = result["skill"]
            session_data["labeled"] = True
            session_data["auto_labeled"] = True
            session_data["confidence"] = result["confidence"]
            
            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)
            
            return True
    except Exception as e:
        print(f"Auto-labeling failed for {session_id}: {e}")
    
    return False


def load_real_sessions(labeled_only: bool = True) -> List[Dict]:
    _ensure_dirs()
    sessions = []
    
    for fname in os.listdir(REAL_SESSIONS_DIR):
        if not fname.endswith(".json"):
            continue
        
        path = os.path.join(REAL_SESSIONS_DIR, fname)
        with open(path, "r") as f:
            session = json.load(f)
        
        if labeled_only and not session.get("labeled"):
            continue
        
        sessions.append(session)
    
    return sessions


def retrain_with_real_sessions(
    num_synthetic: int = 100,
    confidence_threshold: float = 0.70,
    min_real_sessions: int = 5,
) -> Optional[Dict]:
    _ensure_dirs()
    
    real_sessions = load_real_sessions(labeled_only=False)
    
    for session in real_sessions:
        if not session.get("labeled"):
            auto_label_session(session["session_id"], confidence_threshold)
    
    real_sessions = load_real_sessions(labeled_only=True)
    
    if len(real_sessions) < min_real_sessions:
        print(f"Insufficient real sessions: {len(real_sessions)} (need {min_real_sessions})")
        return None
    
    playbook_index = build_playbook_index()
    synthetic_sessions = generate_synthetic_sessions(playbook_index, num_sessions=num_synthetic, seed=42)
    
    all_sessions = synthetic_sessions + real_sessions
    
    model_path, metrics = train_models(all_sessions, playbook_index)
    
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_path": model_path,
        "synthetic_sessions": num_synthetic,
        "real_sessions": len(real_sessions),
        "total_sessions": len(all_sessions),
        "metrics": metrics,
    }
    _log_training_event(event)
    
    print(f"Retrained model with {len(real_sessions)} real + {num_synthetic} synthetic sessions")
    print(f"Model saved: {model_path}")
    print(f"Metrics: {metrics}")
    
    return event


def trigger_incremental_update(session_id: str, auto_retrain: bool = False) -> Dict:
    from backend.database import SessionLocal, HoneypotSession
    
    db = SessionLocal()
    try:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.session_id == session_id
        ).first()
        
        if not session:
            return {"success": False, "message": f"Session {session_id} not found"}
        
        try:
            commands = json.loads(session.commands)
        except (json.JSONDecodeError, TypeError):
            commands = []
        
        if not commands:
            return {"success": False, "message": "No commands in session"}
        
        session_file = save_real_session(session_id, commands, session.ip_address)
        auto_labeled = auto_label_session(session_id, confidence_threshold=0.70)
        
        result = {
            "success": True,
            "session_id": session_id,
            "commands_count": len(commands),
            "session_file": session_file,
            "auto_labeled": auto_labeled,
        }
        
        if auto_retrain:
            real_count = len(load_real_sessions(labeled_only=True))
            if real_count >= 10 and real_count % 10 == 0:
                retrain_result = retrain_with_real_sessions()
                if retrain_result:
                    result["retrained"] = True
                    result["model_path"] = retrain_result["model_path"]
        
        return result
    finally:
        db.close()
