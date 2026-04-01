import requests
import json
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'honeypot-ai'))
from backend.database import AttackLog, DATABASE_URL

API_URL = "http://localhost:8000"

def test():
    # 1. Register
    reg_data = {"username": "debug_user", "password": "password123"}
    try:
        requests.post(f"{API_URL}/auth/register", data=reg_data)
    except:
        pass # Might already exist

    # 2. Login
    login_data = {"username": "debug_user", "password": "password123"}
    res = requests.post(f"{API_URL}/auth/login", data=login_data)
    print(f"Login Response: {res.status_code}")

    # 3. Check DB
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    last_log = db.query(AttackLog).order_by(AttackLog.id.desc()).first()
    print(f"Last Log ID: {last_log.id}")
    print(f"Last Log Type: '{last_log.attack_type}'")
    
    if last_log.attack_type == "Successful Login":
        print("SUCCESS: Logic is working.")
    else:
        print("FAILURE: Logic failed to tag as Successful Login.")

if __name__ == "__main__":
    test()
