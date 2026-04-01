"""
Standalone test script to verify Gmail SMTP configuration works.
This bypasses the web server to test email directly.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "testcyber7274@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "testcyber7274@gmail.com")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "ashishroyblr@gmail.com")

print("=" * 60)
print("Gmail SMTP Test Script")
print("=" * 60)
print(f"SMTP Host: {SMTP_HOST}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"Username: {SMTP_USERNAME}")
print(f"Password: {'***' + SMTP_PASSWORD[-4:] if SMTP_PASSWORD else 'NOT SET'}")
print(f"From: {SENDER_EMAIL}")
print(f"To: {RECEIVER_EMAIL}")
print("=" * 60)

if not SMTP_PASSWORD:
    print("\n❌ ERROR: SMTP_PASSWORD is not set!")
    print("Please check your .env file.")
    exit(1)

# Create test email
message = MIMEMultipart('alternative')
message['Subject'] = "🧪 Test Email from Honeypot System"
message['From'] = f"Honeypot Security System <{SENDER_EMAIL}>"
message['To'] = RECEIVER_EMAIL
message['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

text_body = """
This is a test email from your Honeypot Security System.

If you're reading this, the Gmail SMTP configuration is working correctly!

Timestamp: {}
""".format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))

html_body = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #4CAF50;">✅ Test Email Successful!</h2>
    <p>This is a test email from your <strong>Honeypot Security System</strong>.</p>
    <p>If you're reading this, the Gmail SMTP configuration is working correctly!</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        Timestamp: {}<br>
        From: {}<br>
        To: {}
    </p>
</body>
</html>
""".format(
    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
    SENDER_EMAIL,
    RECEIVER_EMAIL
)

part1 = MIMEText(text_body, 'plain')
part2 = MIMEText(html_body, 'html')
message.attach(part1)
message.attach(part2)

# Send email
print("\n📧 Attempting to send test email...")
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        print("✓ Connected to SMTP server")
        
        server.starttls()
        print("✓ TLS started")
        
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✓ Authentication successful")
        
        server.send_message(message)
        print("✓ Email sent successfully")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Email sent to", RECEIVER_EMAIL)
    print("=" * 60)
    print("\nCheck your inbox (and spam folder) for the test email!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nPossible issues:")
    print("1. App Password is incorrect")
    print("2. 2-Factor Authentication not enabled")
    print("3. App Password not generated")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP error: {e}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
