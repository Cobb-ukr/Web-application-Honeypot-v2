from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from backend.database import SessionLocal, User, AttackLog, BlockedIP, ThreatScore
from backend.ai_engine import ai_engine
from backend.threat_scoring import scorer
from datetime import datetime
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    ip = request.client.host

    # Analyze only the username to avoid password-based false positives
    payload = username

    # 1. AI Analysis on username
    analysis = ai_engine.analyze_payload(payload)
    is_malicious = analysis['score'] > 0.7

    # Determine Result
    status_type = "clean"
    user = db.query(User).filter(User.username == username).first()

    if is_malicious:
        status_type = analysis['type']  # SQLi, XSS, etc.
        # Update score for malicious input
        current_score = scorer.update_score(db, ip, analysis['score'], analysis['type'])
    elif not user or user.password_hash != password:
        status_type = "Failed Login"
        # Increment threat score for failed attempts
        current_score = scorer.update_score(db, ip, 1.0, "Failed Login")
    else:
        status_type = "Successful Login"
        # Reset threat score on successful login (legitimate user got in)
        threat_entry = db.query(ThreatScore).filter(ThreatScore.ip_address == ip).first()
        if threat_entry:
            threat_entry.score = 0.0
            threat_entry.last_updated = datetime.utcnow()
            db.commit()
            current_score = 0.0
        else:
            current_score = 0.0

    # 2. Log the attempt
    log_payload = json.dumps({
        "username": username,
        "password": password,
        "full_payload": payload if is_malicious else "HIDDEN"
    })

    log_entry = AttackLog(
        ip_address=ip,
        timestamp=datetime.utcnow(),
        payload=log_payload,
        attack_type=status_type,
        threat_score=current_score,
        user_agent=request.headers.get("user-agent"),
        endpoint="/auth/login",
        method="POST",
        headers=json.dumps(dict(request.headers))
    )
    db.add(log_entry)
    db.commit()

    # Decide redirection
    blocked = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
    should_trap = scorer.should_redirect(db, ip) or is_malicious

    # Blocked IPs always go to honeypot
    if blocked:
        return JSONResponse(content={"token": "fake-jwt-token-honeypot", "redirect": "/internal/dashboard", "message": "Login Successful"}, status_code=200)

    # Legitimate success should never be trapped
    if status_type == "Successful Login":
        redirect_url = "/static/welcome.html"
        if user.role == "admin":
            redirect_url = "/static/dashboard.html"
        return JSONResponse(content={"token": f"real-jwt-token-{user.role}", "redirect": redirect_url, "message": "Login Successful"}, status_code=200)

    # Malicious or flagged IPs go to honeypot
    if should_trap:
        return JSONResponse(content={"token": "fake-jwt-token-honeypot", "redirect": "/internal/dashboard", "message": "Login Successful"}, status_code=200)

    # Normal failed login: 401 (frontend will show error and stay on login)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/auth/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Basic registration for setup
    try:
        user = User(username=username, password_hash=password, role="user")
        db.add(user)
        db.commit()
        return {"message": "User registered"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
