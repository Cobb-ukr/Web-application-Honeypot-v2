from datetime import datetime
from typing import Dict, Any

def get_honeypot_alert_template(session_data: Dict[str, Any]) -> tuple[str, str, str]:
    """
    Generate professional email template for honeypot alerts.
    
    Args:
        session_data: Dictionary containing session information
        
    Returns:
        Tuple of (subject, html_body, text_body)
    """
    
    ip_address = session_data.get('ip_address', 'Unknown')
    session_id = session_data.get('session_id', 'N/A')
    timestamp = session_data.get('timestamp', datetime.utcnow())
    user_agent = session_data.get('user_agent', 'Unknown')
    location = session_data.get('location', 'Unknown')
    
    # Format timestamp
    if isinstance(timestamp, str):
        time_str = timestamp
    else:
        time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Subject line - professional and clear
    subject = f"Security Alert: Honeypot Session Detected from {ip_address}"
    
    # HTML Email Body
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 20px -30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .alert-badge {{
            display: inline-block;
            background-color: #ff4444;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        }}
        .info-section {{
            margin: 20px 0;
        }}
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}
        .info-row:last-child {{
            border-bottom: none;
        }}
        .info-label {{
            font-weight: 600;
            color: #555;
            min-width: 140px;
        }}
        .info-value {{
            color: #333;
            word-break: break-all;
        }}
        .ip-highlight {{
            background-color: #fff3cd;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            font-size: 12px;
            color: #666;
        }}
        .action-required {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .action-required strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Honeypot Security Alert</h1>
            <span class="alert-badge">INTRUSION DETECTED</span>
        </div>
        
        <p>A new honeypot session has been initiated. An unauthorized user is attempting to access your system.</p>
        
        <div class="action-required">
            <strong>⚠️ Action Required:</strong> Review the session details below and monitor the attacker's activity through your admin dashboard.
        </div>
        
        <div class="info-section">
            <h3 style="color: #667eea; margin-bottom: 15px;">Session Details</h3>
            
            <div class="info-row">
                <div class="info-label">IP Address:</div>
                <div class="info-value"><span class="ip-highlight">{ip_address}</span></div>
            </div>
            
            <div class="info-row">
                <div class="info-label">Session ID:</div>
                <div class="info-value">{session_id}</div>
            </div>
            
            <div class="info-row">
                <div class="info-label">Timestamp:</div>
                <div class="info-value">{time_str}</div>
            </div>
            
            <div class="info-row">
                <div class="info-label">User Agent:</div>
                <div class="info-value">{user_agent}</div>
            </div>
            
            <div class="info-row">
                <div class="info-label">Location:</div>
                <div class="info-value">{location}</div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>What to do next:</strong></p>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Log in to your honeypot admin dashboard to view real-time activity</li>
                <li>Monitor the attacker's commands and behavior</li>
                <li>Review attack patterns and update security measures if needed</li>
            </ul>
            
            <p style="margin-top: 20px; font-size: 11px; color: #999;">
                This is an automated alert from your Honeypot Security System. 
                Do not reply to this email.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Plain text version (fallback)
    text_body = f"""
HONEYPOT SECURITY ALERT
=======================

INTRUSION DETECTED

A new honeypot session has been initiated. An unauthorized user is attempting to access your system.

SESSION DETAILS:
----------------
IP Address:    {ip_address}
Session ID:    {session_id}
Timestamp:     {time_str}
User Agent:    {user_agent}
Location:      {location}

ACTION REQUIRED:
----------------
1. Log in to your honeypot admin dashboard to view real-time activity
2. Monitor the attacker's commands and behavior
3. Review attack patterns and update security measures if needed

---
This is an automated alert from your Honeypot Security System.
Do not reply to this email.
"""
    
    return subject, html_body, text_body
