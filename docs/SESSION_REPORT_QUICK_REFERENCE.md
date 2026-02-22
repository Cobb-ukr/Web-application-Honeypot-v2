# Session Report Feature - Quick Reference

## 🎯 What It Does

When an attacker logs out of the honeypot, a detailed email report is automatically generated containing:
- Attacker's IP address
- Browser fingerprint (browser type, OS, user agent)
- Connection duration
- Complete list of terminal commands executed with system responses
- AI-generated attacker profile (skill level, sophistication)

## 📂 File Locations

```
New Files:
├── reportGen/
│   ├── __init__.py (empty module file)
│   └── session_report_generator.py (core logic - 200+ lines)
└── backend/
    └── email_templates_report.py (email formatting - 280+ lines)

Modified Files:
└── backend/honeypot.py (added imports + 2 new functions)

Documentation:
├── docs/SESSION_REPORT_GUIDE.md (comprehensive guide)
└── docs/SESSION_REPORT_IMPLEMENTATION.md (this summary)
```

## 🔧 How to Use

### For End Users
Nothing to do! Reports are automatically sent when attackers logout.

### For Developers

**Generate a report manually:**
```python
from reportGen.session_report_generator import generate_session_report

report = generate_session_report("session-id-here")
print(report['attacker_ip'])
print(report['connection_duration'])
print(report['command_count'])
```

**Send a report via email:**
```python
from backend.honeypot import send_session_completion_report

success = send_session_completion_report("session-id-here")
```

**Check what's in a report:**
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

## 🚀 Key Functions

### `reportGen.session_report_generator`

| Function | Purpose |
|----------|---------|
| `generate_session_report(session_id)` | Main entry point - generates complete report |
| `get_session_data(session_id)` | Fetches session data from DB |
| `calculate_connection_duration(start, end)` | Formats duration as "1h 23m 45s" |
| `extract_browser_fingerprint(ua, headers)` | Parses browser/OS from headers |
| `format_command_history(commands)` | Formats commands with timestamps/responses |
| `get_attacker_profile(session_id)` | Runs ML profiler on commands |

### `backend.email_templates_report`

| Function | Purpose |
|----------|---------|
| `get_session_report_email_template(report)` | Creates (subject, html, text) tuple |

### `backend.honeypot`

| Function | Purpose |
|----------|---------|
| `send_session_completion_report(session_id)` | Generates + sends email report |
| `end_session(session_id)` | Enhanced - now sends report on logout |

## 🔌 Integration

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

## ⚙️ Configuration

No new configuration needed! Uses existing `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RECEIVER_EMAIL=security_team@company.com
```

**Reports automatically sent to**: `RECEIVER_EMAIL`

## 📧 Email Format

**Subject**: `Session Report: Attacker 192.168.1.100 - 1h 23m 45s session`

**Includes**:
- HTML version (pretty formatted)
- Plain text version (fallback)
- Both sent together (client chooses)

## 🧪 Quick Test

```bash
# 1. Check that attacker logs out
curl -X POST http://localhost:8000/portal/logout \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-123"}'

# 2. Check email for report (arrives in seconds)

# 3. Check logs for debug info
# Look for: "✅ Session completion report sent successfully"
```

## ⚠️ Important Notes

### Non-Breaking
- ✅ No database schema changes
- ✅ No new dependencies
- ✅ No impact on existing features
- ✅ Gracefully handles missing components
- ✅ Test sessions skip report generation

### Error Handling
- Email not configured? Logs warning, skips sending
- Profiler unavailable? Creates report without profile
- Session not found? Logs error, continues
- SMTP fails? Logs error, doesn't block logout

### Performance
- Report generation: async (doesn't block logout)
- Typically completes in 1-5 seconds
- Logout returns immediately to client

## 🔐 Security Considerations

- Reports contain **full command history** (sensitive!)
- Include **attacker IP and browser details**
- Sent via **SMTP with TLS encryption**
- Consider **email encryption** if needed
- **Store with restricted access**
- **Sanitize** before sharing outside team

## 📚 Full Documentation

See **docs/SESSION_REPORT_GUIDE.md** for:
- Detailed architecture
- All configuration options
- Troubleshooting guide
- Performance tuning
- Future enhancements

## 🎨 Customization Examples

### Change email subject line
Edit `backend/email_templates_report.py`:
```python
subject = f"Security Report: Session from {attacker_ip}"
```

### Add geolocation
Edit `reportGen/session_report_generator.py`:
```python
def get_geolocation(ip):
    # Call MaxMind or similar service
    return location_data
```

### Add to report
```python
report['geolocation'] = get_geolocation(session_data['ip_address'])
```

Then include in template:
```html
<div class="info-row">
    <div class="info-label">Location:</div>
    <div class="info-value">{geolocation['city']}</div>
</div>
```

## 📊 Example Report Email

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
Attacker IP: 203.45.67.89 (highlighted)
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

## 🐛 Debugging

### Enable verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test report generation
```python
from reportGen.session_report_generator import generate_session_report
import json

try:
    report = generate_session_report("session-id")
    print(json.dumps(report, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### Test email sending
```python
from backend.honeypot import send_session_completion_report

result = send_session_completion_report("session-id")
print(f"Email sent: {result}")
```

## 💡 Pro Tips

1. **Test report generation separately** before deploying to production
2. **Monitor email logs** to verify reports are being sent
3. **Keep ML model updated** for accurate profiling
4. **Archive reports** if you need to comply with regulations
5. **Use template variables** for customization across deployments

## 📞 Support Checklist

If reports aren't working:
- [ ] `.env` file has `SMTP_PASSWORD` (not empty)
- [ ] `RECEIVER_EMAIL` is set correctly
- [ ] Application logs show "✅ report sent successfully"
- [ ] ML model file exists in `attacker_profiler/model_store/`
- [ ] Test email works: `POST /test_honeypot_email`
- [ ] Attacker session has commands (empty sessions can't be profiled)

## 🎓 Next Steps

1. **Deploy** the new code to your environment
2. **Test** with a sample attacker session
3. **Monitor** email delivery and content
4. **Customize** templates if needed
5. **Archive** reports for compliance/analysis

---

**That's it!** The feature is ready to use. No additional setup needed beyond what you already have. 🎉
