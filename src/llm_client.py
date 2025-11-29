"""
LLM Client supporting AI Pipe and OpenAI
"""
import logging
import requests
import json
from openai import OpenAI
from src.config import Config

logger = logging.getLogger(__name__)

class LLMClient:
    """Unified LLM client supporting AI Pipe and OpenAI"""
    
    def __init__(self):
        self.use_aipipe = config.Config.use_aipipe()
        
        if self.use_aipipe:
            logger.info("Using AI Pipe for LLM requests")
            self.token = config.Config.AIPIPE_TOKEN
            self.base_url = config.Config.AIPIPE_BASE_URL
        else:
            logger.info("Using OpenAI for LLM requests")
            self.client = OpenAI(api_key=config.Config.OPENAI_API_KEY)
    
    def chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        """Create a chat completion using AI Pipe or OpenAI"""
        
        # Use config defaults if not specified
        model = model or config.Config.LLM_MODEL
        temperature = temperature or config.Config.LLM_TEMPERATURE
        max_tokens = max_tokens or config.Config.LLM_MAX_TOKENS
        
        if self.use_aipipe:
            return self._aipipe_chat_completion(messages, model, temperature, max_tokens)
        else:
            return self._openai_chat_completion(messages, model, temperature, max_tokens)
    
    def _aipipe_chat_completion(self, messages, model, temperature, max_tokens):
        """Make chat completion request to AI Pipe"""
        logger.info(f"AI Pipe request - Model: {model}")
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content from AI Pipe response
            content = result['choices'][0]['message']['content']
            
            # Return in OpenAI-compatible format
            return MockResponse(content)
            
        except Exception as e:
            logger.error(f"AI Pipe request failed: {e}")
            raise
    
    def _openai_chat_completion(self, messages, model, temperature, max_tokens):
        """Make chat completion request to OpenAI"""
        logger.info(f"OpenAI request - Model: {model}")
        
        try:
            # Convert AI Pipe model format to OpenAI format if needed
            if '/' in model:
                model = model.split('/')[-1]  # Extract model name after slash
            
            # Map AI Pipe models to OpenAI models
            model_mapping = {
                'gpt-4o-mini': 'gpt-4o-mini',
                'gpt-4.1-nano': 'gpt-4o-mini',
                'gpt-4-turbo-preview': 'gpt-4-turbo-preview',
                'gpt-4': 'gpt-4'
            }
            
            model = model_mapping.get(model, 'gpt-4o-mini')
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            raise

class MockResponse:
    """Mock response to match OpenAI response format"""
    
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice to match OpenAI choice format"""
    
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message to match OpenAI message format"""
    
    def __init__(self, content):
        self.content = content
