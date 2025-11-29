#!/usr/bin/env python3
"""
Test runner script
"""
import sys
import os
import subprocess

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("Running LLM Analysis Quiz Tests")
    
    test_files = [
        'tests/test_swagger.py',
        'tests/test_endpoint.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}")
            result = subprocess.run([sys.executable, test_file], cwd='.')
            if result.returncode != 0:
                print(f"FAILED: {test_file}")
            else:
                print(f"PASSED: {test_file}")
