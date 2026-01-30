#!/usr/bin/env python3
"""
Comprehensive test to demonstrate model logging with different retraining modes.
Run from honeypot-ai directory.
"""

import os
import sys
import subprocess

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_for_mode(mode):
    """Run the startup sequence for a specific retraining mode."""
    print(f"\n{'='*70}")
    print(f"Testing RETRAIN_MODE={mode}")
    print(f"{'='*70}\n")
    
    # Set environment variable and run Python
    env = os.environ.copy()
    env['RETRAIN_MODE'] = mode
    
    result = subprocess.run(
        [sys.executable, 'test_model_logging.py'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=env,
        capture_output=True,
        text=True
    )
    
    # Show only the log file output
    lines = result.stdout.split('\n')
    in_log_section = False
    for line in lines:
        if 'Log file contents:' in line:
            in_log_section = True
        if in_log_section and line.startswith('-'):
            break
        if in_log_section:
            print(line)
    
    if in_log_section:
        # Show the actual log
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_log.txt")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                print(f.read())
    
    print()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("MODEL RETRAINING LOGGING - COMPREHENSIVE TEST")
    print("="*70)
    
    # Test all three modes
    for mode in ['skip', 'all', 'recent']:
        run_test_for_mode(mode)
    
    print("="*70)
    print("All tests completed!")
    print("="*70)
    print("\nNote: The model_log.txt file is overwritten with each test.")
    print("This demonstrates that each startup generates a fresh log.")
