# Session Report Generation System

## Overview

The session report generation system automatically creates comprehensive security reports when an attacker logs out of the honeypot. These reports are generated in real-time and sent via email to the configured security team.

## Features

### 1. **Automatic Report Generation**
- Triggered when an attacker executes the logout command
- Non-blocking: Report generation runs asynchronously without delaying the logout response
- Graceful error handling: System continues to function even if report generation fails

### 2. **Report Contents**

Each session report includes:

#### Session Overview
- **Session ID**: Unique identifier for tracking
- **Attacker IP Address**: Source IP of the connection
- **Connection Duration**: Total time attacker was connected (formatted as h:m:s)
- **Start/End Timestamps**: Exact UTC times of connection lifecycle
- **Command Count**: Total number of commands executed

#### Browser Fingerprint Analysis
- **Browser Type**: Chrome, Firefox, Safari, Edge, etc.
- **Operating System**: Windows, macOS, Linux, Android
- **User Agent String**: Full HTTP User-Agent header
- **Accept Headers**: Language and encoding preferences
- **Security Headers**: Fetch destination and mode information

#### Complete Command History
- Full list of all terminal commands executed by the attacker
- Timestamps for each command execution
- System responses to each command (first 500 characters shown in email)
- Organized chronologically with command numbering

#### Attacker Profile Analysis
- **Skill Level Assessment**: Based on command patterns
- **Attack Sophistication Score**: Complexity metrics
- **Average Complexity**: Mean complexity of executed commands
- **Maximum Complexity**: Most complex command observed
- Behavioral analysis using machine learning profiling

### 3. **Email Format**

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

## Data Flow

### 1. Session Data Collection
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

### 2. Report Generation Process

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

### 3. Email Sending

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

## Integration Points

### Existing Functionality Preserved

1. **Database Operations**: Uses existing `HoneypotSession` model
2. **Email Service**: Reuses `EmailNotificationService` infrastructure
3. **Email Configuration**: Uses same `.env` variables
4. **Attacker Profiler**: Leverages existing ML models
5. **Session Management**: No changes to session creation/tracking

### Non-Breaking Changes

- Report generation is **asynchronous** - doesn't block logout
- **Error handling**: Failures don't interrupt the logout process
- **Test mode**: Reports skipped for test sessions (session IDs starting with `test_`)
- **Optional feature**: Gracefully degrades if:
  - Email not configured
  - Profiler unavailable
  - Session data incomplete

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

## Usage Examples

### Manual Report Generation

```python
from reportGen.session_report_generator import generate_session_report

# Generate report for a specific session
report = generate_session_report("session-uuid-here")

print(f"Attacker IP: {report['attacker_ip']}")
print(f"Duration: {report['connection_duration']}")
print(f"Commands: {report['command_count']}")
print(f"Browser: {report['browser_fingerprint']['browser']}")
```

### Accessing Report in Email Context

The report is automatically sent on logout. To verify it worked:

```python
from backend.honeypot import send_session_completion_report

# Manually trigger report (for testing)
success = send_session_completion_report("session-id")
```

## Error Handling

### Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| Email not configured | Logs warning, skips sending |
| Session not found | Logs warning, returns None |
| No commands executed | Creates profile with 0 commands |
| Profiler fails | Includes "Profiling unavailable" in report |
| SMTP connection fails | Logs error, doesn't block logout |
| Report generation fails | Continues session logout normally |

### Logging

All report operations are logged with appropriate levels:

```
INFO: Generating session report for {session_id}
INFO: Successfully profiled session {session_id}
INFO: ✅ Session completion report sent successfully
WARNING: ⚠️ Email alert failed (returned False)
ERROR: ❌ Failed to send session completion report: {error}
```

## Performance Considerations

- **Report generation**: ~1-5 seconds depending on command count
- **Email sending**: ~2-10 seconds depending on email provider
- **Non-blocking**: Logout response returned immediately; report sent asynchronously
- **Database**: Minimal impact; single query per report
- **Profiler**: Uses existing trained model; no retraining needed

## Troubleshooting

### Reports not being sent?

1. Check `.env` file has `SMTP_PASSWORD` set (not empty)
2. Verify `RECEIVER_EMAIL` is correct
3. Check logs for error messages
4. Test email configuration: `POST /test_honeypot_email` endpoint

### Profile data missing?

1. Ensure attacker executed commands (empty sessions won't have profiles)
2. Check that ML model file exists in `attacker_profiler/model_store/`
3. Review logs for profiler errors

### Email formatting issues?

1. Test with different email clients
2. Check `email_templates_report.py` CSS styling
3. Verify both HTML and plain text parts render correctly

## Testing

### Quick Test

```bash
# Trigger a logout (which will attempt report generation)
curl -X POST http://localhost:8000/portal/logout \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}'
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

## Security Notes

- Reports contain full command history; treat as sensitive
- Email reports include attacker IP; use encrypted email
- Consider storing reports in encrypted format
- Logs contain session data; handle with appropriate access controls
- Test mode sessions exclude reports from generation
