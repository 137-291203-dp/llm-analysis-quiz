#!/usr/bin/env python3
"""
Quiz Accuracy Testing Suite
Tests how accurately your LLM solves different types of quizzes
"""
import requests
import json
import time
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class QuizAccuracyTester:
    """Test quiz solving accuracy across different quiz types"""
    
    def __init__(self, api_base_url, email, secret):
        self.api_base_url = api_base_url.rstrip('/')
        self.email = email
        self.secret = secret
        self.results = []
        
    def test_single_quiz(self, quiz_url, expected_result=None, quiz_name="Unknown"):
        """Test a single quiz and measure performance"""
        print(f"\n🧪 Testing: {quiz_name}")
        print(f"📍 URL: {quiz_url}")
        
        start_time = time.time()
        
        try:
            # Send request to your API
            response = requests.post(
                f"{self.api_base_url}/api/v1/quiz/solve",
                json={
                    "email": self.email,
                    "secret": self.secret,
                    "url": quiz_url
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                test_result = {
                    "quiz_name": quiz_name,
                    "url": quiz_url,
                    "status": "success",
                    "response": result,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "expected": expected_result
                }
                
                print(f"✅ Success! Response: {result}")
                print(f"⏱️  Response time: {response_time:.2f}s")
                
            else:
                test_result = {
                    "quiz_name": quiz_name,
                    "url": quiz_url,
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "expected": expected_result
                }
                
                print(f"❌ Failed! HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            response_time = time.time() - start_time
            test_result = {
                "quiz_name": quiz_name,
                "url": quiz_url,
                "status": "exception",
                "error": str(e),
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "expected": expected_result
            }
            
            print(f"💥 Exception: {e}")
        
        self.results.append(test_result)
        return test_result
    
    def test_quiz_suite(self):
        """Test a comprehensive suite of different quiz types"""
        
        print("🎯 COMPREHENSIVE QUIZ ACCURACY TEST")
        print("=" * 60)
        
        # Test different types of quizzes
        quiz_suite = [
            {
                "name": "Demo Quiz (Basic)",
                "url": "https://tds-llm-analysis.s-anand.net/demo",
                "expected": "Should solve basic data analysis tasks",
                "difficulty": "Easy"
            },
            {
                "name": "Math/Statistics Quiz",
                "url": "https://tds-llm-analysis.s-anand.net/math-stats",
                "expected": "Statistical calculations and analysis",
                "difficulty": "Medium"
            },
            {
                "name": "Data Visualization Quiz",
                "url": "https://tds-llm-analysis.s-anand.net/dataviz",
                "expected": "Chart interpretation and creation",
                "difficulty": "Medium"
            },
            {
                "name": "Machine Learning Quiz",
                "url": "https://tds-llm-analysis.s-anand.net/ml-quiz",
                "expected": "ML concepts and implementation",
                "difficulty": "Hard"
            },
            {
                "name": "Advanced Analytics",
                "url": "https://tds-llm-analysis.s-anand.net/advanced",
                "expected": "Complex data analysis tasks",
                "difficulty": "Hard"
            }
        ]
        
        # Run tests
        for quiz in quiz_suite:
            self.test_single_quiz(
                quiz["url"], 
                quiz["expected"], 
                f"{quiz['name']} ({quiz['difficulty']})"
            )
            time.sleep(2)  # Wait between tests
        
        return self.analyze_results()
    
    def analyze_results(self):
        """Analyze test results and provide insights"""
        
        print(f"\n📊 TEST RESULTS ANALYSIS")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["status"] == "success"])
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r["response_time"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        print(f"📈 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        print(f"⏱️  Average Response Time: {avg_response_time:.2f}s")
        print(f"✅ Successful Tests: {successful_tests}")
        print(f"❌ Failed Tests: {failed_tests}")
        
        # Detailed breakdown
        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(self.results, 1):
            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"{status_emoji} {i}. {result['quiz_name']} - {result['status']} ({result['response_time']:.2f}s)")
            
            if result["status"] != "success":
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Performance insights
        print(f"\n💡 Performance Insights:")
        if success_rate >= 80:
            print("🎉 Excellent! Your LLM is solving most quizzes successfully")
        elif success_rate >= 60:
            print("👍 Good performance, but there's room for improvement")
        elif success_rate >= 40:
            print("⚠️  Moderate performance, consider reviewing your prompts or LLM settings")
        else:
            print("🔧 Low success rate, check your configuration and error patterns")
            
        if avg_response_time < 5:
            print("⚡ Fast response times - great for user experience")
        elif avg_response_time < 10:
            print("⏱️  Moderate response times - acceptable performance")
        else:
            print("🐌 Slow response times - consider optimizing your processing pipeline")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "detailed_results": self.results
        }
    
    def save_results(self, filename="quiz_accuracy_results.json"):
        """Save detailed results to file"""
        
        analysis = self.analyze_results()
        
        with open(filename, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": analysis["total_tests"],
                    "successful_tests": analysis["successful_tests"], 
                    "success_rate": analysis["success_rate"],
                    "avg_response_time": analysis["avg_response_time"],
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": analysis["detailed_results"]
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

def test_custom_quiz():
    """Test with a custom quiz URL"""
    
    api_url = input("Enter your API URL (or press Enter for default): ").strip()
    if not api_url:
        api_url = "https://llm-analysis-quiz-20q6.onrender.com"
    
    quiz_url = input("Enter quiz URL to test: ").strip()
    if not quiz_url:
        print("❌ Quiz URL is required")
        return
    
    print(f"\n🧪 Testing Custom Quiz")
    print(f"API: {api_url}")
    print(f"Quiz: {quiz_url}")
    
    tester = QuizAccuracyTester(
        api_base_url=api_url,
        email="24ds2000137@ds.study.iitm.ac.in",
        secret="my-secret-123"
    )
    
    result = tester.test_single_quiz(quiz_url, quiz_name="Custom Quiz")
    
    print(f"\n📊 Result: {result['status']}")
    if result['status'] == 'success':
        print(f"✅ Quiz solved successfully in {result['response_time']:.2f}s")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def main():
    """Main testing function"""
    
    print("🧪 QUIZ ACCURACY TESTING SUITE")
    print("=" * 50)
    print("Choose testing mode:")
    print("1. Full suite test (recommended)")
    print("2. Single custom quiz test")
    print("3. Local API test")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Full suite test with deployed API
        tester = QuizAccuracyTester(
            api_base_url="https://llm-analysis-quiz-20q6.onrender.com",
            email="24ds2000137@ds.study.iitm.ac.in", 
            secret="my-secret-123"
        )
        
        results = tester.test_quiz_suite()
        tester.save_results()
        
    elif choice == "2":
        test_custom_quiz()
        
    elif choice == "3":
        # Test local API
        print("🏠 Testing local API at http://localhost:5000")
        
        tester = QuizAccuracyTester(
            api_base_url="http://localhost:5000",
            email="24ds2000137@ds.study.iitm.ac.in",
            secret="my-secret-123"
        )
        
        # Test with demo quiz
        result = tester.test_single_quiz(
            "https://tds-llm-analysis.s-anand.net/demo",
            "Basic demo functionality",
            "Local Demo Test"
        )
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
