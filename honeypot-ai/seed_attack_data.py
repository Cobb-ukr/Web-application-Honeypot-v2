#!/usr/bin/env python3
"""
Seed the database with sample attack data for ML model training.
Run this script to populate the database with realistic attack examples.
"""

import sys
import os
from datetime import datetime, timedelta
import json
import random

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, AttackLog, init_db

def seed_attack_data():
    """Add sample attack data to the database."""
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    # Sample attack payloads for different attack types
    attack_samples = [
        # SQL Injection attacks
        {
            "username": "' OR 1=1 --",
            "password": "anything",
            "attack_type": "SQLi",
            "threat_score": 5.0,
            "ip": "192.168.1.100"
        },
        {
            "username": "admin' OR '1'='1",
            "password": "test",
            "attack_type": "SQLi",
            "threat_score": 5.0,
            "ip": "10.0.0.50"
        },
        {
            "username": "' UNION SELECT NULL--",
            "password": "pass",
            "attack_type": "SQLi",
            "threat_score": 5.0,
            "ip": "172.16.0.25"
        },
        {
            "username": "admin'--",
            "password": "anything",
            "attack_type": "SQLi",
            "threat_score": 5.0,
            "ip": "192.168.2.10"
        },
        {
            "username": "' OR 'x'='x",
            "password": "test123",
            "attack_type": "SQLi",
            "threat_score": 5.0,
            "ip": "10.10.10.10"
        },
        
        # XSS attacks
        {
            "username": "<script>alert('XSS')</script>",
            "password": "test",
            "attack_type": "XSS",
            "threat_score": 4.0,
            "ip": "192.168.1.101"
        },
        {
            "username": "<img src=x onerror=alert(1)>",
            "password": "pass",
            "attack_type": "XSS",
            "threat_score": 4.0,
            "ip": "10.0.0.51"
        },
        {
            "username": "admin<script>alert(document.cookie)</script>",
            "password": "test",
            "attack_type": "XSS",
            "threat_score": 4.0,
            "ip": "172.16.0.26"
        },
        
        # Command Injection attacks
        {
            "username": "admin; ls -la",
            "password": "test",
            "attack_type": "CommandInjection",
            "threat_score": 5.0,
            "ip": "192.168.1.102"
        },
        {
            "username": "user && cat /etc/passwd",
            "password": "anything",
            "attack_type": "CommandInjection",
            "threat_score": 5.0,
            "ip": "10.0.0.52"
        },
        {
            "username": "test | whoami",
            "password": "pass",
            "attack_type": "CommandInjection",
            "threat_score": 5.0,
            "ip": "172.16.0.27"
        },
        
        # Path Traversal attacks
        {
            "username": "../../../etc/passwd",
            "password": "test",
            "attack_type": "PathTraversal",
            "threat_score": 4.0,
            "ip": "192.168.1.103"
        },
        {
            "username": "..\\..\\..\\windows\\system32",
            "password": "anything",
            "attack_type": "PathTraversal",
            "threat_score": 4.0,
            "ip": "10.0.0.53"
        },
        
        # Anomaly/High entropy attacks
        {
            "username": "xK9#mL@pQ2$vN8&wR5*tY1",
            "password": "random",
            "attack_type": "Anomaly",
            "threat_score": 3.5,
            "ip": "192.168.1.104"
        },
        {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "password": "test",
            "attack_type": "Anomaly",
            "threat_score": 3.0,
            "ip": "10.0.0.54"
        },
    ]
    
    # Check existing count
    existing_count = db.query(AttackLog).filter(
        AttackLog.attack_type != "Failed Login"
    ).filter(
        AttackLog.attack_type != "Successful Login"
    ).count()
    
    print(f"Current attack logs in database: {existing_count}")
    print(f"Adding {len(attack_samples)} sample attack logs...\n")
    
    # Add samples with varying timestamps (spread over last 30 days)
    added_count = 0
    for i, sample in enumerate(attack_samples):
        # Create timestamp (random time in last 30 days)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        # Create payload JSON
        payload = json.dumps({
            "username": sample["username"],
            "password": sample["password"],
            "full_payload": sample["username"]
        })
        
        # Create attack log entry
        log_entry = AttackLog(
            ip_address=sample["ip"],
            timestamp=timestamp,
            payload=payload,
            attack_type=sample["attack_type"],
            threat_score=sample["threat_score"],
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            endpoint="/auth/login",
            method="POST",
            headers=json.dumps({"user-agent": "Mozilla/5.0", "host": "localhost:8000"})
        )
        
        db.add(log_entry)
        added_count += 1
        print(f"✓ Added {sample['attack_type']} attack from {sample['ip']}: {sample['username'][:50]}")
    
    db.commit()
    db.close()
    
    print(f"\n{'='*70}")
    print(f"Successfully added {added_count} attack samples to the database!")
    print(f"Total attack logs now: {existing_count + added_count}")
    print(f"{'='*70}")
    print("\nYou can now restart the system with retraining enabled:")
    print("  RETRAIN_MODE=all python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    print("\nOr check the model log after restarting:")
    print("  cat logs/model_log.txt")

if __name__ == "__main__":
    print("="*70)
    print("ATTACK DATA SEEDING SCRIPT")
    print("="*70)
    print()
    
    try:
        seed_attack_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
