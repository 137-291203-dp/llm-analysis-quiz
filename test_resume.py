#!/usr/bin/env python3
"""
Test resume functionality with a real quiz
"""

import time
from src.quiz_solver import QuizSolver

def test_resume_functionality():
    """Test the resume functionality"""
    
    print("🔄 TESTING RESUME FUNCTIONALITY")
    print("=" * 50)
    
    # Create solver
    solver = QuizSolver(
        email="24ds2000137@ds.study.iitm.ac.in",
        secret="my-secret-123",
        start_time=time.time()
    )
    
    # 1. Clear any existing checkpoint
    print("1️⃣ Clearing any existing checkpoint...")
    solver.clear_checkpoint()
    
    # 2. Create a fake checkpoint as if we stopped at question 3
    print("2️⃣ Creating fake checkpoint (as if stopped at question 3)...")
    fake_checkpoint_url = "https://tds-llm-analysis.s-anand.net/project2-reevals-3?email=24ds2000137%40ds.study.iitm.ac.in&id=101667"
    fake_progress = {
        'last_correct': True,
        'last_reason': '',
        'questions_completed': 3
    }
    solver.save_checkpoint(fake_checkpoint_url, 3, fake_progress)
    
    # 3. Test the solve_quiz_chain method with resume
    print("3️⃣ Testing solve_quiz_chain with resume...")
    print("   This should detect the checkpoint and resume from question 3")
    
    # Start the quiz chain - it should resume from the checkpoint
    initial_url = "https://tds-llm-analysis.s-anand.net/project2-reevals"
    
    print(f"\n🚀 Starting quiz chain from: {initial_url}")
    print("📂 Expected behavior: Should resume from question 3 instead of starting fresh")
    
    # Note: We're not actually running the full chain here to avoid making real API calls
    # Just testing the checkpoint loading logic
    checkpoint = solver.load_checkpoint()
    if checkpoint:
        print(f"✅ Checkpoint detected!")
        print(f"   📍 Would resume from: {checkpoint['current_url']}")
        print(f"   🔢 At question: {checkpoint['attempt']}")
        print(f"   📊 Progress: {checkpoint['progress']}")
    else:
        print("❌ No checkpoint detected - would start fresh")
    
    # 4. Clear checkpoint
    print("\n4️⃣ Clearing test checkpoint...")
    solver.clear_checkpoint()
    
    print("\n🎉 RESUME TEST COMPLETED!")
    print("\n💡 USAGE:")
    print("   • If quiz stops at question 8, next run resumes from question 8")
    print("   • No need to start from question 1 again")
    print("   • Saves time and API calls")
    print("   • Automatic cleanup when quiz completes")

if __name__ == "__main__":
    test_resume_functionality()
