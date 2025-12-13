#!/usr/bin/env python3
"""
Run the LLM Analysis Quiz system on project2 URL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.quiz_solver import QuizSolver
from src.data_processor import DataProcessor
from src.llm_client import LLMClient
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the quiz solver on project2"""
    
    # Initialize components
    llm_client = LLMClient()
    data_processor = DataProcessor()
    
    # Your credentials
    email = "24ds2000137@ds.study.iitm.ac.in"
    secret = "my-secret-123"
    
    # Initialize quiz solver
    quiz_solver = QuizSolver(
        llm_client=llm_client,
        data_processor=data_processor,
        email=email,
        secret=secret
    )
    
    # Run on project2 URL
    project2_url = "https://tds-llm-analysis.s-anand.net/project2"
    
    print(f"🚀 Starting LLM Analysis Quiz on: {project2_url}")
    print(f"📧 Email: {email}")
    print("=" * 60)
    
    try:
        result = quiz_solver.solve_quiz_chain(project2_url)
        
        if result:
            print("\n🎉 SUCCESS! Quiz chain completed!")
            print(f"Final result: {result}")
        else:
            print("\n❌ Quiz chain failed or incomplete")
            
    except Exception as e:
        print(f"\n💥 Error running quiz: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
