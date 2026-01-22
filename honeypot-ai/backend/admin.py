from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal, AttackLog, ThreatScore, BlockedIP

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/admin/block_ip")
async def block_ip(ip_dict: dict, db: Session = Depends(get_db)):
    ip = ip_dict.get("ip")
    if not ip: return {"error": "No IP provided"}
    
    exists = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
    if not exists:
        blocked = BlockedIP(ip_address=ip, reason="Manual Block by Admin")
        db.add(blocked)
        db.commit()
    return {"message": f"IP {ip} blocked successfully"}

@router.post("/admin/unblock_ip")
async def unblock_ip(ip_dict: dict, db: Session = Depends(get_db)):
    ip = ip_dict.get("ip")
    if not ip: return {"error": "No IP provided"}
    
    blocked = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
    if blocked:
        db.delete(blocked)
        db.commit()
        return {"message": f"IP {ip} unblocked successfully"}
    return {"message": f"IP {ip} was not blocked"}

@router.get("/admin/stats")
async def get_stats(db: Session = Depends(get_db)):
    # Counter Logic:
    # Login = "Successful Login"
    # Attack = Everything else that is NOT "Successful Login" AND NOT "clean" (though clean usually implies success/fail logic handled above)
    
    total_logins = db.query(AttackLog).filter(AttackLog.attack_type == "Successful Login").count()
    
    # Attacks include Failed Login, SQLi, XSS, etc.
    total_attacks = db.query(AttackLog).filter(AttackLog.attack_type != "Successful Login", AttackLog.attack_type != "clean").count()
    
    active_threats = db.query(ThreatScore).filter(ThreatScore.score > 0).count()
    
    # Group by logic
    attack_types = db.query(AttackLog.attack_type, func.count(AttackLog.attack_type)).group_by(AttackLog.attack_type).all()
    
    recent_logs = []
    logs_query = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).limit(100).all()
    
    import json
    from datetime import datetime, timezone
    
    for log in logs_query:
        username = "-"
        password = "-"
        attack_detail = "-"
        
        try:
            if log.payload.startswith("{"):
                data = json.loads(log.payload)
                username = data.get("username", "-")
                password = data.get("password", "-")
                if "full_payload" in data and data["full_payload"] != "HIDDEN":
                     attack_detail = data["full_payload"]
            else:
                attack_detail = log.payload
        except:
            attack_detail = log.payload

        # Format timestamp as ISO 8601 for proper JavaScript parsing
        # Add 'Z' suffix to indicate UTC time so JavaScript converts to local timezone
        iso_time = log.timestamp.isoformat() + 'Z' if log.timestamp else ""
        
        recent_logs.append({
            "id": log.id,
            "ip": log.ip_address,
            "type": log.attack_type,
            "username": username,
            "password": password,
            "attack_detail": attack_detail,
            "time": iso_time,
            "time_formatted": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A"
        })

    return {
        "total_logins": total_logins,
        "total_attacks": total_attacks,
        "active_threats": active_threats,
        "attack_distribution": {type_: count for type_, count in attack_types},
        "recent_logs": recent_logs
    }

@router.get("/admin/log/{log_id}")
async def get_log_details(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AttackLog).filter(AttackLog.id == log_id).first()
    
    if not log:
        return {"error": "Log not found"}
    
    import json
    username = "-"
    password = "-"
    attack_detail = "-"
    
    try:
        if log.payload.startswith("{"):
            data = json.loads(log.payload)
            username = data.get("username", "-")
            password = data.get("password", "-")
            if "full_payload" in data and data["full_payload"] != "HIDDEN":
                attack_detail = data["full_payload"]
        else:
            attack_detail = log.payload
    except:
        attack_detail = log.payload
    
    # Parse headers
    try:
        headers = json.loads(log.headers) if log.headers else {}
    except:
        headers = {}
    
    iso_time = log.timestamp.isoformat() + 'Z' if log.timestamp else ""
    
    return {
        "id": log.id,
        "ip": log.ip_address,
        "type": log.attack_type,
        "username": username,
        "password": password,
        "attack_detail": attack_detail,
        "time": iso_time,
        "time_formatted": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A",
        "user_agent": log.user_agent,
        "endpoint": log.endpoint,
        "method": log.method,
        "headers": headers,
        "threat_score": log.threat_score
    }

