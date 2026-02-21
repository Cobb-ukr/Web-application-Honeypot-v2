#!/usr/bin/env python
"""
Test the 3-strike failed login behavior without needing requests.
Uses direct DB queries to simulate and verify the flow.
"""

import sys
import os
# Add the honeypot-ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'honeypot-ai'))

from backend.database import SessionLocal, User, ThreatScore, AttackLog
from backend.threat_scoring import scorer

def test_three_strikes():
    db = SessionLocal()
    
    # Setup: Create a test user
    test_ip = "192.168.1.100"
    test_user = "testuser"
    test_password = "correct123"
    
    # Remove any existing test user
    db.query(User).filter(User.username == test_user).delete()
    db.query(ThreatScore).filter(ThreatScore.ip_address == test_ip).delete()
    db.commit()
    
    # Create test user
    new_user = User(username=test_user, password_hash=test_password, role="user")
    db.add(new_user)
    db.commit()
    
    print("=" * 60)
    print("TEST: 3-Strike Failed Login Behavior")
    print("=" * 60)
    
    # Simulate 3 failed login attempts
    for attempt in range(1, 4):
        print(f"\n--- Failed Login Attempt {attempt} ---")
        
        # Simulate failed login: track the attempt and check if it's the 3rd strike
        is_third_strike = scorer.track_failed_login(db, test_ip)
        
        if is_third_strike:
            # 3rd strike: update threat score
            current_score = scorer.update_score(db, test_ip, 3.0, "Brute Force Attempt")
        else:
            # Not 3rd strike yet: don't update score, just get current
            threat_entry = db.query(ThreatScore).filter(ThreatScore.ip_address == test_ip).first()
            current_score = threat_entry.score if threat_entry else 0.0
        
        # Check if should_redirect (threshold is 3.0)
        should_trap = scorer.should_redirect(db, test_ip)
        
        print(f"IP: {test_ip}")
        print(f"Current Score: {current_score}")
        print(f"Should Redirect to Honeypot: {should_trap}")
        print(f"Is 3rd Strike: {is_third_strike}")
        
        if attempt < 3:
            assert not should_trap, f"Attempt {attempt}: Should NOT be trapped yet!"
            print(f"✓ Correctly NOT trapped on attempt {attempt}")
        else:
            assert should_trap, f"Attempt {attempt}: Should be trapped now!"
            print(f"✓ Correctly trapped on attempt {attempt}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED: 3-strike behavior is correct!")
    print("=" * 60)
    
    # Cleanup
    db.query(User).filter(User.username == test_user).delete()
    db.query(ThreatScore).filter(ThreatScore.ip_address == test_ip).delete()
    db.commit()
    db.close()

if __name__ == "__main__":
    test_three_strikes()
