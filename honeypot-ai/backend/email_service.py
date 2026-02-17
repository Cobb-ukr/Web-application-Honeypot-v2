import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Ensure .env is loaded
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

from backend.email_config import EmailConfig
from backend.email_templates import get_honeypot_alert_template

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications via SMTP2GO"""
    
    def __init__(self):
        self.config = EmailConfig
        
    def send_honeypot_alert(self, session_data: Dict[str, Any]) -> bool:
        """
        Send honeypot alert email when a new session is detected.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.config.is_configured():
            logger.warning("Email not configured. Skipping alert notification.")
            return False
        
        try:
            # Generate email content
            subject, html_body, text_body = get_honeypot_alert_template(session_data)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.config.get_sender()
            message['To'] = self.config.get_receiver_email()
            message['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.config.get_smtp_host(), self.config.get_smtp_port(), timeout=self.config.TIMEOUT) as server:
                if self.config.USE_TLS:
                    server.starttls()
                
                server.login(self.config.get_smtp_username(), self.config.get_smtp_password())
                server.send_message(message)
            
            logger.info(f"Honeypot alert email sent successfully to {self.config.get_receiver_email()}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send honeypot alert email: {e}")
            return False
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test SMTP connection and authentication.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.config.is_configured():
            return False, "Email not configured. Please set SMTP_USERNAME and SMTP_PASSWORD."
        
        try:
            with smtplib.SMTP(self.config.get_smtp_host(), self.config.get_smtp_port(), timeout=self.config.TIMEOUT) as server:
                if self.config.USE_TLS:
                    server.starttls()
                
                server.login(self.config.get_smtp_username(), self.config.get_smtp_password())
            
            return True, "SMTP connection successful!"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check your SMTP username and password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

# Global instance
email_service = EmailNotificationService()
