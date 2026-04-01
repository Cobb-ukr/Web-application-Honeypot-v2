# Session Report System

Complete guide to the automated session report generation and email notification system.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Overview](#overview)
3. [Features](#features)
4. [System Architecture](#system-architecture)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Email Format](#email-format)
8. [Integration](#integration)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Customization](#customization)

---

## Quick Reference

### 🎯 What It Does

When an attacker logs out of the honeypot, a detailed email report is automatically generated containing:
- Attacker's IP address
- Browser fingerprint (browser type, OS, user agent)
- Connection duration
- Complete list of terminal commands executed with system responses
- AI-generated attacker profile (skill level, sophistication)

### 📂 File Locations

```
New Files:
├── reportGen/
│   ├── __init__.py (empty module file)
│   └── session_report_generator.py (core logic - 200+ lines)
└── backend/
    └── email_templates_report.py (email formatting - 280+ lines)

Modified Files:
└── backend/honeypot.py (added imports + 2 new functions)
```

### 🔧 Quick Start - For End Users

Nothing to do! Reports are automatically sent when attackers logout.

### 🚀 Key Functions

#### `reportGen.session_report_generator`

| Function | Purpose |
|----------|---------|
| `generate_session_report(session_id)` | Main entry point - generates complete report |
| `get_session_data(session_id)` | Fetches session data from DB |
| `calculate_connection_duration(start, end)` | Formats duration as "1h 23m 45s" |
| `extract_browser_fingerprint(ua, headers)` | Parses browser/OS from headers |
| `format_command_history(commands)` | Formats commands with timestamps/responses |
| `get_attacker_profile(session_id)` | Runs ML profiler on commands |

#### `backend.email_templates_report`

| Function | Purpose |
|----------|---------|
| `get_session_report_email_template(report)` | Creates (subject, html, text) tuple |

#### `backend.honeypot`

| Function | Purpose |
|----------|---------|
| `send_session_completion_report(session_id)` | Generates + sends email report |
| `end_session(session_id)` | Enhanced - now sends report on logout |

### ⚙️ Configuration

No new configuration needed! Uses existing `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RECEIVER_EMAIL=security_team@company.com
```

**Reports automatically sent to**: `RECEIVER_EMAIL`

---

## Overview

The session report generation system automatically creates comprehensive security reports when an attacker logs out of the honeypot. These reports are generated in real-time and sent via email to the configured security team.

### Automatic Report Generation
- Triggered when an attacker executes the logout command
- Non-blocking: Report generation runs asynchronously without delaying the logout response
- Graceful error handling: System continues to function even if report generation fails

---

## Features

### 1. Session Overview

Each session report includes:

- **Session ID**: Unique identifier for tracking
- **Attacker IP Address**: Source IP of the connection
- **Connection Duration**: Total time attacker was connected (formatted as h:m:s)
- **Start/End Timestamps**: Exact UTC times of connection lifecycle
- **Command Count**: Total number of commands executed

### 2. Browser Fingerprint Analysis

- **Browser Type**: Chrome, Firefox, Safari, Edge, etc.
- **Operating System**: Windows, macOS, Linux, Android
- **User Agent String**: Full HTTP User-Agent header
- **Accept Headers**: Language and encoding preferences
- **Security Headers**: Fetch destination and mode information

### 3. Complete Command History

- Full list of all terminal commands executed by the attacker
- Timestamps for each command execution
- System responses to each command (first 500 characters shown in email)
- Organized chronologically with command numbering

### 4. Attacker Profile Analysis

- **Skill Level Assessment**: Based on command patterns
- **Attack Sophistication Score**: Complexity metrics
- **Average Complexity**: Mean complexity of executed commands
- **Maximum Complexity**: Most complex command observed
- Behavioral analysis using machine learning profiling

### 5. Email Format

Reports are sent in both HTML and plain text formats:

**HTML Version**:
- Professional styling with gradient headers
- Color-coded sections for easy scanning
- Embedded command history viewer with scrollable display
- Visual summary statistics
- Formatted metrics cards

**Plain Text Version**:
- Fallback format for email clients without HTML support
- Same information as HTML, plain-text formatted
- Ensures compatibility across all email systems

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   HONEYPOT LOGOUT                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │   end_session()              │
        │   (honeypot.py)              │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────────┐
        │ send_session_completion_report()         │
        │ • Validates email config                 │
        │ • Calls report generator                 │
        │ • Formats email template                 │
        │ • Sends via SMTP                         │
        └────────────┬─────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌──────────────────┐  ┌───────────────────────┐
    │ Report Generator │  │ Email Template        │
    │ (sessionReport   │  │ Generator             │
    │  Generator.py)   │  │ (email_templates_     │
    │                  │  │  report.py)           │
    │ • Gets session   │  │                       │
    │   data from DB   │  │ • Formats HTML        │
    │ • Extracts       │  │ • Formats plain text  │
    │   fingerprint    │  │ • Embeds all data     │
    │ • Formats cmds   │  │                       │
    │ • Runs profiler  │  │                       │
    └──────────────────┘  └───────────────────────┘
```

### Module Structure

```
honeypot-ai/
├── reportGen/
│   ├── __init__.py                    (Empty module init)
│   └── session_report_generator.py    (Core report logic)
│
├── backend/
│   ├── honeypot.py                    (Enhanced with report integration)
│   ├── email_templates_report.py      (Report email templates)
│   └── email_service.py               (Existing email service - reused)
│
└── attacker_profiler/                 (Existing, called by report generator)
    └── step5_infer.py                 (Profile analysis)
```

### Data Flow

#### 1. Session Data Collection
```python
Session Data Collected:
├── session_id
├── ip_address
├── user_agent
├── start_time
├── end_time
├── commands (JSON array)
└── headers (HTTP headers dict)
```

#### 2. Report Generation Process

```
get_session_data(session_id)
    ├── Query HoneypotSession from database
    ├── Parse JSON commands array
    ├── Parse JSON headers dict
    └── Return structured session object

├── calculate_connection_duration()
│   ├── Get end_time - start_time
│   └── Format as "Xh Ym Zs"

├── extract_browser_fingerprint()
│   ├── Parse user_agent string
│   ├── Detect browser type
│   ├── Detect OS
│   └── Extract header values

├── format_command_history()
│   ├── Iterate through commands array
│   ├── Format with timestamps
│   ├── Include responses (truncated)
│   └── Return formatted text

└── get_attacker_profile()
    ├── Import AttackerProfiler
    ├── Load commands from session
    ├── Run profiler.analyze_session()
    └── Return profile metrics
```

#### 3. Email Sending

```
generate_session_report() → Report Dictionary
                ├── Extract all metrics
                └── Compile comprehensive object

get_session_report_email_template() → (subject, html, text)
                ├── Extract data from report
                ├── Generate HTML version
                ├── Generate plain text version
                └── Return tuple

send_session_completion_report()
                ├── Validate email config
                ├── Create MIME message
                ├── Add HTML and plain text parts
                ├── Connect via SMTP
                ├── Authenticate
                └── Send message
```

### Integration Points

#### Existing Functionality Preserved

1. **Database Operations**: Uses existing `HoneypotSession` model
2. **Email Service**: Reuses `EmailNotificationService` infrastructure
3. **Email Configuration**: Uses same `.env` variables
4. **Attacker Profiler**: Leverages existing ML models
5. **Session Management**: No changes to session creation/tracking

#### Non-Breaking Changes

- Report generation is **asynchronous** - doesn't block logout
- **Error handling**: Failures don't interrupt the logout process
- **Test mode**: Reports skipped for test sessions (session IDs starting with `test_`)
- **Optional feature**: Gracefully degrades if:
  - Email not configured
  - Profiler unavailable
  - Session data incomplete

---

## Configuration

### Prerequisites

Ensure your `.env` file has email configured:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=Honeypot Security System
RECEIVER_EMAIL=security_team@company.com
```

For detailed SMTP setup instructions, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md#gmail-smtp-setup).

### Optional Customizations

You can modify the following files to customize reports:

**Adjust Report Format** (`email_templates_report.py`):
- Modify HTML styling
- Change section order
- Add/remove metrics
- Customize email subject line

**Extend Report Data** (`session_report_generator.py`):
- Add geolocation lookups (IP lookup services)
- Extract additional fingerprints
- Add threat intelligence lookups
- Include system metrics

---

## Usage Examples

### For Developers

#### Generate a Report Manually

```python
from reportGen.session_report_generator import generate_session_report

# Generate report for a specific session
report = generate_session_report("session-id-here")

# Access report data
print(report['attacker_ip'])
print(report['connection_duration'])
print(report['command_count'])
```

#### Send a Report via Email

```python
from backend.honeypot import send_session_completion_report

success = send_session_completion_report("session-id-here")
```

#### Report Data Structure

```python
{
    'report_generated_at': '2026-02-22T12:34:56.789012',
    'session_id': 'abc-123-def',
    'attacker_ip': '192.168.1.100',
    'connection_duration': '1h 23m 45s',
    'session_start': '2026-02-22T11:00:00',
    'session_end': '2026-02-22T12:30:00',
    'browser_fingerprint': {
        'user_agent': 'Mozilla/5.0...',
        'browser': 'Chrome',
        'os': 'Windows',
        'accept_language': 'en-US',
        'accept_encoding': 'gzip, deflate'
    },
    'command_count': 42,
    'command_history': '--- Command 1 ---\nTimestamp: ...',
    'attacker_profile': {
        'skill_level': 'intermediate',
        'sophistication': 7.5,
        'avg_complexity': 6.2,
        'max_complexity': 9.1
    }
}
```

### Accessing Report in Email Context

The report is automatically sent on logout. To verify it worked:

```python
from backend.honeypot import send_session_completion_report

# Manually trigger report (for testing)
success = send_session_completion_report("session-id")
```

---

## Email Format

### Subject Line

**Format**: `Session Report: Attacker 192.168.1.100 - 1h 23m 45s session`

### Email Body Structure

**Includes**:
- HTML version (pretty formatted)
- Plain text version (fallback)
- Both sent together (client chooses)

### Example Report Email

```
FROM: Honeypot Security System <your_email@gmail.com>
TO: security_team@company.com
SUBJECT: Session Report: Attacker 203.45.67.89 - 2h 15m 30s session

---

SESSION COMPLETION REPORT

📊 Session Ended

Session Duration: 2h 15m 30s
Commands Executed: 47

SESSION OVERVIEW

Session ID: abc-def-123-456
Attacker IP: 203.45.67.89
Connection Start: 2026-02-22 10:00:00
Connection End: 2026-02-22 12:15:30
Total Duration: 2h 15m 30s

BROWSER FINGERPRINT

Browser: Chrome
Operating System: Linux
User Agent: Mozilla/5.0 (X11; Linux x86_64)...

COMMAND EXECUTION HISTORY (47 commands)

--- Command 1 ---
Timestamp: 2026-02-22 10:00:15
Command: whoami
Response: root

--- Command 2 ---
Timestamp: 2026-02-22 10:00:20
Command: pwd
Response: /root

[... 45 more commands ...]

ATTACKER PROFILE

Status: Analysis Complete
Skill Level: intermediate
Attack Sophistication: 7.5
Avg Complexity: 6.2
Max Complexity: 9.1

---

This is an automated report from your Honeypot Security System.
Do not reply to this email.
```

---

## Integration

### Logout Flow

```
Logout → end_session()
           ├── Mark session inactive
           ├── Send report (async)
           │   ├── get_session_data()
           │   ├── format command history
           │   ├── extract fingerprint
           │   ├── run profiler
           │   └── send email
           └── Return response
```

### Error Handling

#### Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| Email not configured | Logs warning, skips sending |
| Session not found | Logs warning, returns None |
| No commands executed | Creates profile with 0 commands |
| Profiler fails | Includes "Profiling unavailable" in report |
| SMTP connection fails | Logs error, doesn't block logout |
| Report generation fails | Continues session logout normally |

#### Logging

All report operations are logged with appropriate levels:

```
INFO: Generating session report for {session_id}
INFO: Successfully profiled session {session_id}
INFO: ✅ Session completion report sent successfully
WARNING: ⚠️ Email alert failed (returned False)
ERROR: ❌ Failed to send session completion report: {error}
```

### Performance Considerations

- **Report generation**: ~1-5 seconds depending on command count
- **Email sending**: ~2-10 seconds depending on email provider
- **Non-blocking**: Logout response returned immediately; report sent asynchronously
- **Database**: Minimal impact; single query per report
- **Profiler**: Uses existing trained model; no retraining needed

---

## Testing

### Quick Test

```bash
# 1. Trigger a logout (which will attempt report generation)
curl -X POST http://localhost:8000/portal/logout \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-123"}'

# 2. Check email for report (arrives in seconds)

# 3. Check logs for debug info
# Look for: "✅ Session completion report sent successfully"
```

### Manual Report Generation

```bash
cd honeypot-ai

# Generate report and inspect
python -c "
from reportGen.session_report_generator import generate_session_report
report = generate_session_report('session-id')
import json
print(json.dumps(report, indent=2, default=str))
"
```

### Test Email Sending

```python
from backend.honeypot import send_session_completion_report

result = send_session_completion_report("session-id")
print(f"Email sent: {result}")
```

---

## Troubleshooting

### Reports Not Being Sent?

**Check:**
1. `.env` file has `SMTP_PASSWORD` set (not empty)
2. Verify `RECEIVER_EMAIL` is correct
3. Check logs for error messages
4. Test email configuration: `POST /test_honeypot_email` endpoint

**Solutions:**
```bash
# Test SMTP configuration
curl -X POST http://localhost:8000/api/admin/test_email

# Check environment variables
cat honeypot-ai/.env | grep SMTP

# View logs
tail -f honeypot-ai/logs/model_log.txt
```

### Profile Data Missing?

**Check:**
1. Ensure attacker executed commands (empty sessions won't have profiles)
2. Check that ML model file exists in `attacker_profiler/model_store/`
3. Review logs for profiler errors

**Solutions:**
```bash
# Verify model exists
ls -lh honeypot-ai/attacker_profiler/model_store/

# Test profiler manually
python honeypot-ai/attacker_profiler/step5_infer.py
```

### Email Formatting Issues?

**Check:**
1. Test with different email clients
2. Check `email_templates_report.py` CSS styling
3. Verify both HTML and plain text parts render correctly

### Support Checklist

If reports aren't working:
- [ ] `.env` file has `SMTP_PASSWORD` (not empty)
- [ ] `RECEIVER_EMAIL` is set correctly
- [ ] Application logs show "✅ report sent successfully"
- [ ] ML model file exists in `attacker_profiler/model_store/`
- [ ] Test email works: `POST /test_honeypot_email`
- [ ] Attacker session has commands (empty sessions can't be profiled)

---

## Customization

### Change Email Subject Line

Edit `backend/email_templates_report.py`:
```python
subject = f"Security Report: Session from {attacker_ip}"
```

### Add Geolocation

Edit `reportGen/session_report_generator.py`:
```python
def get_geolocation(ip):
    # Call MaxMind or similar service
    return location_data
```

Add to report:
```python
report['geolocation'] = get_geolocation(session_data['ip_address'])
```

Include in template:
```html
<div class="info-row">
    <div class="info-label">Location:</div>
    <div class="info-value">{geolocation['city']}</div>
</div>
```

### Modify HTML Styling

Edit `backend/email_templates_report.py` to customize:
- Colors and gradients
- Font sizes and families
- Section layouts
- Card styling
- Command history display

### Add Custom Metrics

1. Calculate metric in `session_report_generator.py`
2. Add to report dictionary
3. Display in email template

Example:
```python
# In session_report_generator.py
report['custom_metric'] = calculate_custom_metric(session_data)

# In email_templates_report.py
<div class="info-row">
    <div class="info-label">Custom Metric:</div>
    <div class="info-value">{custom_metric}</div>
</div>
```

---

## Security Considerations

⚠️ **Important Security Notes**:

- Reports contain **full command history** - treat as sensitive data
- Include **attacker IP and browser details** - handle with care
- Sent via **SMTP with TLS encryption** - ensure proper configuration
- Consider **email encryption** for highly sensitive environments
- **Store with restricted access** - limit who can view reports
- **Sanitize before sharing** - remove sensitive info if sharing outside team

### Best Practices

1. Use encrypted email when possible
2. Restrict access to email account receiving reports
3. Archive reports in secure storage
4. Follow data retention policies
5. Consider PII regulations (GDPR, CCPA)

---

## Future Enhancements

Potential improvements:

1. **Geolocation**: Add IP geolocation lookup
2. **Threat Intelligence**: Query IP reputation databases
3. **Command Analysis**: Add MITRE ATT&CK mapping
4. **PDF Export**: Generate downloadable PDF reports
5. **Dashboard Integration**: Store reports in database for review
6. **Custom Templates**: Allow admin-defined email templates
7. **Conditional Alerting**: Only send reports for high-threat sessions
8. **Report Archival**: Store reports in S3 or similar

---

## Summary

The session report system provides:
- ✅ Automatic report generation on logout
- ✅ Comprehensive session analysis
- ✅ Professional email formatting
- ✅ ML-powered attacker profiling
- ✅ Non-blocking asynchronous operation
- ✅ Graceful error handling
- ✅ Easy customization and extension

For detailed technical information, see [full_project.md](full_project.md#session-report-generation-system).
