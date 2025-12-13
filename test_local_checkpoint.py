#!/usr/bin/env python3
"""
Test checkpoint functionality locally
"""

import time
import json
import os
from src.quiz_solver import QuizSolver

def test_local_checkpoint():
    """Test checkpoint functionality locally"""
    
    print("🧪 TESTING LOCAL CHECKPOINT SYSTEM")
    print("=" * 50)
    
    # Create a quiz solver
    solver = QuizSolver(
        email="24ds2000137@ds.study.iitm.ac.in",
        secret="my-secret-123",
        start_time=time.time()
    )
    
    print(f"📁 Checkpoint file: {solver.checkpoint_file}")
    
    # 1. Check if checkpoint exists
    print("\n1️⃣ Checking for existing checkpoint...")
    checkpoint = solver.load_checkpoint()
    if checkpoint:
        print(f"✅ Found checkpoint: {checkpoint}")
    else:
        print("📂 No checkpoint found")
    
    # 2. Create a test checkpoint
    print("\n2️⃣ Creating test checkpoint...")
    test_url = "https://tds-llm-analysis.s-anand.net/project2-reevals-5"
    test_progress = {
        'last_correct': True,
        'last_reason': '',
        'questions_completed': 5
    }
    
    solver.save_checkpoint(test_url, 5, test_progress)
    
    # 3. Load the checkpoint
    print("\n3️⃣ Loading checkpoint...")
    loaded_checkpoint = solver.load_checkpoint()
    if loaded_checkpoint:
        print(f"✅ Checkpoint loaded successfully:")
        print(f"   📍 Current URL: {loaded_checkpoint['current_url']}")
        print(f"   🔢 Attempt: {loaded_checkpoint['attempt']}")
        print(f"   📊 Progress: {loaded_checkpoint['progress']}")
        print(f"   ⏰ Timestamp: {time.ctime(loaded_checkpoint['timestamp'])}")
    else:
        print("❌ Failed to load checkpoint")
    
    # 4. Test checkpoint clearing
    print("\n4️⃣ Testing checkpoint clearing...")
    solver.clear_checkpoint()
    
    # 5. Verify checkpoint is cleared
    print("\n5️⃣ Verifying checkpoint is cleared...")
    final_checkpoint = solver.load_checkpoint()
    if final_checkpoint:
        print("❌ Checkpoint still exists after clearing")
    else:
        print("✅ Checkpoint successfully cleared")
    
    print("\n🎉 LOCAL CHECKPOINT TEST COMPLETED!")
    print("\n💡 HOW IT WORKS:")
    print("   1. When quiz runs, it saves progress after each question")
    print("   2. If quiz stops/fails, next run will resume from last question")
    print("   3. Checkpoint is automatically cleared when quiz completes")
    print("   4. Checkpoints expire after 24 hours")

if __name__ == "__main__":
    test_local_checkpoint()
