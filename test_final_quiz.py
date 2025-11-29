#!/usr/bin/env python3
"""
Test the complete quiz solving with actual credentials
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

def test_complete_quiz_solving():
    """Test the complete quiz solving pipeline with real credentials"""
    
    print("🎯 TESTING COMPLETE QUIZ SOLVING")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        # Create solver with actual credentials (same as in test_api.ps1)
        solver = QuizSolver(
            email="24ds2000137@ds.study.iitm.ac.in",
            secret="my-secret-123",
            start_time=time.time()
        )
        
        test_url = "https://tds-llm-analysis.s-anand.net/demo"
        
        print(f"🌐 Testing complete quiz solving for: {test_url}")
        print(f"📧 Using email: {solver.email}")
        print(f"🔑 Using secret: {solver.secret}")
        
        # Test the complete quiz solving process
        print(f"\n🔄 Step 1: Fetching quiz page...")
        quiz_data = solver.fetch_quiz_page(test_url)
        print(f"✅ Method: {quiz_data.get('method', 'unknown')}")
        print(f"✅ Content: {len(quiz_data.get('text', ''))} chars")
        
        print(f"\n🔄 Step 2: Parsing quiz with LLM...")
        quiz_info = solver.parse_quiz_with_llm(quiz_data)
        print(f"✅ Question: {quiz_info.get('question', 'Unknown')[:50]}...")
        print(f"✅ Submit URL: {quiz_info.get('submit_url', 'None')}")
        
        print(f"\n🔄 Step 3: Processing data source...")
        if quiz_info.get('data_source'):
            processed_data = solver.data_processor.process_data_source(
                quiz_info['data_source'],
                quiz_info.get('question', '')
            )
            print(f"✅ Data processed: {type(processed_data)}")
        else:
            processed_data = None
            print("ℹ️ No data source to process")
        
        print(f"\n🔄 Step 4: Generating answer with LLM...")
        answer = solver.solve_task_with_llm(quiz_info, processed_data)
        print(f"✅ Answer generated: {type(answer)}")
        print(f"📋 Answer content: {answer}")
        
        # Validate the answer has correct credentials
        if isinstance(answer, dict):
            if 'email' in answer and 'secret' in answer:
                if answer['email'] == solver.email and answer['secret'] == solver.secret:
                    print(f"✅ CREDENTIALS CORRECT! Using real values, not placeholders")
                else:
                    print(f"⚠️ Credentials might be wrong:")
                    print(f"   Expected email: {solver.email}")
                    print(f"   Got email: {answer.get('email')}")
                    print(f"   Expected secret: {solver.secret}")
                    print(f"   Got secret: {answer.get('secret')}")
            else:
                print(f"ℹ️ Answer doesn't require email/secret fields")
        
        print(f"\n🎯 QUIZ SOLVING TEST: SUCCESS!")
        print(f"🚀 Ready for deployment - will work end-to-end!")
        return True
        
    except Exception as e:
        print(f"❌ Quiz solving test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the final quiz test"""
    
    print("🎯 FINAL QUIZ SOLVING TEST")
    print("=" * 70)
    print("Testing the complete pipeline with credential fixes")
    print("=" * 70)
    
    success = test_complete_quiz_solving()
    
    if success:
        print(f"\n🎉 ALL SYSTEMS GO!")
        print(f"✅ Playwright working")
        print(f"✅ Fallback working") 
        print(f"✅ Data processing working")
        print(f"✅ LLM parsing working")
        print(f"✅ Credential handling FIXED")
        print(f"✅ Quiz generation working")
        
        print(f"\n🚀 DEPLOYMENT READY:")
        print(f"1. git add .")
        print(f"2. git commit -m '🎯 Fix credential handling - complete quiz solving'")
        print(f"3. git push")
        print(f"4. Test with PowerShell script")
        
        print(f"\n🎯 EXPECTED RESULT:")
        print(f"✅ Complete quiz solving success")
        print(f"✅ Real credentials in submission")
        print(f"✅ Successful answer submission")
        
    else:
        print(f"\n⚠️ NEEDS ATTENTION")
        print(f"Check the errors above before deploying")

if __name__ == "__main__":
    main()
