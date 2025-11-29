"""
Display submission information for Google Form
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config import Config
from src.prompts import get_system_prompt, get_user_prompt

def main():
    """Display submission information"""
    print("="*60)
    print("GOOGLE FORM SUBMISSION INFORMATION")
    print("="*60)
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set up your .env file correctly:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your credentials:")
        print("   - For FREE option: Get AI Pipe token from https://aipipe.org")
        print("   - For PAID option: Get OpenAI API key from https://platform.openai.com")
        print("3. Run this script again")
        sys.exit(1)
    
    print("\n1. EMAIL ADDRESS")
    print("-" * 60)
    print(f"   {Config.STUDENT_EMAIL}")
    
    print("\n2. SECRET STRING")
    print("-" * 60)
    print(f"   {Config.STUDENT_SECRET}")
    print(f"   ⚠️  Keep this confidential!")
    
    # Show LLM provider information
    print(f"\n💡 LLM PROVIDER")
    print("-" * 60)
    if Config.use_aipipe():
        print(f"   ✅ Using AI Pipe (FREE)")
        print(f"   Token: {Config.AIPIPE_TOKEN[:20]}...")
        print(f"   Model: {Config.LLM_MODEL}")
        print(f"   💰 Cost: FREE ($0.10/week credit)")
    elif Config.OPENAI_API_KEY:
        print(f"   💳 Using OpenAI (PAID)")
        print(f"   Key: {Config.OPENAI_API_KEY[:20]}...")
        print(f"   Model: {Config.LLM_MODEL}")
        print(f"   💰 Cost: ~$0.01-0.03 per request")
    else:
        print(f"   ❌ No LLM provider configured")
        print(f"   Set AIPIPE_TOKEN (free) or OPENAI_API_KEY (paid) in .env")
    
    print("\n3. SYSTEM PROMPT (Max 100 chars)")
    print("-" * 60)
    system_prompt = get_system_prompt()
    char_count = len(system_prompt)
    status = "✓" if char_count <= 100 else "✗"
    print(f"   {system_prompt}")
    print(f"   {status} Character count: {char_count}/100")
    
    print("\n4. USER PROMPT (Max 100 chars)")
    print("-" * 60)
    user_prompt = get_user_prompt()
    char_count = len(user_prompt)
    status = "✓" if char_count <= 100 else "✗"
    print(f"   {user_prompt}")
    print(f"   {status} Character count: {char_count}/100")
    
    print("\n5. API ENDPOINT URL")
    print("-" * 60)
    print(f"   [YOUR DEPLOYED HTTPS URL]")
    print(f"   Example: https://llm-analysis-quiz.onrender.com")
    print(f"   ⚠️  Must be HTTPS, not HTTP")
    print(f"   ⚠️  Must be publicly accessible")
    
    print("\n6. GITHUB REPOSITORY URL")
    print("-" * 60)
    print(f"   [YOUR PUBLIC GITHUB REPO URL]")
    print(f"   Example: https://github.com/username/llm-analysis-quiz")
    print(f"   ⚠️  Must be public")
    print(f"   ⚠️  Must include MIT LICENSE")
    
    print("\n" + "="*60)
    print("PRE-SUBMISSION CHECKLIST")
    print("="*60)
    
    checklist = [
        "Email is correct",
        "Secret matches .env file",
        "System prompt is ≤ 100 characters",
        "User prompt is ≤ 100 characters",
        "API endpoint is HTTPS",
        "API endpoint is accessible (test with curl)",
        "GitHub repo is public",
        "LICENSE file exists",
        "All code is pushed to GitHub",
        "Tested with demo endpoint"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"   [ ] {i}. {item}")
    
    print("\n" + "="*60)
    print("TESTING COMMANDS")
    print("="*60)
    
    print("\nTest your local endpoint:")
    print(f"   python test_endpoint.py")
    
    print("\nTest your deployed endpoint:")
    print(f"   curl https://your-endpoint.com/")
    
    print("\nTest with demo quiz:")
    print(f"""   curl -X POST https://your-endpoint.com/quiz \\
     -H "Content-Type: application/json" \\
     -d '{{"email": "{Config.STUDENT_EMAIL}", "secret": "{Config.STUDENT_SECRET}", "url": "https://tds-llm-analysis.s-anand.net/demo"}}'""")
    
    print("\n" + "="*60)
    print("EVALUATION SCHEDULE")
    print("="*60)
    print("   Date: Saturday, November 29, 2025")
    print("   Time: 3:00 PM - 4:00 PM IST")
    print("   ⚠️  Make sure your endpoint is running!")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("   1. Deploy your application (see DEPLOYMENT.md)")
    print("   2. Test your deployed endpoint")
    print("   3. Make your GitHub repo public")
    print("   4. Fill out the Google Form")
    print("   5. Keep your endpoint running until evaluation")
    
    print("\n✨ Good luck with your submission!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
