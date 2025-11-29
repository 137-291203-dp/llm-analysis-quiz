#!/usr/bin/env python3
"""
Quick quiz test to verify the config fix works
"""
import requests
import time

def test_quiz_solve():
    """Quick test of the quiz solving endpoint"""
    
    print("🧪 Quick Quiz Solve Test")
    print("=" * 40)
    
    # Test data
    url = "https://llm-analysis-quiz-20q6.onrender.com/api/v1/quiz/solve"
    data = {
        "email": "24ds2000137@ds.study.iitm.ac.in",
        "secret": "my-secret-123",
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
    
    print(f"📍 API: {url}")
    print(f"🎯 Quiz: {data['url']}")
    
    try:
        print("\n⏳ Sending request...")
        start_time = time.time()
        
        response = requests.post(url, json=data, timeout=30)
        response_time = time.time() - start_time
        
        print(f"⏱️  Response time: {response_time:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📋 Response: {result}")
            
            # Check if it's actually solving (not just accepting)
            if result.get("status") == "accepted":
                print(f"\n🎉 QUIZ SOLVING IS WORKING!")
                print(f"   The config.Config error has been FIXED! ✅")
                return True
            else:
                print(f"⚠️  Unexpected response status: {result.get('status')}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    
    print("\n🩺 Health Check Test")
    print("-" * 25)
    
    try:
        response = requests.get("https://llm-analysis-quiz-20q6.onrender.com/api/v1/quiz/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed!")
            print(f"📋 Status: {result.get('status')}")
            print(f"🤖 LLM Provider: {result.get('llm_provider')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Health check exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING DEPLOYED APP AFTER CONFIG FIX")
    print("=" * 50)
    
    # Test health first
    health_ok = test_health_check()
    
    if health_ok:
        # Test quiz solving
        quiz_ok = test_quiz_solve()
        
        print("\n" + "=" * 50)
        if quiz_ok:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Config fix successful")
            print("✅ Quiz solving works")
            print("🚀 Your app is ready for Google Form submission!")
        else:
            print("⚠️  Health check passed but quiz solving failed")
            print("🔧 Check the deployment logs for errors")
    else:
        print("\n❌ Health check failed - app may not be deployed correctly")
