#!/usr/bin/env python3
"""
Test script for checkpoint functionality
"""

import requests
import json
import time

def test_checkpoint_system():
    """Test the checkpoint system"""
    
    base_url = "https://llm-analysis-quiz-20q6.onrender.com"
    
    print("🧪 TESTING CHECKPOINT SYSTEM")
    print("=" * 50)
    
    # 1. Check if checkpoint exists
    print("\n1️⃣ Checking for existing checkpoint...")
    try:
        response = requests.get(f"{base_url}/checkpoint")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Checkpoint status: {data}")
            
            if data.get('exists'):
                checkpoint = data.get('checkpoint', {})
                print(f"📂 Found checkpoint at question {checkpoint.get('attempt', 'unknown')}")
                print(f"🔗 URL: {checkpoint.get('current_url', 'unknown')}")
                print(f"⏰ Saved: {time.ctime(checkpoint.get('timestamp', 0))}")
            else:
                print("📂 No checkpoint found")
        else:
            print(f"❌ Failed to check checkpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking checkpoint: {e}")
    
    # 2. Start quiz (will resume if checkpoint exists)
    print("\n2️⃣ Starting quiz (with auto-resume)...")
    try:
        quiz_data = {
            "email": "24ds2000137@ds.study.iitm.ac.in",
            "secret": "my-secret-123",
            "url": "https://tds-llm-analysis.s-anand.net/project2-reevals"
        }
        
        response = requests.post(f"{base_url}/quiz", json=quiz_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quiz started: {data}")
        else:
            print(f"❌ Failed to start quiz: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error starting quiz: {e}")
    
    print("\n3️⃣ Quiz is now running...")
    print("💡 TIP: The system will automatically resume from where it left off!")
    print("💡 TIP: Check logs at https://llm-analysis-quiz-20q6.onrender.com (Render dashboard)")
    
    # 4. Show how to clear checkpoint manually
    print("\n4️⃣ To clear checkpoint manually (if needed):")
    print("DELETE https://llm-analysis-quiz-20q6.onrender.com/checkpoint")
    print("\nOr use curl:")
    print("curl -X DELETE https://llm-analysis-quiz-20q6.onrender.com/checkpoint")

if __name__ == "__main__":
    test_checkpoint_system()
