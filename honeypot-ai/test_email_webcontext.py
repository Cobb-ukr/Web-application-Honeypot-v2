"""
Simple script to test if email service works when imported in web server context
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.email_service import email_service
from backend.email_config import EmailConfig
from datetime import datetime

print("=" * 60)
print("Testing Email Service in Web Server Context")
print("=" * 60)

# Check configuration
print(f"\nEmail Configuration:")
print(f"  SMTP Host: {EmailConfig.get_smtp_host()}")
print(f"  SMTP Port: {EmailConfig.get_smtp_port()}")
print(f"  Username: {EmailConfig.get_smtp_username()}")
print(f"  Password: {'***' if EmailConfig.get_smtp_password() else 'NOT SET'}")
print(f"  Is Configured: {EmailConfig.is_configured()}")

if not EmailConfig.is_configured():
    print("\n❌ Email is NOT configured!")
    print("Environment variables are not being loaded correctly.")
    exit(1)

# Test connection
print("\n📧 Testing SMTP connection...")
success, message = email_service.test_connection()
print(f"Result: {message}")

if not success:
    print("\n❌ SMTP connection failed!")
    exit(1)

# Send test alert
print("\n📧 Sending test honeypot alert...")
test_session_data = {
    'ip_address': '192.168.1.100',
    'session_id': 'test-web-context-12345',
    'timestamp': datetime.utcnow(),
    'user_agent': 'Mozilla/5.0 (Test Browser)',
    'location': 'Test Location'
}

result = email_service.send_honeypot_alert(test_session_data)

if result:
    print("\n✅ SUCCESS! Email sent from web server context!")
else:
    print("\n❌ FAILED! Email could not be sent from web server context!")

print("=" * 60)
