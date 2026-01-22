from sqlalchemy.orm import Session
from backend.database import ThreatScore, BlockedIP, AttackLog, SessionLocal
from datetime import datetime
import logging

class ThreatScorer:
    def __init__(self):
        self.threshold_block = 5.0  # Score to soft-block/redirect to honeypot permanently
        self.threshold_alert = 3.0

    def update_score(self, db: Session, ip: str, attack_score: float, attack_type: str):
        # Get existing score
        threat_entry = db.query(ThreatScore).filter(ThreatScore.ip_address == ip).first()
        
        if not threat_entry:
            threat_entry = ThreatScore(ip_address=ip, score=0.0)
            db.add(threat_entry)
        
        # Logic: Accumulate score
        # SQLi/Cmd are high impact (add full score)
        # Anomaly is medium impact
        if attack_score > 0:
            threat_entry.score += attack_score
            threat_entry.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(threat_entry)
            
            return threat_entry.score
        return threat_entry.score if threat_entry else 0

    def should_redirect(self, db: Session, ip: str) -> bool:
        threat_entry = db.query(ThreatScore).filter(ThreatScore.ip_address == ip).first()
        if threat_entry and threat_entry.score >= self.threshold_alert:
            return True
        # Also check if IP is explicitly blocked
        blocked = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        if blocked:
            return True
        return False

    def get_risk_level(self, score):
        if score < 3:
            return "Low"
        elif score < 5:
            return "Medium"
        else:
            return "High"

scorer = ThreatScorer()
