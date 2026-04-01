"""
Email template for session completion reports.
Formats session data into professional HTML and plain text emails.
"""

from datetime import datetime
from typing import Dict, Any
import json


def get_session_report_email_template(report: Dict[str, Any]) -> tuple[str, str, str]:
    """
    Generate professional email template for session completion reports.
    
    Args:
        report: Session report dictionary from session_report_generator
        
    Returns:
        Tuple of (subject, html_body, text_body)
    """
    
    session_id = report.get('session_id', 'Unknown')
    attacker_ip = report.get('attacker_ip', 'Unknown')
    duration = report.get('connection_duration', 'Unknown')
    start_time = report.get('session_start', 'Unknown')
    end_time = report.get('session_end', 'Unknown')
    command_count = report.get('command_count', 0)
    
    fingerprint = report.get('browser_fingerprint', {})
    browser = fingerprint.get('browser', 'Unknown')
    os = fingerprint.get('os', 'Unknown')
    user_agent = fingerprint.get('user_agent', 'Unknown')
    
    profile = report.get('attacker_profile', {})
    profile_status = profile.get('status', 'No data')
    
    # Extract key profile metrics if available
    profile_html = ""
    if profile and profile.get('skill'):
        # Profile has data from the ML profiler
        skill = profile.get('skill', 'Unknown')
        intent = profile.get('intent', 'Unknown')
        confidence = profile.get('confidence', 0)
        intent_conf = profile.get('intent_confidence', 0)
        skill_conf = profile.get('skill_confidence', 0)
        
        profile_html = f"""
        <div class="section">
            <div class="section-title">Attacker Profile Analysis (AI-Generated)</div>
            <div class="profile-metrics">
                <div class="info-row">
                    <div class="info-label">Skill Level:</div>
                    <div class="info-value"><strong>{skill}</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Attack Intent:</div>
                    <div class="info-value"><strong>{intent}</strong></div>
                </div>
                <div class="info-row">
                    <div class="info-label">Overall Confidence:</div>
                    <div class="info-value">{confidence * 100:.1f}%</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Skill Confidence:</div>
                    <div class="info-value">{skill_conf * 100:.1f}%</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Intent Confidence:</div>
                    <div class="info-value">{intent_conf * 100:.1f}%</div>
                </div>
            </div>
        </div>
        """
    
    # Subject line
    subject = f"Session Report: Attacker {attacker_ip} - {duration} session"
    
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
            max-width: 900px;
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
        .completion-badge {{
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        }}
        .section {{
            margin: 25px 0;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 15px;
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
            min-width: 160px;
        }}
        .info-value {{
            color: #333;
            word-break: break-all;
            flex: 1;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }}
        .command-section {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}
        .profile-metrics {{
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .profile-metrics h4 {{
            margin-top: 0;
            color: #1565c0;
        }}
        .summary-stat {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 10px 10px 10px 0;
            min-width: 120px;
            text-align: center;
        }}
        .summary-stat-label {{
            font-size: 12px;
            opacity: 0.9;
        }}
        .summary-stat-value {{
            font-size: 20px;
            font-weight: 600;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Session Completion Report</h1>
            <span class="completion-badge">SESSION ENDED</span>
        </div>
        
        <div class="section">
            <div class="summary-stat">
                <div class="summary-stat-label">Session Duration</div>
                <div class="summary-stat-value">{duration}</div>
            </div>
            <div class="summary-stat">
                <div class="summary-stat-label">Commands Executed</div>
                <div class="summary-stat-value">{command_count}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Session Overview</div>
            <div class="info-row">
                <div class="info-label">Session ID:</div>
                <div class="info-value"><span class="highlight">{session_id}</span></div>
            </div>
            <div class="info-row">
                <div class="info-label">Attacker IP:</div>
                <div class="info-value"><span class="highlight">{attacker_ip}</span></div>
            </div>
            <div class="info-row">
                <div class="info-label">Connection Start:</div>
                <div class="info-value">{start_time}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Connection End:</div>
                <div class="info-value">{end_time}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Duration:</div>
                <div class="info-value">{duration}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Browser Fingerprint</div>
            <div class="info-row">
                <div class="info-label">Browser:</div>
                <div class="info-value">{browser}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Operating System:</div>
                <div class="info-value">{os}</div>
            </div>
            <div class="info-row">
                <div class="info-label">User Agent:</div>
                <div class="info-value"><code>{user_agent}</code></div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Command Execution History ({command_count} commands)</div>
            <div class="command-section">
                {report.get('command_history', 'No commands available').replace(chr(10), '<br>')}
            </div>
        </div>
        
        {profile_html if profile_html else ""}
        
        <div class="footer">
            <p><strong>Next Steps:</strong></p>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Review the command execution history for suspicious patterns</li>
                <li>Update firewall rules if the attacker IP is from a known malicious source</li>
                <li>Monitor similar attack patterns from other IPs</li>
                <li>Use the attacker profile to identify skill level and threat classification</li>
            </ul>
            
            <p style="margin-top: 20px; font-size: 11px; color: #999;">
                This is an automated report from your Honeypot Security System. 
                Do not reply to this email.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Plain text version (fallback)
    text_body = f"""
HONEYPOT SESSION COMPLETION REPORT
==================================

SESSION ENDED

QUICK SUMMARY:
- Duration: {duration}
- Attacker IP: {attacker_ip}
- Commands Executed: {command_count}

SESSION DETAILS:
----------------
Session ID:        {session_id}
Attacker IP:       {attacker_ip}
Connection Start:  {start_time}
Connection End:    {end_time}
Total Duration:    {duration}

BROWSER FINGERPRINT:
---------------------
Browser:           {browser}
Operating System:  {os}
User Agent:        {user_agent}

COMMAND EXECUTION HISTORY ({command_count} commands):
-----------------------------------------------------
{report.get('command_history', 'No commands available')}

ATTACKER PROFILE:
-----------------
Status: {profile_status}
Skill Level:       {profile.get('skill', 'N/A')}
Attack Intent:     {profile.get('intent', 'N/A')}
Overall Confidence: {profile.get('confidence', 0) * 100:.1f}%
Skill Confidence:  {profile.get('skill_confidence', 0) * 100:.1f}%
Intent Confidence: {profile.get('intent_confidence', 0) * 100:.1f}%

NEXT STEPS:
-----------
1. Review the command execution history for suspicious patterns
2. Update firewall rules if the attacker IP is from a known malicious source
3. Monitor similar attack patterns from other IPs
4. Use the attacker profile to identify skill level and threat classification

---
This is an automated report from your Honeypot Security System.
Do not reply to this email.
"""
    
    return subject, html_body, text_body
