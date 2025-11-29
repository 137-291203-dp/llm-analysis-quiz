"""
Test script for Swagger API endpoints
"""
import requests
import json
import sys
import os
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config import Config

def test_swagger_health(base_url):
    """Test the health check endpoint"""
    print("\n=== Testing Swagger Health Check ===")
    try:
        response = requests.get(f"{base_url}/api/v1/quiz/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_swagger_solve_valid(base_url):
    """Test solving endpoint with valid credentials"""
    print("\n=== Testing Swagger Solve (Valid) ===")
    try:
        payload = {
            "email": Config.STUDENT_EMAIL,
            "secret": Config.STUDENT_SECRET,
            "url": "https://tds-llm-analysis.s-anand.net/demo"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/quiz/solve",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_swagger_solve_invalid_secret(base_url):
    """Test with invalid secret"""
    print("\n=== Testing Swagger Solve (Invalid Secret) ===")
    try:
        payload = {
            "email": Config.STUDENT_EMAIL,
            "secret": "wrong-secret",
            "url": "https://example.com/quiz"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/quiz/solve",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 403
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_swagger_docs(base_url):
    """Test Swagger documentation accessibility"""
    print("\n=== Testing Swagger Documentation ===")
    try:
        response = requests.get(f"{base_url}/docs/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
            print(f"🌐 Open in browser: {base_url}/docs/")
            return True
        else:
            print("❌ Swagger UI not accessible")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_legacy_compatibility(base_url):
    """Test legacy /quiz endpoint compatibility"""
    print("\n=== Testing Legacy Compatibility ===")
    try:
        payload = {
            "email": Config.STUDENT_EMAIL,
            "secret": Config.STUDENT_SECRET,
            "url": "https://tds-llm-analysis.s-anand.net/demo"
        }
        
        response = requests.post(
            f"{base_url}/quiz",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_server_running(base_url):
    """Check if server is running"""
    try:
        response = requests.get(base_url, timeout=5)
        return True
    except:
        return False

def main():
    """Run all Swagger API tests"""
    
    # Load config
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your .env file correctly")
        sys.exit(1)
    
    # Get base URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = f"http://localhost:{Config.PORT}"
    
    print("🧪 Testing Swagger API Endpoints")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Email: {Config.STUDENT_EMAIL}")
    
    if Config.use_aipipe():
        print(f"🆓 LLM Provider: AI Pipe (FREE)")
    else:
        print(f"💳 LLM Provider: OpenAI (PAID)")
    
    # Check if server is running
    if not check_server_running(base_url):
        print(f"\n❌ Server not running at {base_url}")
        print("Please start the server first:")
        print("  python app_with_swagger.py")
        print("  or")
        print("  python run_local.py")
        sys.exit(1)
    
    print("\n✅ Server is running")
    
    # Run tests
    results = {
        "Swagger Health Check": test_swagger_health(base_url),
        "Swagger Solve (Valid)": test_swagger_solve_valid(base_url),
        "Swagger Solve (Invalid Secret)": test_swagger_solve_invalid_secret(base_url),
        "Swagger Documentation": test_swagger_docs(base_url),
        "Legacy Compatibility": test_legacy_compatibility(base_url)
    }
    
    # Print summary
    print("\n" + "="*60)
    print("🧪 SWAGGER API TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Swagger API tests passed!")
        print(f"\n🌐 Access Swagger UI at: {base_url}/docs/")
        print(f"🔗 API endpoints at: {base_url}/api/v1/")
        print(f"📊 Health check at: {base_url}/api/v1/quiz/health")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
