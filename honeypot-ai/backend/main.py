from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from backend.database import init_db
from backend.auth import router as auth_router
from backend.honeypot import router as honeypot_router
from backend.admin import router as admin_router
import os

app = FastAPI(title="Adaptive Honeypot System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()
    seed_signatures()

def seed_signatures():
    from backend.database import SessionLocal, AttackSignature
    db = SessionLocal()
    # Default patterns
    defaults = [
        {"pattern": r"(?i)(\%27)|(\')|(\-\-)|(\%23)|(#)", "type": "SQLi", "description": "Generic SQL Comment"},
        {"pattern": r"(?i)((\%27)|(\'))union", "type": "SQLi", "description": "SQL Union Attack"},
        {"pattern": r"(?i)or\s+1\s*=\s*1", "type": "SQLi", "description": "SQL Tautology"},
        {"pattern": r"(?i)<script>", "type": "XSS", "description": "Script Tag"},
        {"pattern": r"(?i)alert\(", "type": "XSS", "description": "Alert Function"},
        {"pattern": r"(?i)cmd\.exe", "type": "CommandInjection", "description": "Windows Command Shell"},
        {"pattern": r"(?i)/bin/sh", "type": "CommandInjection", "description": "Linux Shell"},
    ]
    
    for item in defaults:
        exists = db.query(AttackSignature).filter(AttackSignature.pattern == item["pattern"]).first()
        if not exists:
            db.add(AttackSignature(**item))
    db.commit()
    db.close()

# Mount Routes
app.include_router(auth_router)
app.include_router(honeypot_router, prefix="/honeypot")
app.include_router(admin_router, prefix="/api")

# Mount Frontend (Static Files)
# We serve the frontend folder as static.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/login.html")
