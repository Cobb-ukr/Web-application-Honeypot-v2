import re
import math
import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import os
import logging
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Signatures for Rule-Based Detection
SQLI_PATTERNS = [
    r"(?i)(\%27)|(\')|(\-\-)|(\%23)|(#)",
    r"(?i)((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
    r"(?i)\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
    r"(?i)((\%27)|(\'))union",
    r"(?i)exec(\s|\+)+(s|x)p\w+",
    r"(?i)select\s+.*\s+from",
    r"(?i)or\s+1\s*=\s*1"
]

XSS_PATTERNS = [
    r"(?i)<script>",
    r"(?i)javascript:",
    r"(?i)onload\s*=",
    r"(?i)onerror\s*=",
    r"(?i)<img\s+src",
    r"(?i)alert\(",
]

CMD_PATTERNS = [
    r"(?i)cmd\.exe",
    r"(?i)/bin/sh",
    r"(?i)/bin/bash",
    r"(?i)\s+;\s+",
    r"(?i)\s+\|\s+",
    r"(?i)\s+&&\s+"
]

TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\"
]

class AIEngine:
    def __init__(self):
        self.model = None
        # Get the models directory
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(self.base_dir, "models")
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.model_version = self._get_latest_model_version()
        self._load_or_train_model()

    def _get_latest_model_version(self):
        """Get the latest model version number from the models directory."""
        if not os.path.exists(self.models_dir):
            return 0
        
        model_files = [f for f in os.listdir(self.models_dir) if f.startswith("model_v") and f.endswith(".pkl")]
        if not model_files:
            return 0
        
        # Extract version numbers and return the highest
        versions = []
        for f in model_files:
            try:
                version = int(f.replace("model_v", "").replace(".pkl", ""))
                versions.append(version)
            except ValueError:
                continue
        
        return max(versions) if versions else 0

    def _get_model_path(self, version=None):
        """Get the full path for a model file."""
        if version is None:
            version = self.model_version
        return os.path.join(self.models_dir, f"model_v{version}.pkl")

    def _calculate_entropy(self, text):
        if not text:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(text.count(chr(x))) / len(text)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy

    def extract_features(self, payload):
        if not payload:
            return [0, 0, 0, 0]
        
        length = len(payload)
        entropy = self._calculate_entropy(payload)
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', payload))
        keywords = len(re.findall(r'(select|union|insert|delete|update|script|alert|etc|passwd)', payload, re.IGNORECASE))
        
        return [length, entropy, special_chars, keywords] # Feature vector

    def _load_or_train_model(self):
        # In a real scenario, this would load a pretrained model.
        # For this project, we'll train a simple one on initialization if not exists.
        model_path = self._get_model_path()
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                logger.info(f"Loaded model version {self.model_version} from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model v{self.model_version}: {e}. Training new model.")
                self._train_dummy_model()
        else:
            self._train_dummy_model()
            
        self._load_signatures()

    def _load_signatures(self):
        from backend.database import SessionLocal, AttackSignature
        db = SessionLocal()
        signatures = db.query(AttackSignature).all()
        self.db_signatures = signatures
        db.close()

    def _train_dummy_model(self):
        # 0 = Safe, 1 = Malicious
        X = [
            [5, 1.5, 0, 0], [10, 2.0, 1, 0], [4, 1.0, 0, 0], # Normal
            [50, 4.5, 10, 2], [100, 5.0, 20, 5], [30, 3.8, 5, 1] # Malicious
        ]
        y = [0, 0, 0, 1, 1, 1]
        self.model = RandomForestClassifier(n_estimators=10)
        self.model.fit(X, y)
        logger.info("Trained dummy model with baseline data")

    def retrain_on_historical_data(self, retrain_mode="all"):
        """
        Retrain the model on historical attack data from the database.
        
        Args:
            retrain_mode: "all" to retrain on all data, "recent" for last 7 days, "skip" to skip retraining
        
        Returns:
            dict: Contains 'success' (bool), 'message' (str), 'samples' (int), 'version' (int)
        """
        if retrain_mode == "skip":
            logger.info("Model retraining skipped.")
            return {
                "success": False,
                "message": "Retraining skipped. Using existing model.",
                "samples": 0,
                "version": self.model_version
            }
        
        try:
            from backend.database import SessionLocal, AttackLog
            db = SessionLocal()
            
            # Query attack logs, excluding "Failed Login" entries
            query = db.query(AttackLog).filter(
                AttackLog.attack_type != "Failed Login"
            ).filter(
                AttackLog.attack_type != "Successful Login"
            )
            
            # Filter by time if recent mode
            if retrain_mode == "recent":
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                query = query.filter(AttackLog.timestamp >= seven_days_ago)
                logger.info("Retraining on data from last 7 days")
            elif retrain_mode == "all":
                logger.info("Retraining on all historical attack data")
            
            logs = query.all()
            
            if len(logs) < 5:
                message = f"Insufficient training data: only {len(logs)} attack logs found. Using dummy model."
                logger.warning(message)
                db.close()
                return {
                    "success": False,
                    "message": message,
                    "samples": 0,
                    "version": self.model_version
                }
            
            X, y = [], []
            
            for log in logs:
                try:
                    # Extract username from payload
                    payload_data = json.loads(log.payload)
                    payload = payload_data.get('username', '')
                    
                    if not payload:
                        continue
                    
                    # Extract features
                    features = self.extract_features(payload)
                    X.append(features)
                    
                    # Label: 1 if it's an actual attack, 0 if clean
                    # Only attack types like SQLi, XSS, CommandInjection, etc. are malicious
                    is_malicious = log.attack_type in ["SQLi", "XSS", "CommandInjection", "PathTraversal", "Anomaly"]
                    y.append(1 if is_malicious else 0)
                    
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.debug(f"Skipping log entry due to parsing error: {e}")
                    continue
            
            if len(X) < 5:
                message = f"Insufficient parsed training data: only {len(X)} samples. Using dummy model."
                logger.warning(message)
                db.close()
                return {
                    "success": False,
                    "message": message,
                    "samples": 0,
                    "version": self.model_version
                }
            
            # Train the model on historical data
            self.model = RandomForestClassifier(n_estimators=10, random_state=42)
            self.model.fit(X, y)
            
            # Increment version and save
            self.model_version += 1
            model_path = self._get_model_path()
            joblib.dump(self.model, model_path)
            
            message = f"Successfully retrained model on {len(X)} samples. Saved as model_v{self.model_version}"
            logger.info(message)
            db.close()
            return {
                "success": True,
                "message": message,
                "samples": len(X),
                "version": self.model_version
            }
            
        except Exception as e:
            message = f"Error during model retraining: {e}. Keeping current model."
            logger.error(message)
            return {
                "success": False,
                "message": message,
                "samples": 0,
                "version": self.model_version
            }

    def analyze_payload(self, payload):
        """
        Returns a dict with detection results.
        """
        if not payload:
            return {"score": 0, "type": "clean", "details": "Empty payload"}

        # 1. Rule Based
        for p in SQLI_PATTERNS:
            if re.search(p, payload):
                return {"score": 0.9, "type": "SQLi", "details": f"Matched pattern: {p}"}
        
        for p in XSS_PATTERNS:
            if re.search(p, payload):
                return {"score": 0.8, "type": "XSS", "details": f"Matched pattern: {p}"}
                
        for p in CMD_PATTERNS:
            if re.search(p, payload):
                return {"score": 1.0, "type": "CommandInjection", "details": f"Matched pattern: {p}"}

        for p in TRAVERSAL_PATTERNS:
            if re.search(p, payload):
                return {"score": 0.8, "type": "PathTraversal", "details": f"Matched pattern: {p}"}

        # 1.1 DB Based Signatures (Dynamic)
        if hasattr(self, 'db_signatures'):
            for sig in self.db_signatures:
                if re.search(sig.pattern, payload):
                    # Assign score based on type
                    score = 0.9 if sig.type in ["SQLi", "CommandInjection"] else 0.8
                    return {"score": score, "type": sig.type, "details": f"Matched DB Pattern: {sig.description}"}

        # 2. ML/Heuristic Based
        features = self.extract_features(payload)
        prediction = self.model.predict([features])[0]
        
        # Handle predict_proba returning different shapes depending on training data
        proba = self.model.predict_proba([features])[0]
        
        # If model was trained with only one class, proba will have length 1
        if len(proba) == 1:
            # Only one class in training - assume it's the clean class, so malicious prob = 0
            prob = 0.0
        else:
            # Normal case: two classes, get probability of malicious class (class 1)
            prob = proba[1] if prediction == 1 else proba[0]

        if prediction == 1 and prob > 0.75:
            return {"score": float(prob), "type": "Anomaly", "details": f"ML detected high entropy/keywords. Prob: {prob:.2f}"}

        return {"score": 0, "type": "clean", "details": "No threats detected"}

ai_engine = AIEngine()
