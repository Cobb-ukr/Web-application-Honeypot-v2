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
import requests

from backend.terminal_emulator.command_filter import (
    should_use_llm,
    sanitize_terminal_output,
    build_connection_error_message,
)
from backend.terminal_emulator.state_manager import load_state, merge_state
from backend.playbook_loader import get_relevant_context

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
    with open(UI_PATH, "r", encoding="utf-8") as f:
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

@router.get("/state")
async def get_terminal_state(request: Request):
    state = load_state()
    return {"status": "success", "state": state}

@router.post("/state_update")
async def update_terminal_state(request: Request):
    body = await request.body()
    session_id = request.query_params.get("session_id")

    try:
        data = json.loads(body)
        incoming_state = data.get("state", {})
    except Exception:
        incoming_state = {}

    updated_state = merge_state(session_id, incoming_state)
    return {"status": "success", "state": updated_state}

@router.post("/llm_execute")
async def llm_execute(request: Request):
    body = await request.body()
    session_id = request.query_params.get("session_id")

    print("=" * 80)
    print("[LLM] llm_execute endpoint called")
    print(f"[LLM] Session ID: {session_id}")

    try:
        data = json.loads(body)
    except Exception as e:
        print(f"[LLM] ERROR parsing request body: {e}")
        data = {}

    command = data.get("command", "")
    state = data.get("state") or load_state(session_id)

    print(f"[LLM] Command: {command}")
    print(f"[LLM] State keys: {list(state.keys())}")

    allowed, reason = should_use_llm(command)
    print(f"[LLM] Command allowed: {allowed}, reason: {reason}")
    
    if not allowed:
        cmd_name = command.split(" ")[0] if command else "unknown"
        result = {
            "status": "skipped",
            "reason": reason,
            "output": f"bash: {cmd_name}: command not found",
        }
        print(f"[LLM] Returning skipped: {result}")
        return result

    api_key = os.getenv("GROQ_API_KEY", "")
    print(f"[LLM] API key present: {bool(api_key)}")
    print(f"[LLM] API key length: {len(api_key) if api_key else 0}")
    
    if not api_key:
        print("[LLM] ERROR: No API key found!")
        return {
            "status": "error",
            "output": build_connection_error_message(),
        }

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    print(f"[LLM] Using model: {model}")

    system_prompt = (
        "You are a Linux terminal emulator running Ubuntu 22.04 in a honeypot system. "
        "You must respond EXACTLY like a real Linux terminal would — output ONLY the raw command output. "
        "NEVER include explanations, commentary, markdown formatting, or meta-text like 'the system is now compromised'. "
        "NEVER change the shell prompt format (e.g. do NOT output '[root@...]#'). "
        "The current user is an unprivileged user named 'user'. "
        "Assume standard Linux tools are installed: curl, wget, nmap, base64, python3, gcc, ssh, scp, netcat, etc. "
        "If attack reference data is provided, use it to make outputs more realistic."
    )

    # Look up relevant playbook context for this command
    playbook_context = get_relevant_context(command)

    user_prompt = (
        "Current system state (JSON):\n"
        f"{json.dumps(state)}\n\n"
    )

    if playbook_context:
        user_prompt += f"{playbook_context}\n\n"

    user_prompt += (
        "Rules:\n"
        "- Output ONLY the raw terminal output, nothing else.\n"
        "- Use the state to keep outputs consistent (files, directories, user, hostname).\n"
        "- If attack reference data is provided, use it for realistic command output.\n"
        "- If a command produces no output (like cp, mv), return an empty string.\n"
        "- For truly invalid commands, return 'bash: <cmd>: command not found'.\n"
        "- Do NOT add any commentary, explanations, or narrative text.\n"
        "- Do NOT change the shell prompt or pretend to be root.\n"
        "- Keep responses concise (under 20 lines) and realistic.\n\n"
        f"Command: {command}\n"
        "Output:"
    )

    try:
        print(f"[LLM] Calling Groq with model: {model}")
        print(f"[LLM] Command: {command}")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=10,
        )
        
        print(f"[LLM] Response status: {response.status_code}")
        response.raise_for_status()
        
        payload = response.json()
        print(f"[LLM] Response payload: {payload}")
        
        raw_output = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        output = sanitize_terminal_output(raw_output)
        print(f"[LLM] Sanitized output: {output[:100]}...")
        print("=" * 80)
        return {"status": "success", "output": output}
    except requests.exceptions.Timeout:
        print(f"[LLM] ERROR: Request timeout after 10 seconds")
        print("=" * 80)
        return {
            "status": "error",
            "output": build_connection_error_message(),
        }
    except requests.exceptions.HTTPError as e:
        print(f"[LLM] HTTP Error: {e.response.status_code} - {e.response.text}")
        print("=" * 80)
        return {
            "status": "error",
            "output": build_connection_error_message(),
        }
    except Exception as e:
        print(f"[LLM] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return {
            "status": "error",
            "output": build_connection_error_message(),
        }

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

