import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "honeypot.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user") # user, admin

class AttackLog(Base):
    __tablename__ = "attack_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    payload = Column(String, nullable=True) # The malicious payload if any
    attack_type = Column(String) # SQLi, XSS, CommandInjection, SuspiciousActivity, etc.
    threat_score = Column(Float)
    user_agent = Column(String)
    endpoint = Column(String)
    method = Column(String)
    headers = Column(String) # Store JSON string of headers

class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ThreatScore(Base):
    __tablename__ = "threat_scores"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class AttackSignature(Base):
    __tablename__ = "attack_signatures"
    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String, unique=True)
    type = Column(String) # SQLi, XSS, Cmd
    description = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
