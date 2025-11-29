"""
Test script for API endpoints
"""
import requests
import json
import time
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config import Config

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_valid_request(base_url):
    """Test with valid credentials"""
    print("\n=== Testing Valid Request ===")
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

def test_invalid_secret(base_url):
    """Test with invalid secret (should return 403)"""
    print("\n=== Testing Invalid Secret ===")
    try:
        payload = {
            "email": Config.STUDENT_EMAIL,
            "secret": "wrong-secret",
            "url": "https://example.com/quiz"
        }
        
        response = requests.post(
            f"{base_url}/quiz",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 403
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_json(base_url):
    """Test with invalid JSON (should return 400)"""
    print("\n=== Testing Invalid JSON ===")
    try:
        response = requests.post(
            f"{base_url}/quiz",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_missing_fields(base_url):
    """Test with missing required fields (should return 400)"""
    print("\n=== Testing Missing Fields ===")
    try:
        payload = {
            "email": Config.STUDENT_EMAIL
            # Missing secret and url
        }
        
        response = requests.post(
            f"{base_url}/quiz",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
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
    
    print(f"Testing endpoint: {base_url}")
    print(f"Email: {Config.STUDENT_EMAIL}")
    
    # Run tests
    results = {
        "Health Check": test_health_check(base_url),
        "Valid Request": test_valid_request(base_url),
        "Invalid Secret": test_invalid_secret(base_url),
        "Invalid JSON": test_invalid_json(base_url),
        "Missing Fields": test_missing_fields(base_url)
    }
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
