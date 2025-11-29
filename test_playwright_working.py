#!/usr/bin/env python3
"""
Test that Playwright is working properly
"""
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_playwright_import():
    """Test that Playwright can be imported"""
    print("🎭 TESTING PLAYWRIGHT IMPORT")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright import successful!")
        return True
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
        return False

def test_playwright_browser_launch():
    """Test that Playwright can launch a browser"""
    print("\n🚀 TESTING PLAYWRIGHT BROWSER LAUNCH")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("🔧 Launching Chromium browser...")
            browser = p.chromium.launch(headless=True)
            print("✅ Browser launched successfully!")
            
            print("🌐 Creating new page...")
            page = browser.new_page()
            print("✅ Page created successfully!")
            
            print("📄 Navigating to test page...")
            page.goto("https://example.com")
            title = page.title()
            print(f"✅ Page loaded successfully! Title: {title}")
            
            browser.close()
            print("🔒 Browser closed successfully!")
            
        return True
        
    except Exception as e:
        print(f"❌ Playwright browser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_quiz_solver():
    """Test the full quiz solver with Playwright"""
    print("\n🎯 TESTING FULL QUIZ SOLVER WITH PLAYWRIGHT")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        import time
        
        solver = QuizSolver(
            email="test@ds.study.iitm.ac.in",
            secret="test-secret",
            start_time=time.time()
        )
        
        test_url = "https://tds-llm-analysis.s-anand.net/demo"
        print(f"🌐 Testing quiz page fetch: {test_url}")
        
        # This should now use Playwright directly
        result = solver.fetch_quiz_page(test_url)
        
        print(f"📊 QUIZ FETCH RESULT:")
        print(f"✅ Method used: {result.get('method', 'unknown')}")
        print(f"📄 Title: {result.get('title', 'No title')}")
        print(f"📏 Content length: {len(result.get('text', ''))}")
        
        # Check if Playwright was actually used
        if result.get('method') == 'playwright':
            print("🎉 SUCCESS: Playwright is working properly!")
            return True
        elif result.get('method') == 'requests_fallback':
            print("⚠️ WARNING: Fell back to requests (Playwright may have issues)")
            return False
        else:
            print("❓ UNCLEAR: Unknown method used")
            return False
            
    except Exception as e:
        print(f"❌ Quiz solver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Playwright tests"""
    
    print("🧪 COMPREHENSIVE PLAYWRIGHT TESTING")
    print("=" * 70)
    
    # Test 1: Import test
    import_ok = test_playwright_import()
    
    # Test 2: Browser launch test
    browser_ok = test_playwright_browser_launch()
    
    # Test 3: Full quiz solver test
    solver_ok = test_full_quiz_solver()
    
    print(f"\n📊 FINAL TEST RESULTS:")
    print(f"✅ Playwright Import: {'PASSED' if import_ok else 'FAILED'}")
    print(f"✅ Browser Launch: {'PASSED' if browser_ok else 'FAILED'}")
    print(f"✅ Quiz Solver: {'PASSED' if solver_ok else 'FAILED'}")
    
    if import_ok and browser_ok and solver_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Playwright is fully functional!")
        print(f"🚀 Ready for deployment!")
    else:
        print(f"\n⚠️ SOME TESTS FAILED")
        print(f"💡 Check the error messages above")
        
        if not import_ok:
            print("🔧 Install Playwright: pip install playwright")
        if import_ok and not browser_ok:
            print("🔧 Install browsers: playwright install chromium")

if __name__ == "__main__":
    main()
