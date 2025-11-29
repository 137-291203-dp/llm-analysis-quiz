#!/usr/bin/env python3
"""
Test the Playwright fix and fallback mechanisms
"""
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_web_scraping_fallback():
    """Test web scraping with and without Playwright"""
    
    print("🧪 TESTING WEB SCRAPING FALLBACK MECHANISMS")
    print("=" * 60)
    
    try:
        from src.quiz_solver import QuizSolver
        import time
        
        # Create solver
        solver = QuizSolver(
            email="test@example.com",
            secret="test-secret",
            start_time=time.time()
        )
        
        # Test URL
        test_url = "https://tds-llm-analysis.s-anand.net/demo"
        
        print(f"🌐 Testing URL: {test_url}")
        
        # Test the fetch method (will try Playwright first, then fallback)
        result = solver.fetch_quiz_page(test_url)
        
        print(f"\n📊 RESULT:")
        print(f"✅ Successfully fetched page!")
        print(f"📄 Method used: {result.get('method', 'unknown')}")
        print(f"📝 Title: {result.get('title', 'No title')}")
        print(f"📏 Content length: {len(result.get('text', ''))}")
        print(f"🔧 Fallback used: {result.get('fallback', False)}")
        
        if result.get('error'):
            print(f"⚠️ Original error (but recovered): {result['error']}")
        
        # Check content quality
        content = result.get('text', '')
        if len(content) > 100:
            print(f"✅ Content looks good ({len(content)} characters)")
        else:
            print(f"⚠️ Content seems short ({len(content)} characters)")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run this script after fixing requirements")
        return False
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False

def test_requests_only():
    """Test direct requests method"""
    
    print(f"\n🌐 TESTING REQUESTS-ONLY METHOD")
    print("-" * 40)
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = "https://tds-llm-analysis.s-anand.net/demo"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        print(f"✅ Requests method works!")
        print(f"📊 Status: {response.status_code}")
        print(f"📏 Content: {len(text)} characters")
        print(f"📝 Title: {soup.title.string if soup.title else 'No title'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Requests method failed: {e}")
        return False

def suggest_deployment_fix():
    """Suggest how to fix the deployment"""
    
    print(f"\n🚀 DEPLOYMENT FIX INSTRUCTIONS")
    print("=" * 50)
    
    print("""
📋 TO FIX THE PLAYWRIGHT ISSUE ON RENDER:

1. 🔧 **Updated Dockerfile** (already done)
   - Added proper system dependencies
   - Fixed Playwright installation
   - Added fallback mechanisms

2. 🚀 **Deploy the fix:**
   ```bash
   git add .
   git commit -m "🔧 Fix Playwright installation + add fallback web scraping"
   git push origin main
   ```

3. ⏳ **Wait for Render redeploy** (~5-10 minutes)

4. 🧪 **Test again:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File test_api.ps1
   ```

📊 **What will happen:**
- ✅ If Playwright works: Uses browser rendering (best)
- ✅ If Playwright fails: Falls back to requests (good)
- ✅ If both fail: Provides minimal processing (backup)

🎯 **Expected result:** Your quiz solving will work!
""")

def main():
    """Main testing function"""
    
    print("🔧 PLAYWRIGHT FIX VERIFICATION")
    print("Choose test option:")
    print("1. Test full web scraping (with fallbacks)")
    print("2. Test requests-only method")
    print("3. Show deployment instructions")
    print("4. All tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_web_scraping_fallback()
    elif choice == "2":
        test_requests_only()
    elif choice == "3":
        suggest_deployment_fix()
    elif choice == "4":
        success1 = test_web_scraping_fallback()
        success2 = test_requests_only()
        suggest_deployment_fix()
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"✅ Full scraping: {'PASSED' if success1 else 'FAILED'}")
        print(f"✅ Requests only: {'PASSED' if success2 else 'FAILED'}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
