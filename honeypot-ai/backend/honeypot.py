from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from backend.database import SessionLocal, HoneypotSession
from backend.email_service import email_service
from datetime import datetime
import json
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def is_test_mode(session_id: str) -> bool:
    """Check if session is in test mode (prefixed with test_)"""
    return session_id and session_id.startswith("test_")

def get_or_create_session(request: Request, session_id: str):
    """Get existing session or create new one"""
    # Skip database operations for test mode
    if is_test_mode(session_id):
        return None
    
    db = SessionLocal()
    
    # Try to find existing session
    session = db.query(HoneypotSession).filter(
        HoneypotSession.session_id == session_id,
        HoneypotSession.is_active == True
    ).first()
    
    if not session:
        # Create new session
        session = HoneypotSession(
            session_id=session_id,
            ip_address=request.client.host,
            start_time=datetime.utcnow(),
            is_active=True,
            commands=json.dumps([]),  # Empty array initially
            user_agent=request.headers.get("user-agent", ""),
            headers=json.dumps(dict(request.headers))
        )
        db.add(session)
        db.commit()
        
        # Send email alert for new session
        logger.info(f"New honeypot session created: {session_id} from {request.client.host}")
        try:
            session_data = {
                'ip_address': request.client.host,
                'session_id': session_id,
                'timestamp': datetime.utcnow(),
                'user_agent': request.headers.get("user-agent", "Unknown"),
                'location': 'Unknown'  # You can integrate IP geolocation API later
            }
            logger.info(f"Attempting to send email alert for session: {session_id}")
            result = email_service.send_honeypot_alert(session_data)
            if result:
                logger.info(f"✅ Email alert sent successfully for session: {session_id}")
            else:
                logger.warning(f"⚠️ Email alert failed (returned False) for session: {session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send email alert for session {session_id}: {e}", exc_info=True)
    
    db.close()
    return session

def append_to_session(session_id: str, action_type: str, details: str = "", response: str = ""):
    """Append an action to the session's commands array"""
    # Skip logging for test mode
    if is_test_mode(session_id):
        return
    
    db = SessionLocal()
    
    session = db.query(HoneypotSession).filter(
        HoneypotSession.session_id == session_id
    ).first()
    
    if session:
        try:
            commands = json.loads(session.commands)
        except:
            commands = []
        
        # Add new command with optional response
        command_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": action_type,
            "command": details,
            "response": response if response else ""
        }
        
        commands.append(command_entry)
        
        session.commands = json.dumps(commands)
        db.commit()
    
    db.close()

def end_session(session_id: str):
    """Mark session as inactive"""
    # Skip for test mode
    if is_test_mode(session_id):
        print(f"Test mode session {session_id} - not logging to database")
        return True
    
    db = SessionLocal()
    
    try:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.session_id == session_id
        ).first()
        
        if session:
            session.is_active = False
            session.end_time = datetime.utcnow()
            db.commit()
            print(f"Session {session_id} ended at {session.end_time}, is_active={session.is_active}")
            return True
        else:
            print(f"Session {session_id} not found")
            return False
    except Exception as e:
        print(f"Error ending session: {e}")
        db.rollback()
        return False
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
async def fake_dashboard(request: Request):
    session_id = request.query_params.get("session_id")
    test_mode = request.query_params.get("test") == "true"
    
    if not session_id:
        # Generate new session ID
        if test_mode:
            session_id = f"test_{uuid.uuid4()}"
        else:
            session_id = str(uuid.uuid4())
    
    # Create or get session (email alert is sent inside get_or_create_session for new sessions)
    get_or_create_session(request, session_id)
    
    append_to_session(session_id, "Viewed Fake Dashboard", "Accessed honeypot interface", "Dashboard loaded successfully")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UI_PATH = os.path.join(BASE_DIR, "frontend", "honeypot_ui.html")
    with open(UI_PATH, "r") as f:
        content = f.read()
    
    # Inject session ID into the HTML
    content = content.replace("SESSION_ID_PLACEHOLDER", session_id)
    return content

@router.get("/files")
async def fake_files(request: Request):
    session_id = request.query_params.get("session_id")
    if session_id:
        append_to_session(session_id, "Listed Fake Files", "Requested directory listing")
    
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
    session_id = request.query_params.get("session_id")
    if session_id:
        append_to_session(session_id, "Downloaded File", f"File: {filename}")
    
    # Return empty content as requested
    return ""

@router.post("/execute")
async def fake_terminal(request: Request):
    body = await request.body()
    session_id = request.query_params.get("session_id")
    
    command = ""
    output = ""
    
    try:
        data = json.loads(body)
        command = data.get("command", "")
        output = data.get("output", "")
    except:
        # Fallback for plain text body
        command = body.decode()
        output = ""
    
    # Create or get session on first command (this will trigger email alert for new sessions)
    if session_id:
        get_or_create_session(request, session_id)
        append_to_session(session_id, "Terminal Command", command, output)
    
    return {"status": "success", "output": output}

@router.post("/logout")
async def logout_honeypot(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
        session_id = data.get("session_id")
        if session_id:
            result = end_session(session_id)
            return {"message": "Session ended", "success": result}
    except Exception as e:
        print(f"Logout error: {e}")
        return {"error": str(e)}
    
    return {"error": "Invalid session"}

@router.post("/test_honeypot_email")
async def test_honeypot_email(request: Request):
    """Test endpoint to manually trigger a honeypot email alert"""
    logger.info("Test honeypot email endpoint called")
    try:
        test_session_data = {
            'ip_address': request.client.host,
            'session_id': 'test-manual-trigger-' + str(uuid.uuid4()),
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get("user-agent", "Test Browser"),
            'location': 'Test Location'
        }
        logger.info(f"Attempting to send test email alert...")
        result = email_service.send_honeypot_alert(test_session_data)
        if result:
            logger.info(f"✅ Test email sent successfully!")
            return {"success": True, "message": "Test email sent successfully!"}
        else:
            logger.warning(f"⚠️ Test email failed (returned False)")
            return {"success": False, "message": "Email service returned False"}
    except Exception as e:
        logger.error(f"❌ Failed to send test email: {e}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}

