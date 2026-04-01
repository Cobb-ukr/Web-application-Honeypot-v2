"""
Generate comprehensive session reports when attackers log out.
Includes session data, attacker profile, and command history.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from backend.database import SessionLocal, HoneypotSession

logger = logging.getLogger(__name__)


def get_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve all session data from database.
    
    Args:
        session_id: The honeypot session ID
        
    Returns:
        Dictionary with session details or None if not found
    """
    db = SessionLocal()
    try:
        session = db.query(HoneypotSession).filter(
            HoneypotSession.session_id == session_id
        ).first()
        
        if not session:
            logger.warning(f"Session {session_id} not found in database")
            return None
        
        try:
            commands = json.loads(session.commands) if session.commands else []
        except (json.JSONDecodeError, TypeError):
            commands = []
        
        try:
            headers = json.loads(session.headers) if session.headers else {}
        except (json.JSONDecodeError, TypeError):
            headers = {}
        
        return {
            'session_id': session.session_id,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'is_active': session.is_active,
            'commands': commands,
            'headers': headers
        }
    finally:
        db.close()


def calculate_connection_duration(start_time: datetime, end_time: Optional[datetime]) -> str:
    """
    Calculate and format connection duration.
    
    Args:
        start_time: Session start time
        end_time: Session end time
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    if not end_time:
        end_time = datetime.utcnow()
    
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def extract_browser_fingerprint(user_agent: str, headers: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract browser fingerprint information from user agent and headers.
    
    Args:
        user_agent: HTTP User-Agent header
        headers: Dictionary of HTTP headers
        
    Returns:
        Dictionary with browser fingerprint details
    """
    fingerprint = {
        'user_agent': user_agent or 'Unknown',
        'accept_language': headers.get('accept-language', 'Unknown'),
        'accept_encoding': headers.get('accept-encoding', 'Unknown'),
        'referer': headers.get('referer', 'Unknown'),
        'sec_fetch_dest': headers.get('sec-fetch-dest', 'Unknown'),
        'sec_fetch_mode': headers.get('sec-fetch-mode', 'Unknown'),
    }
    
    # Parse user agent for basic browser info
    if 'Chrome' in user_agent:
        fingerprint['browser'] = 'Chrome'
    elif 'Firefox' in user_agent:
        fingerprint['browser'] = 'Firefox'
    elif 'Safari' in user_agent:
        fingerprint['browser'] = 'Safari'
    elif 'Edge' in user_agent:
        fingerprint['browser'] = 'Edge'
    else:
        fingerprint['browser'] = 'Unknown'
    
    if 'Windows' in user_agent:
        fingerprint['os'] = 'Windows'
    elif 'Mac' in user_agent:
        fingerprint['os'] = 'macOS'
    elif 'Linux' in user_agent:
        fingerprint['os'] = 'Linux'
    elif 'Android' in user_agent:
        fingerprint['os'] = 'Android'
    else:
        fingerprint['os'] = 'Unknown'
    
    return fingerprint


def format_command_history(commands: List[Dict[str, Any]]) -> str:
    """
    Format command history into readable text.
    
    Args:
        commands: List of command dictionaries
        
    Returns:
        Formatted command history string
    """
    if not commands:
        return "No commands executed."
    
    formatted = []
    for i, cmd in enumerate(commands, 1):
        if isinstance(cmd, dict):
            timestamp = cmd.get('timestamp', 'Unknown')
            command = cmd.get('command', cmd.get('type', 'Unknown'))
            response = cmd.get('response', '')
            
            formatted.append(f"\n--- Command {i} ---")
            formatted.append(f"Timestamp: {timestamp}")
            formatted.append(f"Command: {command}")
            if response:
                formatted.append(f"Response: {response[:500]}")  # Truncate long responses
        else:
            formatted.append(f"\n--- Command {i} ---")
            formatted.append(f"{str(cmd)[:500]}")
    
    return "\n".join(formatted)


def get_attacker_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Run the attacker profiler on session commands and return the profile.
    
    Args:
        session_id: The honeypot session ID
        
    Returns:
        Dictionary with attacker profile or None if profiling fails
    """
    try:
        from attacker_profiler.step5_infer import AttackerProfiler
        
        # Get commands from database
        db = SessionLocal()
        try:
            session = db.query(HoneypotSession).filter(
                HoneypotSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for profiling")
                return None
            
            try:
                commands = json.loads(session.commands) if session.commands else []
            except (json.JSONDecodeError, TypeError):
                commands = []
            
            if not commands:
                logger.warning(f"Session {session_id} has no commands to profile")
                return None
            
            # Run profiler
            profiler = AttackerProfiler()
            profile = profiler.analyze_session(commands)
            
            logger.info(f"Successfully profiled session {session_id}")
            return profile
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to generate attacker profile for session {session_id}: {e}", exc_info=True)
        return None


def generate_session_report(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Generate comprehensive session report.
    
    Args:
        session_id: The honeypot session ID
        
    Returns:
        Dictionary with complete session report or None if session not found
    """
    logger.info(f"Generating session report for {session_id}")
    
    # Get session data
    session_data = get_session_data(session_id)
    if not session_data:
        return None
    
    # Calculate connection duration
    duration = calculate_connection_duration(
        session_data['start_time'],
        session_data['end_time']
    )
    
    # Extract browser fingerprint
    fingerprint = extract_browser_fingerprint(
        session_data['user_agent'],
        session_data['headers']
    )
    
    # Format command history
    command_history = format_command_history(session_data['commands'])
    
    # Get attacker profile
    attacker_profile = get_attacker_profile(session_id)
    
    # Compile report
    report = {
        'report_generated_at': datetime.utcnow().isoformat(),
        'session_id': session_id,
        'attacker_ip': session_data['ip_address'],
        'connection_duration': duration,
        'session_start': session_data['start_time'].isoformat() if session_data['start_time'] else 'Unknown',
        'session_end': session_data['end_time'].isoformat() if session_data['end_time'] else 'Unknown',
        'browser_fingerprint': fingerprint,
        'command_count': len(session_data['commands']),
        'command_history': command_history,
        'attacker_profile': attacker_profile if attacker_profile else {
            'status': 'Profiling unavailable',
            'reason': 'Could not analyze commands'
        }
    }
    
    logger.info(f"Session report generated successfully for {session_id}")
    return report
