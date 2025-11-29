import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    STUDENT_EMAIL = os.getenv('STUDENT_EMAIL')
    STUDENT_SECRET = os.getenv('STUDENT_SECRET')
    
    # AI Pipe configuration (preferred)
    AIPIPE_TOKEN = os.getenv('AIPIPE_TOKEN')
    
    # OpenAI fallback (optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    PORT = int(os.getenv('PORT', 5000))
    
    # Quiz solving settings
    MAX_QUIZ_TIME = 180  # 3 minutes in seconds
    DOWNLOAD_DIR = 'downloads'
    TEMP_DIR = 'temp'
    
    # LLM settings (AI Pipe models)
    LLM_MODEL = 'openai/gpt-4o-mini'  # AI Pipe model format
    LLM_TEMPERATURE = 0.1
    LLM_MAX_TOKENS = 4096
    
    # AI Pipe API endpoints
    AIPIPE_BASE_URL = 'https://aipipe.org/openrouter/v1'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.STUDENT_EMAIL:
            raise ValueError("STUDENT_EMAIL not set in .env")
        if not cls.STUDENT_SECRET:
            raise ValueError("STUDENT_SECRET not set in .env")
        
        # Check for AI Pipe token or OpenAI API key
        if not cls.AIPIPE_TOKEN and not cls.OPENAI_API_KEY:
            raise ValueError("Either AIPIPE_TOKEN or OPENAI_API_KEY must be set in .env")
        
        return True
    
    @classmethod
    def use_aipipe(cls):
        """Check if AI Pipe should be used"""
        return bool(cls.AIPIPE_TOKEN)
