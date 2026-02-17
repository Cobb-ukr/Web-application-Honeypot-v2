import os
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded when this module is imported
# Get the project root directory (parent of backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

class EmailConfig:
    """Email configuration for Gmail SMTP"""
    
    @classmethod
    def get_smtp_host(cls) -> str:
        return os.getenv("SMTP_HOST", "smtp.gmail.com")
    
    @classmethod
    def get_smtp_port(cls) -> int:
        return int(os.getenv("SMTP_PORT", "587"))
    
    @classmethod
    def get_smtp_username(cls) -> str:
        return os.getenv("SMTP_USERNAME", "testcyber7274@gmail.com")
    
    @classmethod
    def get_smtp_password(cls) -> str:
        return os.getenv("SMTP_PASSWORD", "")
    
    @classmethod
    def get_sender_email(cls) -> str:
        return os.getenv("SENDER_EMAIL", "testcyber7274@gmail.com")
    
    @classmethod
    def get_sender_name(cls) -> str:
        return os.getenv("SENDER_NAME", "Honeypot Security System")
    
    @classmethod
    def get_receiver_email(cls) -> str:
        return os.getenv("RECEIVER_EMAIL", "ashishroyblr@gmail.com")
    
    # Backward compatibility properties
    @property
    def SMTP_HOST(self):
        return self.get_smtp_host()
    
    @property
    def SMTP_PORT(self):
        return self.get_smtp_port()
    
    @property
    def SMTP_USERNAME(self):
        return self.get_smtp_username()
    
    @property
    def SMTP_PASSWORD(self):
        return self.get_smtp_password()
    
    @property
    def SENDER_EMAIL(self):
        return self.get_sender_email()
    
    @property
    def SENDER_NAME(self):
        return self.get_sender_name()
    
    @property
    def RECEIVER_EMAIL(self):
        return self.get_receiver_email()
    
    USE_TLS = True
    TIMEOUT = 10  # seconds
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if email is properly configured"""
        import logging
        logger = logging.getLogger(__name__)
        
        username = cls.get_smtp_username()
        password = cls.get_smtp_password()
        
        logger.info(f"EmailConfig.is_configured() - Username: {username}, Password: {'***' if password else 'EMPTY'}")
        
        return bool(username and password)
    
    @classmethod
    def get_sender(cls) -> str:
        """Get formatted sender address"""
        return f"{cls.get_sender_name()} <{cls.get_sender_email()}>"
