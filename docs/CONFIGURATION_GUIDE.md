# Configuration Guide

Complete configuration guide for Gmail SMTP setup and terminal emulator customization.

---

## Table of Contents

1. [Gmail SMTP Setup](#gmail-smtp-setup)
   - [Quick Setup](#quick-setup-5-minutes)
   - [Step-by-Step Instructions](#step-by-step-instructions)
   - [Troubleshooting](#email-troubleshooting)
   - [Using Other Email Providers](#using-different-email-providers)
2. [Terminal Emulator](#terminal-emulator)
   - [How It Works](#how-it-works)
   - [Hardcoded Commands](#hardcoded-commands)
   - [LLM-Powered Commands](#llm-powered-commands)
   - [Blocked Patterns](#blocked-patterns)
   - [Configuration](#terminal-configuration)
   - [Testing](#testing-the-terminal-emulator)
   - [Customization](#terminal-customization)
   - [Performance](#performance-optimization)

---

## Gmail SMTP Setup

### Quick Setup (5 Minutes)

The honeypot system uses **Gmail SMTP** for sending session reports and email alerts. This guide walks you through the setup process.

---

### Step-by-Step Instructions

#### Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Sign in with your Gmail account (e.g., `your.email@gmail.com`)
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the prompts to enable it (you'll need your phone)

---

#### Step 2: Generate App Password

1. After enabling 2FA, go back to [Security Settings](https://myaccount.google.com/security)
2. Scroll down to "How you sign in to Google"
3. Click **App passwords** (you might need to sign in again)
4. In the "Select app" dropdown, choose **Mail**
5. In the "Select device" dropdown, choose **Other (Custom name)**
6. Type: `Honeypot System`
7. Click **Generate**
8. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)
   - Remove the spaces when you paste it: `abcdefghijklmnop`

---

#### Step 3: Create .env File

1. Copy the example file from the project root:
   ```bash
   cp honeypot-ai/.env.example honeypot-ai/.env
   ```

2. Edit `honeypot-ai/.env` and configure SMTP settings:
   ```env
   # Gmail SMTP Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your.email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password
   
   # Report Recipient
   RECEIVER_EMAIL=security.team@company.com
   
   # (Optional) Groq API for terminal emulation
   GROQ_API_KEY=your-groq-api-key
   ```

   Replace:
   - `your.email@gmail.com` - Your Gmail account
   - `your-16-character-app-password` - The app password from Step 2
   - `security.team@company.com` - Email to receive reports
   - `your-groq-api-key` - (Optional) For realistic terminal output

---

#### Step 4: Test Email Configuration

1. Start the honeypot server:
   ```bash
   cd honeypot-ai
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. Test the email endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/admin/test_email
   ```

3. Check your `RECEIVER_EMAIL` inbox for the test alert!

---

### Email Troubleshooting

#### "Authentication failed" error
- Make sure you're using the **App Password**, not your regular Gmail password
- Remove spaces from the app password
- Verify 2FA is enabled
- Ensure SMTP_USERNAME matches your Gmail account

#### "Less secure app access" message
- You don't need to enable "less secure apps" when using App Passwords
- App Passwords are the secure way to authenticate

#### Email not arriving
- Check spam folder in the receiver email
- Verify the RECEIVER_EMAIL is correct in `.env`
- Check server logs for SMTP error messages
- Try sending from Gmail to Gmail first (less likely to be blocked)

#### Timeout errors
- Check your internet connection
- Ensure firewall allows outbound connections to smtp.gmail.com:587
- Try increasing the SMTP timeout in email configuration

---

### Security Notes

✅ **Safe to use**: App Passwords are designed for this purpose  
✅ **Revocable**: You can revoke the app password anytime from Google Account settings  
✅ **No spam issues**: Gmail-to-Gmail emails rarely go to spam  
✅ **Encrypted**: SMTP uses TLS encryption (port 587)  
✅ **No plaintext**: Never store plaintext passwords in code

---

### What Happens Next

Once configured, the honeypot will automatically send emails when:
- A new attacker session is detected (optional)
- An attacker logs out of the honeypot (automatic)

Each email includes:
- Attacker's IP address and location details
- Session duration and connection times
- Browser fingerprint information
- Complete command execution history
- AI-generated attacker profile (skill level, intent)
- Professional HTML formatting

---

### Using Different Email Providers

The system is configured for Gmail, but you can use other providers:

| Provider | Server | Port | Notes |
|----------|--------|------|-------|
| Gmail | smtp.gmail.com | 587 | Recommended, no verification needed |
| Outlook | smtp-mail.outlook.com | 587 | Use your Outlook account |
| SendGrid | smtp.sendgrid.net | 587 | Requires API key |
| AWS SES | email-smtp.{region}.amazonaws.com | 587 | Requires AWS setup |

For each provider, follow their app password or API key generation process.

---

### Email Configuration Verification

To verify your email is working without a full honeypot session:

```python
# In Python shell or script
import os
from backend.email_service import send_email

# Send a test email
send_email(
    subject="Test Email - Honeypot System",
    html_body="<p>This is a test email from the honeypot system.</p>",
    text_body="This is a test email from the honeypot system."
)
```

If successful, you'll see a confirmation log message. Check your inbox!

---

### Next Steps

1. ✅ Set up Gmail 2FA and app password
2. ✅ Configure `.env` file with SMTP settings
3. ✅ Test email delivery
4. ✅ Deploy honeypot system
5. ✅ Monitor session reports in your inbox

For comprehensive setup instructions, see [README.md](../README.md) in the project root.

---

## Terminal Emulator

### Overview

The honeypot system includes a sophisticated **terminal emulator** that simulates a compromised Linux system. This guide explains how it works, how to customize it, and how to test it independently.

---

### How It Works

```
User Input (Terminal UI)
    ↓
Command Validation
    ├─ Check length (<200 chars)
    ├─ Check for control characters
    ├─ Check if hardcoded command
    ├─ Check if blocked pattern
    ↓
Response Generation
    ├─ If hardcoded → Return preset response (instant)
    └─ If allowed → Call Groq LLM API
    ↓
LLM Processing (Groq)
    ├─ Input: Command string
    ├─ Model: Groq inference engine
    ├─ Timeout: 5 seconds
    └─ Output: Simulated command response
    ↓
Post-Processing
    ├─ Remove markdown code fences
    ├─ Remove ANSI escape codes
    ├─ Normalize line endings
    ├─ Cap at 20 lines max
    └─ Remove fake bash errors
    ↓
Response Returned to Terminal UI
    ↓
Display to User
```

---

### Hardcoded Commands

These commands respond instantly without calling the LLM (fast and deterministic):

#### Basic Navigation
```bash
pwd                 # /root
cd /path            # Updates current directory
ls                  # List directory
ls -la              # Detailed listing
mkdir <dir>         # Creates directory
rm <file>           # Removes file
cat <file>          # Shows file content
echo <text>         # Prints text
```

#### System Information
```bash
whoami              # www-data
hostname            # honeypot-system
uname -a            # Linux honeypot 5.4.0
uptime              # Shows uptime
date                # Current date/time
ps                  # Process list
```

#### Utilities
```bash
help                # Shows available commands
clear               # Clears terminal
exit                # Logs out
grep <pattern>      # Pattern matching
head -n <N>         # First N lines
tail -n <N>         # Last N lines
```

**Advantage:** Instant response (milliseconds), no API calls needed

---

### LLM-Powered Commands

For other commands, the Groq LLM generates realistic output:

#### Examples
```bash
curl https://example.com                # LLM generates HTTP response
wget https://example.com/file.zip       # LLM generates download output
nc -l -p 4444                           # LLM simulates netcat listener
grep -r "pattern" /etc                  # LLM finds matching files
find / -name "*.key"                    # LLM lists matching files
tar -czf backup.tar.gz /home            # LLM simulates compression output
gcc -o program program.c                # LLM simulates compilation
python exploit.py                       # LLM simulates script execution
```

**Advantage:** Realistic, contextual responses; detects attacker intent

---

### Blocked Patterns

These commands are blocked to prevent problematic responses:

```bash
rm -rf /            # Destructive command
shutdown -h now     # System shutdown
reboot              # System restart
mkfs /dev/sda       # Format filesystem
dd if=/dev/zero of=/dev/sda     # Disk wipe
:(){ :|: &};        # Fork bomb
kill -9 1           # Kill init process
sync; sync; sync;   # System halt
```

When blocked, user sees:
```
Error: This command is not permitted
Reason: Destructive filesystem operation
```

---

### Terminal Configuration

#### Enable/Disable LLM

In `backend/terminal_emulator/command_filter.py`:

```python
# Set to False to disable LLM (use hardcoded responses only)
USE_LLM = True

# Groq API timeout in seconds
LLM_TIMEOUT = 5
```

#### Add Custom Hardcoded Command

In `backend/terminal_emulator/command_filter.py`:

```python
HARDCODED_RESPONSES = {
    "whoami": "www-data",
    "your_command": "your_response",  # Add here
    ...
}
```

#### Add Blocked Pattern

In `backend/terminal_emulator/command_filter.py`:

```python
BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",     # Existing pattern
    r"your_pattern_here", # Add here
    ...
]
```

---

### Testing the Terminal Emulator

#### Option 1: Test via Web Interface

1. Start the honeypot:
   ```bash
   cd honeypot-ai
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. Visit `http://localhost:8000/static/login.html`

3. Login as attacker and execute commands in the terminal

4. Observe responses

#### Option 2: Test Terminal HTML Directly

```bash
cd honeypot-ai/backend/terminal_emulator
python -m http.server 8000
```

Visit `http://localhost:8000/terminal.html`

**Note:** This tests the UI only, not the backend API

#### Option 3: Test via API

```bash
# Test a hardcoded command
curl -X POST http://localhost:8000/portal/execute \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "command": "whoami"
  }'

# Expected response:
# {"output": "www-data", "timestamp": "2024-02-22T18:30:45.123Z"}

# Test an LLM command
curl -X POST http://localhost:8000/portal/execute \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "command": "curl https://api.example.com/data"
  }'

# Expected response: (LLM-generated HTTP response)
# {"output": "HTTP/1.1 200 OK\n...", "timestamp": "..."}
```

---

### Filesystem State Management

#### How File State Works

The terminal tracks a simulated filesystem state:

```python
# State stored in: state_history/filesystem.json
{
    "/": {
        "dirs": ["home", "usr", "etc", "var", "opt"],
        "files": {"passwd": "content...", "hostname": "..."}
    },
    "/home/user": {
        "dirs": ["Desktop", "Documents"],
        "files": {"bashrc": "..."}
    }
}
```

#### Operations That Update State

```bash
mkdir <dir>                 # Adds directory to current path
rm <file>                   # Removes file
touch <file>                # Creates file
echo "text" >> file.txt     # Appends to file
cd <dir>                    # Changes current directory
```

#### Operations That Don't Update State

```bash
ls                          # Read-only
cat <file>                  # Read-only
grep <pattern>              # Read-only
ps                          # Read-only
whoami                      # Read-only
```

**Note:** For simplicity, only basic file operations update state. Complex operations (compilation, compression) are simulated without actual state changes.

---

### LLM Integration Details

#### Prompt Engineering

The system sends this prompt to Groq:

```
"Simulate realistic output for this Linux command:
 {user_command}
 
 Requirements:
 - Return ONLY the output, no explanations
 - Maximum 2000 characters
 - Realistic Linux system output
 - No markdown formatting
 - No code blocks (no ```bash```)"
```

#### Response Processing

```python
def process_llm_response(raw_response):
    # 1. Remove markdown code fences
    response = re.sub(r'```.*?```', '', raw_response, flags=re.DOTALL)
    
    # 2. Remove ANSI escape codes
    response = re.sub(r'\x1b\[[0-9;]*m', '', response)
    
    # 3. Split into lines and cap at 20
    lines = response.split('\n')[:20]
    
    # 4. Remove fake bash error lines
    lines = [l for l in lines if 'bash: line' not in l.lower()]
    
    # 5. Join back together
    return '\n'.join(lines)
```

#### Error Handling

```python
try:
    response = await call_groq_api(command, timeout=5)
    return process_response(response)
except TimeoutError:
    # Return generic response if timeout
    return "Command taking too long..."
except APIError:
    # Return error message if API fails
    return "Error: Command execution failed"
except Exception:
    # Catch-all: return hardcoded response
    return get_hardcoded_response(command)
```

---

### Terminal Customization

#### Example 1: Add Custom Command Response

```python
# In command_filter.py, add to HARDCODED_RESPONSES:

HARDCODED_RESPONSES = {
    ...
    "banner": """
╔═══════════════════════════════════════════╗
║  Welcome to the Honeypot System           ║
║  Unauthorized access is prohibited        ║
╚═══════════════════════════════════════════╝
    """,
    ...
}
```

#### Example 2: Block Additional Commands

```python
# In command_filter.py, add to BLOCKED_PATTERNS:

BLOCKED_PATTERNS = [
    ...
    r"format\s+[A-Z]:",          # Windows format command
    r"diskpart",                 # Windows disk partition tool
    r"cipher\s+/w:",             # Windows file wipe
    ...
]
```

#### Example 3: Disable LLM for Security

```python
# In command_filter.py, set:
USE_LLM = False

# Now only hardcoded commands work
# All others return: "Command not found"
```

---

### Performance Optimization

#### Current Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Hardcoded command | 10-50ms | Instant, no API calls |
| LLM command | 200-500ms | Includes Groq API latency |
| State update | 5-20ms | File I/O for filesystem |

#### Optimization Tips

1. **Prefer hardcoded commands**
   - Use common commands like `ls`, `pwd`, `whoami`
   - Avoid LLM for predictable output

2. **Cache LLM responses**
   - If same command called twice, return cached response
   - Reduces API calls and latency

3. **Async processing**
   - Run LLM calls asynchronously
   - Doesn't block terminal UI

4. **Batch commands**
   - Some commands could be combined for efficiency
   - E.g., `ls -la /etc && cat /etc/hostname` as single call

---

### Terminal Troubleshooting

#### Commands not returning output

**Check:**
1. Is LLM enabled? (`USE_LLM = True`)
2. Is Groq API key set? (`GROQ_API_KEY` in `.env`)
3. Is command blocked? (check `BLOCKED_PATTERNS`)
4. Check server logs for errors

**Fix:**
```bash
# Test Groq connectivity
python -c "from backend.terminal_emulator.command_filter import test_groq; test_groq()"
```

#### LLM responses too long

**Problem:** Responses exceed 20 lines and get truncated

**Solution:** Add to `HARDCODED_RESPONSES` for long-output commands

#### Slow command responses

**Problem:** LLM taking >5 seconds

**Solutions:**
1. Check internet connection
2. Increase timeout: `LLM_TIMEOUT = 10`
3. Check Groq API status
4. Use hardcoded response instead

#### Unrealistic output

**Problem:** LLM generating incorrect command output

**Improve Prompt:** Edit prompt in `command_filter.py` to be more specific

---

### Security Notes

✅ **Blocked commands:** Dangerous operations prevented  
✅ **Length limits:** Max 200 characters to prevent exploitation  
✅ **Control characters:** Stripped to prevent shell injection  
✅ **Timeout protection:** 5-second limit prevents hanging  
✅ **State isolation:** Each session has isolated filesystem state

---

## Summary

### Email Configuration
- ✅ Gmail SMTP setup with 2FA and app passwords
- ✅ Test email functionality
- ✅ Support for alternative email providers
- ✅ Comprehensive troubleshooting guide

### Terminal Emulator
- ✅ Realistic command responses (hardcoded or LLM-generated)
- ✅ Safe command execution (blocked dangerous operations)
- ✅ State tracking (simulated filesystem)
- ✅ Performance optimization (hardcoded for common commands)
- ✅ Full customization (add/remove commands, change behavior)

For advanced configuration, see the source code in:
- `honeypot-ai/backend/terminal_emulator/command_filter.py`
- `honeypot-ai/backend/terminal_emulator/state_manager.py`

For comprehensive technical details, see [full_project.md](full_project.md).
