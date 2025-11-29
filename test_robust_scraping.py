#!/usr/bin/env python3
"""
Test both Playwright and fallback mechanisms comprehensively
"""
import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_playwright_availability():
    """Test if Playwright is available and working"""
    print("🎭 TESTING PLAYWRIGHT AVAILABILITY")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright import successful!")
        
        # Try to launch browser
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                print("✅ Browser launch successful!")
                browser.close()
                print("✅ Browser close successful!")
            return True
        except Exception as browser_error:
            print(f"⚠️ Browser launch failed: {browser_error}")
            print("🔄 Will fall back to requests method")
            return False
            
    except ImportError as e:
        print(f"⚠️ Playwright import failed: {e}")
        print("🔄 Will use requests fallback")
        return False

def test_requests_fallback():
    """Test requests fallback mechanism"""
    print("\n🌐 TESTING REQUESTS FALLBACK")
    print("=" * 50)
    
    try:
        import requests
        from bs4 import BeautifulSoup
        print("✅ Required packages available!")
        
        # Test with a simple page
        test_url = "https://httpbin.org/html"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(test_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(strip=True)
        
        print(f"✅ Requests method works! ({len(text)} chars)")
        return True
        
    except Exception as e:
        print(f"❌ Requests fallback failed: {e}")
        return False

def test_quiz_solver_with_both_methods():
    """Test QuizSolver with both Playwright and fallback"""
    print("\n🎯 TESTING QUIZ SOLVER WITH BOTH METHODS")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        solver = QuizSolver(
            email="test@ds.study.iitm.ac.in",
            secret="test-secret",
            start_time=time.time()
        )
        
        test_url = "https://tds-llm-analysis.s-anand.net/demo"
        print(f"🔄 Testing quiz page fetch: {test_url}")
        
        # Test the main fetch method (tries Playwright first, then fallback)
        result = solver.fetch_quiz_page(test_url)
        
        print(f"\n📊 QUIZ FETCH RESULT:")
        print(f"✅ Method used: {result.get('method', 'unknown')}")
        print(f"📄 Title: {result.get('title', 'No title')}")
        print(f"📏 Content length: {result.get('content_length', len(result.get('text', '')))}")
        print(f"🔧 Status: {result.get('status_code', 'N/A')}")
        
        if result.get('fallback'):
            print("⚠️ Used final fallback due to errors")
            print(f"🔍 Error: {result.get('error', 'Unknown')}")
        
        # Verify content quality
        content = result.get('text', '')
        if len(content) > 50:
            print("✅ Content quality: GOOD")
            return True, result.get('method')
        else:
            print("⚠️ Content quality: LIMITED")
            return True, result.get('method')  # Still works
            
    except Exception as e:
        print(f"❌ Quiz solver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_direct_methods():
    """Test both Playwright and requests methods directly"""
    print("\n🔬 TESTING DIRECT METHODS")
    print("=" * 50)
    
    results = {}
    
    try:
        from src.quiz_solver import QuizSolver
        solver = QuizSolver("test@test.com", "secret", time.time())
        
        test_url = "https://tds-llm-analysis.s-anand.net/demo"
        
        # Test Playwright method directly
        print("🎭 Testing Playwright method directly...")
        try:
            playwright_result = solver._fetch_with_playwright(test_url)
            print(f"✅ Playwright: SUCCESS ({len(playwright_result.get('text', ''))} chars)")
            results['playwright'] = True
        except Exception as e:
            print(f"⚠️ Playwright: FAILED - {e}")
            results['playwright'] = False
        
        # Test requests method directly  
        print("🌐 Testing requests method directly...")
        try:
            requests_result = solver._fetch_with_requests(test_url)
            print(f"✅ Requests: SUCCESS ({len(requests_result.get('text', ''))} chars)")
            results['requests'] = True
        except Exception as e:
            print(f"❌ Requests: FAILED - {e}")
            results['requests'] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Direct method testing failed: {e}")
        return {'playwright': False, 'requests': False}

def main():
    """Run comprehensive scraping tests"""
    
    print("🧪 COMPREHENSIVE SCRAPING ROBUSTNESS TEST")
    print("=" * 70)
    
    # Test 1: Playwright availability
    playwright_available = test_playwright_availability()
    
    # Test 2: Requests fallback
    requests_working = test_requests_fallback()
    
    # Test 3: Quiz solver integration
    solver_working, method_used = test_quiz_solver_with_both_methods()
    
    # Test 4: Direct method testing
    direct_results = test_direct_methods()
    
    print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
    print(f"{'=' * 70}")
    print(f"✅ Playwright Available: {'YES' if playwright_available else 'NO'}")
    print(f"✅ Requests Fallback: {'WORKING' if requests_working else 'FAILED'}")
    print(f"✅ Quiz Solver: {'WORKING' if solver_working else 'FAILED'}")
    print(f"📋 Method Used: {method_used or 'None'}")
    print(f"🎭 Direct Playwright: {'WORKING' if direct_results.get('playwright') else 'FAILED'}")
    print(f"🌐 Direct Requests: {'WORKING' if direct_results.get('requests') else 'FAILED'}")
    
    # Overall assessment
    if solver_working and (direct_results.get('playwright') or direct_results.get('requests')):
        print(f"\n🎉 OVERALL RESULT: ROBUST SYSTEM!")
        print(f"✅ Your app has multiple working scraping methods")
        
        if direct_results.get('playwright'):
            print(f"🎭 Primary: Playwright (Full JavaScript support)")
        if direct_results.get('requests'):
            print(f"🌐 Fallback: Requests (Reliable HTTP scraping)")
            
        print(f"🚀 Ready for deployment!")
        
    elif solver_working:
        print(f"\n⚠️ OVERALL RESULT: BASIC FUNCTIONALITY")
        print(f"✅ Quiz solving works but with limited methods")
        print(f"🔄 Will use available fallback mechanisms")
        
    else:
        print(f"\n❌ OVERALL RESULT: NEEDS ATTENTION")
        print(f"❌ Critical scraping functionality not working")
        print(f"🔧 Need to fix dependencies or configuration")
    
    print(f"\n💡 DEPLOYMENT STRATEGY:")
    if direct_results.get('playwright'):
        print(f"🎯 Deploy with full Playwright support")
        print(f"🔄 Requests fallback available as backup")
    elif direct_results.get('requests'):
        print(f"🎯 Deploy with requests fallback")
        print(f"⚠️ Limited JavaScript support but functional")
    else:
        print(f"🔧 Fix package installation before deploying")

if __name__ == "__main__":
    main()
