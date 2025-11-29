#!/usr/bin/env python3
"""
Test the quiz solving system with actual questions
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

def test_math_question():
    """Test with simple math question"""
    print("🧮 TESTING MATH QUESTION")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        solver = QuizSolver(
            email="test@test.com",
            secret="test-secret",
            start_time=time.time()
        )
        
        # Create a simple math quiz
        quiz_info = {
            'question': 'What is 1 + 1?',
            'instructions': ['Solve the math problem', 'Return only the numerical answer'],
            'answer_format': 'number',
            'data_source': None,
            'submit_url': 'https://example.com/submit'
        }
        
        print(f"📋 Question: {quiz_info['question']}")
        
        # Test the LLM solver
        answer = solver.solve_task_with_llm(quiz_info)
        
        print(f"🎯 LLM Answer: {answer} (type: {type(answer).__name__})")
        
        # Check if correct
        if answer == 2 or answer == "2":
            print("✅ CORRECT! LLM solved 1+1 = 2")
            return True
        else:
            print(f"❌ INCORRECT! Expected 2, got {answer}")
            return False
            
    except Exception as e:
        print(f"❌ Math test failed: {e}")
        return False

def test_text_question():
    """Test with text-based question"""
    print("\n📝 TESTING TEXT QUESTION")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        solver = QuizSolver(
            email="test@test.com",
            secret="test-secret",
            start_time=time.time()
        )
        
        # Create a simple text quiz
        quiz_info = {
            'question': 'What is the capital of France?',
            'instructions': ['Answer with the city name only'],
            'answer_format': 'string',
            'data_source': None,
            'submit_url': 'https://example.com/submit'
        }
        
        print(f"📋 Question: {quiz_info['question']}")
        
        # Test the LLM solver
        answer = solver.solve_task_with_llm(quiz_info)
        
        print(f"🎯 LLM Answer: {answer} (type: {type(answer).__name__})")
        
        # Check if reasonable
        if isinstance(answer, str) and 'paris' in answer.lower():
            print("✅ CORRECT! LLM knows Paris is the capital of France")
            return True
        else:
            print(f"⚠️ UNEXPECTED! Got: {answer}")
            return False
            
    except Exception as e:
        print(f"❌ Text test failed: {e}")
        return False

def test_data_analysis_question():
    """Test with data analysis question"""
    print("\n📊 TESTING DATA ANALYSIS QUESTION")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        solver = QuizSolver(
            email="test@test.com",
            secret="test-secret",
            start_time=time.time()
        )
        
        # Create sample data
        sample_data = {
            'type': 'csv',
            'data': [
                {'name': 'Alice', 'age': 25, 'salary': 50000},
                {'name': 'Bob', 'age': 30, 'salary': 60000},
                {'name': 'Charlie', 'age': 35, 'salary': 70000}
            ],
            'summary': {'count': 3, 'avg_age': 30, 'avg_salary': 60000}
        }
        
        quiz_info = {
            'question': 'What is the average age of people in the dataset?',
            'instructions': ['Calculate the average age', 'Return only the number'],
            'answer_format': 'number',
            'data_source': 'sample_data.csv',
            'submit_url': 'https://example.com/submit'
        }
        
        print(f"📋 Question: {quiz_info['question']}")
        print(f"📊 Sample data: 3 people with ages 25, 30, 35")
        
        # Test the LLM solver with data
        answer = solver.solve_task_with_llm(quiz_info, sample_data)
        
        print(f"🎯 LLM Answer: {answer} (type: {type(answer).__name__})")
        
        # Check if correct (average of 25, 30, 35 = 30)
        if answer == 30 or answer == "30":
            print("✅ CORRECT! LLM calculated average age = 30")
            return True
        else:
            print(f"❌ INCORRECT! Expected 30, got {answer}")
            return False
            
    except Exception as e:
        print(f"❌ Data analysis test failed: {e}")
        return False

def test_boolean_question():
    """Test with boolean question"""
    print("\n❓ TESTING BOOLEAN QUESTION")
    print("=" * 50)
    
    try:
        from src.quiz_solver import QuizSolver
        
        solver = QuizSolver(
            email="test@test.com",
            secret="test-secret",
            start_time=time.time()
        )
        
        quiz_info = {
            'question': 'Is Python a programming language?',
            'instructions': ['Answer true or false'],
            'answer_format': 'boolean',
            'data_source': None,
            'submit_url': 'https://example.com/submit'
        }
        
        print(f"📋 Question: {quiz_info['question']}")
        
        # Test the LLM solver
        answer = solver.solve_task_with_llm(quiz_info)
        
        print(f"🎯 LLM Answer: {answer} (type: {type(answer).__name__})")
        
        # Check if correct
        if answer is True or str(answer).lower() == 'true':
            print("✅ CORRECT! LLM knows Python is a programming language")
            return True
        else:
            print(f"❌ INCORRECT! Expected True, got {answer}")
            return False
            
    except Exception as e:
        print(f"❌ Boolean test failed: {e}")
        return False

def main():
    """Run all question type tests"""
    
    print("🎯 TESTING ACTUAL QUIZ QUESTIONS")
    print("=" * 70)
    print("Testing your LLM's ability to solve real problems")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("Math (1+1)", test_math_question),
        ("Geography", test_text_question), 
        ("Data Analysis", test_data_analysis_question),
        ("Boolean Logic", test_boolean_question)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        results[test_name] = test_func()
    
    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print(f"\n🎉 EXCELLENT! Your LLM can solve:")
        print(f"✅ Math problems (1+1)")
        print(f"✅ Knowledge questions (geography)")
        print(f"✅ Data analysis (averages)")
        print(f"✅ Boolean logic (true/false)")
        print(f"\n🚀 Your system is ready for complex quizzes!")
        
    elif passed >= len(tests) // 2:
        print(f"\n⚠️ PARTIAL SUCCESS - Most question types work!")
        print(f"💡 Your system can handle most quiz scenarios")
        
    else:
        print(f"\n🔧 NEEDS IMPROVEMENT")
        print(f"💡 Check LLM prompting and answer parsing logic")

if __name__ == "__main__":
    main()
