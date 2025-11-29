#!/usr/bin/env python3
"""
Test script to see detailed LLM responses and reasoning
"""
import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('detailed_llm_logs.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_local_quiz_solving():
    """Test quiz solving with detailed logging"""
    
    print("🔬 DETAILED LLM TESTING WITH FULL LOGS")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.quiz_solver import QuizSolver
        
        # Validate config
        Config.validate()
        print(f"✅ Config valid - Using {Config.AIPIPE_TOKEN[:20]}...")
        
        # Create quiz solver
        solver = QuizSolver(
            email="24ds2000137@ds.study.iitm.ac.in",
            secret="my-secret-123", 
            start_time=time.time()
        )
        
        print(f"✅ Quiz solver created")
        
        # Test with demo quiz
        quiz_url = "https://tds-llm-analysis.s-anand.net/demo"
        print(f"\n🎯 Testing quiz: {quiz_url}")
        print("📝 This will show FULL LLM reasoning process...")
        
        # Solve quiz (this will show detailed logs)
        result = solver.solve_single_quiz(quiz_url)
        
        if result:
            print(f"\n🎉 QUIZ SOLVED SUCCESSFULLY!")
            print(f"📊 Result: {result}")
        else:
            print(f"\n❌ Quiz solving failed")
            
    except ImportError as e:
        print(f"❌ Import error (run locally): {e}")
        print("💡 Try: pip install -r requirements.txt")
    except Exception as e:
        print(f"💥 Error: {e}")

def show_render_logs_instructions():
    """Show how to access Render deployment logs"""
    
    print("\n" + "="*60)
    print("📊 HOW TO SEE LLM ANSWERS IN RENDER LOGS")
    print("="*60)
    
    print("""
🌐 **Method 1: Render Dashboard**
1. Go to: https://render.com/dashboard
2. Click on your service: "llm-analysis-quiz-20q6"
3. Click on "Logs" tab
4. You'll see real-time logs with LLM responses!

🖥️  **Method 2: Render CLI**
1. Install: npm install -g @render-tools/cli
2. Login: render auth login
3. Tail logs: render logs --service=llm-analysis-quiz-20q6 --tail

📱 **Method 3: Direct URL**
Visit: https://dashboard.render.com/web/srv-YOUR_SERVICE_ID/logs

🔍 **What to Look For in Logs:**
- 🤖 QUIZ PARSING PROMPT: Shows what question LLM sees
- 🤖 QUIZ PARSING RESPONSE: Shows how LLM understands the quiz  
- 🤖 RAW LLM ANSWER RESPONSE: Shows the exact answer LLM gives
- 🎯 FINAL PROCESSED ANSWER: Shows the final formatted answer

📊 **Example Log Output You'll See:**
```
🤖 QUIZ PARSING RESPONSE: {"question": "What is the mean of [1,2,3,4,5]?", "answer_format": "number"}
🤖 RAW LLM ANSWER RESPONSE: 3
🎯 FINAL PROCESSED ANSWER: 3 (type: int)
```
""")

def analyze_log_file():
    """Analyze the detailed log file if it exists"""
    
    log_file = "detailed_llm_logs.txt"
    
    if os.path.exists(log_file):
        print(f"\n📄 ANALYZING LOG FILE: {log_file}")
        print("-" * 40)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
                
            # Extract LLM interactions
            llm_responses = []
            lines = logs.split('\n')
            
            for line in lines:
                if 'RAW LLM ANSWER RESPONSE' in line:
                    llm_responses.append(line)
                    
            print(f"🤖 Found {len(llm_responses)} LLM responses:")
            for i, response in enumerate(llm_responses, 1):
                print(f"   {i}. {response.split('RAW LLM ANSWER RESPONSE: ')[1] if 'RAW LLM ANSWER RESPONSE: ' in response else response}")
                
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print(f"\n📄 No log file found yet. Run the local test first!")

def main():
    """Main function"""
    
    print("🔬 LLM RESPONSE ANALYZER")
    print("Choose an option:")
    print("1. Test locally with detailed logs")
    print("2. Show how to access Render logs")  
    print("3. Analyze local log file")
    print("4. All of the above")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_local_quiz_solving()
    elif choice == "2": 
        show_render_logs_instructions()
    elif choice == "3":
        analyze_log_file()
    elif choice == "4":
        test_local_quiz_solving()
        show_render_logs_instructions()
        analyze_log_file()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
