from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from backend.database import SessionLocal, AttackLog
from backend.ai_engine import ai_engine
from datetime import datetime
import json
import os
import random

router = APIRouter()

def log_honeypot_action(request: Request, action: str, details: str = ""):
    db = SessionLocal()
    # Log every move the attacker makes in the honeypot
    log = AttackLog(
        ip_address=request.client.host,
        timestamp=datetime.utcnow(),
        payload=str(request.query_params) + str(details),
        attack_type="Honeypot Interaction",
        threat_score=0.0, # Already caught, but could track intensity
        user_agent=request.headers.get("user-agent"),
        endpoint=str(request.url),
        method=request.method,
        headers=json.dumps(dict(request.headers))
    )
    db.add(log)
    db.commit()
    db.close()

@router.get("/dashboard", response_class=HTMLResponse)
async def fake_dashboard(request: Request):
    log_honeypot_action(request, "Viewed Fake Dashboard")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UI_PATH = os.path.join(BASE_DIR, "frontend", "honeypot_ui.html")
    with open(UI_PATH, "r") as f:
        content = f.read()
    return content

@router.get("/files")
async def fake_files(request: Request):
    log_honeypot_action(request, "Listed Fake Files")
    # Generate fake file list
    return {
        "files": [
            {"name": "passwords.txt", "size": "1.2KB", "type": "text"},
            {"name": "financial_report_2024.pdf", "size": "4.5MB", "type": "pdf"},
            {"name": "admin_backup.sql", "size": "120MB", "type": "sql"},
            {"name": "private_key.pem", "size": "2KB", "type": "key"}
        ]
    }

@router.get("/files/{filename}")
async def fake_file_content(request: Request, filename: str):
    log_honeypot_action(request, f"Downloaded Fake File: {filename}")
    # Return empty content as requested
    return ""

@router.post("/execute")
async def fake_terminal(request: Request):
    body = await request.body()
    log_honeypot_action(request, "Executed Command in Fake Terminal", details=str(body))
    return {"status": "success", "output": "Command executed successfully (simulated)."}
