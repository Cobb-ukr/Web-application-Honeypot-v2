from dotenv import load_dotenv
import os
import logging

# Load environment variables FIRST, before any other imports
# Get the project root directory (parent of backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

# Now import everything else AFTER env vars are loaded
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from backend.database import init_db
from backend.auth import router as auth_router
from backend.honeypot import router as honeypot_router
from backend.admin import router as admin_router
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
env_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(env_path)
print(f"Loading .env from: {env_path}")
print(f"GROQ_API_KEY loaded: {bool(os.getenv('GROQ_API_KEY'))}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Check if env vars are loaded
logger.info(f"Loading .env from: {ENV_PATH}")
logger.info(f"SMTP_USERNAME loaded: {os.getenv('SMTP_USERNAME', 'NOT_FOUND')}")
logger.info(f"SMTP_PASSWORD loaded: {'***' if os.getenv('SMTP_PASSWORD') else 'NOT_FOUND'}")

app = FastAPI(title="Adaptive Honeypot System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Parse environment variable for retraining mode
def get_retrain_mode():
    """Extract RETRAIN_MODE environment variable."""
    retrain_mode = os.getenv("RETRAIN_MODE", "skip").lower()  # Default: skip retraining
    
    if retrain_mode not in ["all", "recent", "skip"]:
        logger.warning(f"Invalid retrain mode: {retrain_mode}. Valid options: all, recent, skip. Using 'skip'.")
        retrain_mode = "skip"
    
    return retrain_mode

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()
    seed_signatures()
    retrain_ai_model()

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

def retrain_ai_model():
    """Retrain the AI model based on environment variable and log results."""
    from datetime import datetime
    
    retrain_mode = get_retrain_mode()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    
    # Ensure logs directory exists
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, "model_log.txt")
    
    # Prepare log content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines = [
        "=" * 70,
        f"MODEL RETRAINING LOG - {timestamp}",
        "=" * 70,
        "",
        f"Retraining Mode: {retrain_mode.upper()}",
        ""
    ]
    
    logger.info(f"Retraining mode: {retrain_mode}")
    
    try:
        from backend.ai_engine import ai_engine
        result = ai_engine.retrain_on_historical_data(retrain_mode=retrain_mode)
        
        # Log the result
        log_lines.append(f"Status: {'SUCCESS' if result['success'] else 'INFO'}")
        log_lines.append(f"Message: {result['message']}")
        log_lines.append(f"Samples Used: {result['samples']}")
        log_lines.append(f"Model Version: v{result['version']}")
        log_lines.append("")
        
        if result['success']:
            logger.info(f"Model retraining completed successfully. {result['message']}")
        else:
            logger.info(f"Model retraining result: {result['message']}")
            
    except Exception as e:
        error_msg = f"Error during model retraining: {e}"
        logger.error(error_msg)
        log_lines.append(f"Status: ERROR")
        log_lines.append(f"Message: {error_msg}")
        log_lines.append("")
    
    log_lines.append("=" * 70)
    
    # Write to log file (overwrite previous content)
    try:
        with open(log_file, 'w') as f:
            f.write('\n'.join(log_lines))
        logger.info(f"Model log written to {log_file}")
    except Exception as e:
        logger.error(f"Failed to write model log to file: {e}")

# Mount Routes
app.include_router(auth_router)
app.include_router(honeypot_router, prefix="/portal")
app.include_router(admin_router, prefix="/api")

# Mount Frontend (Static Files)
# We serve the frontend folder as static.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Mount Terminal Emulator (Static Files)
TERMINAL_DIR = os.path.join(BASE_DIR, "backend", "terminal_emulator")
app.mount("/terminal", StaticFiles(directory=TERMINAL_DIR), name="terminal")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/login.html")
