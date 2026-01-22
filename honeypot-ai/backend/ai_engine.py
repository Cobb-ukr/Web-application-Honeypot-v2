import re
import math
import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import os

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
        self.model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        self._load_or_train_model()

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
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
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
        # joblib.dump(self.model, self.model_path) # Optional: save

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
        prob = self.model.predict_proba([features])[0][1] # Probability of being malicious

        if prediction == 1 and prob > 0.75:
            return {"score": float(prob), "type": "Anomaly", "details": f"ML detected high entropy/keywords. Prob: {prob:.2f}"}

        return {"score": 0, "type": "clean", "details": "No threats detected"}

ai_engine = AIEngine()
