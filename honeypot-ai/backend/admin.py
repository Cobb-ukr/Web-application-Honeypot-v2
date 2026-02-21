from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal, AttackLog, ThreatScore, BlockedIP, HoneypotSession
from backend.threat_scoring import scorer
import requests
import re

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

@router.get("/admin/active_threats")
async def list_active_threats(db: Session = Depends(get_db)):
    threats = (
        db.query(ThreatScore)
        .filter(ThreatScore.score > 0)
        .order_by(ThreatScore.score.desc())
        .all()
    )

    results = []
    for entry in threats:
        iso_time = entry.last_updated.isoformat() + 'Z' if entry.last_updated else ""
        results.append({
            "ip": entry.ip_address,
            "score": entry.score,
            "risk": scorer.get_risk_level(entry.score),
            "last_updated": iso_time,
        })

    return {"active_threats": results}

@router.delete("/admin/threat/{ip_address}")
async def delete_threat(ip_address: str, db: Session = Depends(get_db)):
    threat = db.query(ThreatScore).filter(ThreatScore.ip_address == ip_address).first()
    if not threat:
        return {"error": "Threat not found"}

    db.delete(threat)
    db.commit()
    return {"message": f"Threat score for {ip_address} deleted"}

@router.get("/admin/stats")
async def get_stats(db: Session = Depends(get_db)):
    # Counter Logic:
    # Login = "Successful Login"
    # Attack = Only malicious attempts and 3-strike failed logins (NOT regular failed logins)
    
    total_logins = db.query(AttackLog).filter(AttackLog.attack_type == "Successful Login").count()
    
    # Attacks include SQLi, XSS, 3-strike failed logins, etc.
    # Exclude: "Successful Login", "clean", and regular "Failed Login"
    total_attacks = db.query(AttackLog).filter(
        AttackLog.attack_type != "Successful Login", 
        AttackLog.attack_type != "clean",
        AttackLog.attack_type != "Failed Login"
    ).count()
    
    # Count active honeypot sessions
    honeypot_sessions = db.query(HoneypotSession).filter(HoneypotSession.is_active == True).count()
    total_attacks += honeypot_sessions  # Include honeypot sessions in attack count
    
    active_threats = db.query(ThreatScore).filter(ThreatScore.score > 0).count()
    
    # Group by logic
    attack_types = db.query(AttackLog.attack_type, func.count(AttackLog.attack_type)).group_by(AttackLog.attack_type).all()
    blocked_ips = set(
        ip for (ip,) in db.query(BlockedIP.ip_address).all()
    )
    
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
            "time_formatted": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A",
            "is_blocked": log.ip_address in blocked_ips
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

    blocked = db.query(BlockedIP).filter(BlockedIP.ip_address == log.ip_address).first()
    
    iso_time = log.timestamp.isoformat() + 'Z' if log.timestamp else ""

    # Try to find a related honeypot session for this IP
    session = None
    if log.timestamp:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.ip_address == log.ip_address,
            HoneypotSession.start_time >= log.timestamp
        ).order_by(HoneypotSession.start_time.asc()).first()

    if not session:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.ip_address == log.ip_address
        ).order_by(HoneypotSession.start_time.desc()).first()

    session_summary = None
    if session:
        try:
            session_commands = json.loads(session.commands)
        except:
            session_commands = []

        session_summary = {
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat() + 'Z' if session.start_time else "",
            "start_time_formatted": session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else "N/A",
            "num_commands": len(session_commands),
            "is_active": session.is_active
        }

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
        "threat_score": log.threat_score,
        "is_blocked": True if blocked else False,
        "honeypot_session": session_summary
    }

@router.delete("/admin/log/{log_id}")
async def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AttackLog).filter(AttackLog.id == log_id).first()
    if not log:
        return {"error": "Log not found"}

    db.delete(log)
    db.commit()
    return {"message": f"Log {log_id} deleted"}

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

@router.post("/admin/test_email")
async def test_email_configuration():
    """Test email configuration and send a test alert"""
    from backend.email_service import email_service
    from datetime import datetime
    
    # Test SMTP connection first
    success, message = email_service.test_connection()
    
    if not success:
        return {"success": False, "message": message}
    
    # Send test email
    test_session_data = {
        'ip_address': '192.168.1.100',
        'session_id': 'test-session-12345',
        'timestamp': datetime.utcnow(),
        'user_agent': 'Mozilla/5.0 (Test Browser)',
        'location': 'Test Location'
    }
    
    email_sent = email_service.send_honeypot_alert(test_session_data)
    
    if email_sent:
        return {
            "success": True,
            "message": "Test email sent successfully! Check your inbox."
        }
    else:
        return {
            "success": False,
            "message": "Failed to send test email. Check server logs for details."
        }

@router.get("/admin/geolocation/{ip_address}")
async def get_geolocation(ip_address: str):
    """Proxy geolocation requests to avoid CORS issues"""
    
    # Validate IP address format
    def is_private_ip(ip):
        if not ip or ip in ['127.0.0.1', 'localhost', '::1', '0.0.0.0']:
            return True
        if ip.startswith(('192.168.', '10.', 'fe80:', 'fd', '127.')):
            return True
        if re.match(r'^172\.(1[6-9]|2\d|3[01])\.', ip):
            return True
        return False
    
    if is_private_ip(ip_address):
        return {
            "success": False,
            "message": "Geolocation not applicable for private/local IPs"
        }
    
    # Try multiple geolocation services
    try:
        # Try ip-api.com first (free, no key required, 45 req/min)
        response = requests.get(
            f"https://ip-api.com/json/{ip_address}?fields=status,country,regionName,city,timezone,isp,org,as,lat,lon",
            timeout=5
        )
        data = response.json()
        
        if data.get('status') == 'success':
            return {
                "success": True,
                "country": data.get('country'),
                "regionName": data.get('regionName'),
                "city": data.get('city'),
                "timezone": data.get('timezone'),
                "isp": data.get('isp'),
                "org": data.get('org'),
                "lat": data.get('lat'),
                "lon": data.get('lon'),
                "as": data.get('as')
            }
    except Exception as e:
        print(f"ip-api.com failed: {e}")
    
    # Fallback to ipwhois.app (free, 10k req/month)
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip_address}", timeout=5)
        data = response.json()
        
        if data.get('success'):
            return {
                "success": True,
                "country": data.get('country'),
                "regionName": data.get('region'),
                "city": data.get('city'),
                "timezone": data.get('timezone'),
                "isp": data.get('org'),
                "org": data.get('org'),
                "lat": data.get('latitude'),
                "lon": data.get('longitude'),
                "as": data.get('asn')
            }
    except Exception as e:
        print(f"ipwhois.app failed: {e}")
    
    # Last fallback: ipapi.co (1000 req/day free)
    try:
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        data = response.json()
        
        if 'error' not in data:
            return {
                "success": True,
                "country": data.get('country_name'),
                "regionName": data.get('region'),
                "city": data.get('city'),
                "timezone": data.get('timezone'),
                "isp": data.get('org'),
                "org": data.get('org'),
                "lat": data.get('latitude'),
                "lon": data.get('longitude'),
                "as": data.get('asn')
            }
    except Exception as e:
        print(f"ipapi.co failed: {e}")
    
    return {
        "success": False,
        "message": "All geolocation services failed or rate limited"
    }


@router.post("/admin/add_session_to_training")
async def add_session_to_training(data: dict, db: Session = Depends(get_db)):
    """Add a honeypot session to the training dataset with optional custom labels"""
    session_id = data.get("session_id")
    custom_intent = data.get("intent")  # Optional manual label
    custom_skill = data.get("skill")    # Optional manual label
    
    if not session_id:
        return {"success": False, "message": "session_id required"}
    
    try:
        from attacker_profiler.incremental_trainer import save_real_session
        from attacker_profiler.step5_infer import AttackerProfiler
        import json
        
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
            return {"success": False, "message": "Session has no commands"}
        
        # Save session file
        session_file = save_real_session(session_id, commands, session.ip_address)
        
        # Load the saved session and update labels
        with open(session_file, "r") as f:
            session_data = json.load(f)
        
        # Use custom labels if provided, otherwise auto-label
        if custom_intent and custom_skill:
            session_data["intent"] = custom_intent
            session_data["skill"] = custom_skill
            session_data["labeled"] = True
            session_data["manual_label"] = True
        else:
            # Auto-label using current model
            try:
                profiler = AttackerProfiler()
                result = profiler.analyze_session(commands)
                session_data["intent"] = result["intent"]
                session_data["skill"] = result["skill"]
                session_data["labeled"] = True
                session_data["auto_labeled"] = True
                session_data["confidence"] = result["confidence"]
            except Exception as e:
                return {"success": False, "message": f"Auto-labeling failed: {e}"}
        
        # Save updated session
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        
        return {
            "success": True,
            "message": "Session added to training dataset",
            "session_id": session_id,
            "intent": session_data["intent"],
            "skill": session_data["skill"],
            "commands_count": len(commands)
        }
    
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


@router.post("/admin/retrain_model")
async def retrain_model(data: dict):
    """Retrain the model with all labeled sessions"""
    num_synthetic = data.get("num_synthetic", 100)
    min_real = data.get("min_real", 5)
    
    try:
        from attacker_profiler.incremental_trainer import retrain_with_real_sessions, load_real_sessions
        
        real_sessions = load_real_sessions(labeled_only=True)
        
        if len(real_sessions) < min_real:
            return {
                "success": False,
                "message": f"Insufficient labeled sessions: {len(real_sessions)} (need {min_real})"
            }
        
        result = retrain_with_real_sessions(
            num_synthetic=num_synthetic,
            confidence_threshold=0.70,
            min_real_sessions=min_real
        )
        
        if result:
            return {
                "success": True,
                "message": "Model retrained successfully",
                "model_path": result["model_path"],
                "metrics": result["metrics"],
                "real_sessions": result["real_sessions"],
                "synthetic_sessions": result["synthetic_sessions"]
            }
        else:
            return {"success": False, "message": "Retraining failed"}
    
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


@router.get("/admin/training_stats")
async def get_training_stats():
    """Get statistics about the training dataset"""
    try:
        from attacker_profiler.incremental_trainer import load_real_sessions
        import os
        
        all_sessions = load_real_sessions(labeled_only=False)
        labeled_sessions = load_real_sessions(labeled_only=True)
        
        intent_counts = {}
        skill_counts = {}
        
        for session in labeled_sessions:
            intent = session.get("intent", "Unknown")
            skill = session.get("skill", "Unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Load training log
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "attacker_profiler",
            "training_log.json"
        )
        
        training_history = []
        if os.path.exists(log_path):
            import json
            with open(log_path, "r") as f:
                try:
                    training_history = json.load(f)
                except json.JSONDecodeError:
                    training_history = []
        
        return {
            "total_sessions": len(all_sessions),
            "labeled_sessions": len(labeled_sessions),
            "unlabeled_sessions": len(all_sessions) - len(labeled_sessions),
            "intent_distribution": intent_counts,
            "skill_distribution": skill_counts,
            "training_history": training_history[-5:] if training_history else []  # Last 5 trainings
        }
    
    except Exception as e:
        return {"error": str(e)}
