#!/usr/bin/env python3
"""
Quick test script to verify model logging works correctly.
Run from honeypot-ai directory.
"""

import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['RETRAIN_MODE'] = 'skip'

from backend.main import on_startup
from datetime import datetime

print("=" * 70)
print(f"Testing Model Logging - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("=" * 70)
print()

print("Running startup sequence...")
on_startup()

print()
print("Checking for model_log.txt...")
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_log.txt")

if os.path.exists(log_file):
    print(f"✓ Log file found at: {log_file}")
    print()
    print("Log file contents:")
    print("-" * 70)
    with open(log_file, 'r') as f:
        print(f.read())
    print("-" * 70)
else:
    print(f"✗ Log file not found at: {log_file}")

print()
print("Test complete!")
