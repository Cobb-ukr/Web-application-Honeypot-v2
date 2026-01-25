from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal, AttackLog, ThreatScore, BlockedIP, HoneypotSession

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

@router.post("/admin/clear_logs")
async def clear_logs(db: Session = Depends(get_db)):
    try:
        log_count = db.query(AttackLog).count()
        threat_count = db.query(ThreatScore).filter(ThreatScore.score > 0).count()
        session_count = db.query(HoneypotSession).count()
        
        db.query(AttackLog).delete(synchronize_session=False)
        db.query(ThreatScore).delete(synchronize_session=False)
        db.query(HoneypotSession).delete(synchronize_session=False)
        db.commit()
        
        return {"message": f"Successfully deleted {log_count} attack logs, reset {threat_count} threat scores, and cleared {session_count} honeypot sessions"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@router.get("/admin/stats")
async def get_stats(db: Session = Depends(get_db)):
    # Counter Logic:
    # Login = "Successful Login"
    # Attack = Everything else that is NOT "Successful Login" AND NOT "clean"
    
    total_logins = db.query(AttackLog).filter(AttackLog.attack_type == "Successful Login").count()
    
    # Attacks include Failed Login, SQLi, XSS, etc. (not honeypot sessions)
    total_attacks = db.query(AttackLog).filter(AttackLog.attack_type != "Successful Login", AttackLog.attack_type != "clean").count()
    
    # Count active honeypot sessions
    honeypot_sessions = db.query(HoneypotSession).filter(HoneypotSession.is_active == True).count()
    total_attacks += honeypot_sessions  # Include honeypot sessions in attack count
    
    active_threats = db.query(ThreatScore).filter(ThreatScore.score > 0).count()
    
    # Group by logic
    attack_types = db.query(AttackLog.attack_type, func.count(AttackLog.attack_type)).group_by(AttackLog.attack_type).all()
    
    recent_logs = []
    
    # Get recent attack logs
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
    
    # Get recent honeypot sessions
    sessions_query = db.query(HoneypotSession).order_by(HoneypotSession.start_time.desc()).limit(50).all()
    
    for session in sessions_query:
        try:
            commands = json.loads(session.commands)
        except:
            commands = []
        
        num_commands = len(commands)
        iso_time = session.start_time.isoformat() + 'Z' if session.start_time else ""
        
        recent_logs.append({
            "id": session.id,
            "ip": session.ip_address,
            "type": "Honeypot Session",
            "username": "-",
            "password": "-",
            "attack_detail": f"Session with {num_commands} commands",
            "time": iso_time,
            "time_formatted": session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else "N/A",
            "is_session": True,
            "session_id": session.session_id,
            "num_commands": num_commands
        })
    
    # Sort all logs by timestamp (most recent first)
    recent_logs.sort(key=lambda x: x["time"], reverse=True)
    recent_logs = recent_logs[:100]  # Limit to 100 total

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

@router.get("/admin/honeypot_session/{session_id}")
async def get_honeypot_session_details(session_id: str, db: Session = Depends(get_db)):
    session = db.query(HoneypotSession).filter(
        HoneypotSession.session_id == session_id
    ).first()
    
    if not session:
        return {"error": "Session not found"}
    
    import json
    
    try:
        commands = json.loads(session.commands)
    except:
        commands = []
    
    try:
        headers = json.loads(session.headers) if session.headers else {}
    except:
        headers = {}
    
    iso_start = session.start_time.isoformat() + 'Z' if session.start_time else ""
    iso_end = session.end_time.isoformat() + 'Z' if session.end_time else ""
    
    duration_seconds = 0
    if session.start_time and session.end_time:
        duration_seconds = int((session.end_time - session.start_time).total_seconds())
    
    return {
        "session_id": session.session_id,
        "ip_address": session.ip_address,
        "start_time": iso_start,
        "end_time": iso_end,
        "start_time_formatted": session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else "N/A",
        "end_time_formatted": session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else "Still Active",
        "is_active": session.is_active,
        "duration_seconds": duration_seconds,
        "user_agent": session.user_agent,
        "headers": headers,
        "commands": commands,
        "num_commands": len(commands)
    }

