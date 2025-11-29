import logging
import time
import requests
import json
from playwright.sync_api import sync_playwright
from src.config import Config
from src.data_processor import DataProcessor
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)

class QuizSolver:
    """Solves quiz tasks using headless browser and LLM"""
    
    def __init__(self, email, secret, start_time):
        self.email = email
        self.secret = secret
        self.start_time = start_time
        self.llm_client = LLMClient()
        self.data_processor = DataProcessor()
        
    def get_remaining_time(self):
        """Get remaining time in seconds"""
        elapsed = time.time() - self.start_time
        return max(0, config.Config.MAX_QUIZ_TIME - elapsed)
    
    def fetch_quiz_page(self, url):
        """Fetch and render quiz page using Playwright"""
        logger.info(f"Fetching quiz page: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Navigate to the page
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to render
                page.wait_for_timeout(2000)
                
                # Get the rendered HTML
                content = page.content()
                
                # Get text content from body
                text_content = page.evaluate('() => document.body.innerText')
                
                browser.close()
                
                logger.info(f"Successfully fetched quiz page")
                return {
                    'html': content,
                    'text': text_content,
                    'url': url
                }
        except Exception as e:
            logger.error(f"Error fetching quiz page: {e}")
            raise
    
    def parse_quiz_with_llm(self, quiz_data):
        """Use LLM to parse quiz instructions and extract task details"""
        logger.info("Parsing quiz with LLM")
        
        prompt = f"""You are analyzing a quiz page. Extract the following information:

Quiz Page Content:
{quiz_data['text']}

Extract and return a JSON object with:
1. "question": The main question or task description
2. "data_source": URL or file to download (if any)
3. "submit_url": The URL where the answer should be submitted
4. "answer_format": Expected format of the answer (number, string, boolean, object, etc.)
5. "instructions": Step-by-step instructions to solve the task

Return ONLY valid JSON, no other text."""

        try:
            response = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to extract JSON from markdown code blocks if present
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                result = result.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(result)
            logger.info(f"Parsed quiz: {parsed.get('question', 'Unknown')}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing quiz with LLM: {e}")
            raise
    
    def solve_task_with_llm(self, quiz_info, processed_data=None):
        """Use LLM to solve the quiz task"""
        logger.info("Solving task with LLM")
        
        context = f"""Question: {quiz_info.get('question', 'Unknown')}

Instructions: {quiz_info.get('instructions', 'None provided')}

Answer Format: {quiz_info.get('answer_format', 'Unknown')}
"""
        
        if processed_data:
            context += f"\n\nProcessed Data:\n{json.dumps(processed_data, indent=2)[:5000]}"
        
        prompt = f"""{context}

Based on the above information, provide the answer to the question.
Return ONLY the answer value in the appropriate format (number, string, boolean, or JSON object).
Do not include explanations or additional text."""

        try:
            response = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise data analysis assistant. Provide only the requested answer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Try to parse as JSON if it looks like JSON
            if answer.startswith('{') or answer.startswith('['):
                try:
                    answer = json.loads(answer)
                except:
                    pass
            # Try to parse as number
            elif answer.replace('.', '').replace('-', '').isdigit():
                try:
                    answer = int(answer) if '.' not in answer else float(answer)
                except:
                    pass
            # Try to parse as boolean
            elif answer.lower() in ['true', 'false']:
                answer = answer.lower() == 'true'
            
            logger.info(f"Generated answer: {answer}")
            return answer
            
        except Exception as e:
            logger.error(f"Error solving task with LLM: {e}")
            raise
    
    def submit_answer(self, submit_url, quiz_url, answer):
        """Submit answer to the specified endpoint"""
        logger.info(f"Submitting answer to: {submit_url}")
        
        payload = {
            "email": self.email,
            "secret": self.secret,
            "url": quiz_url,
            "answer": answer
        }
        
        try:
            response = requests.post(
                submit_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            logger.info(f"Submit response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Submit result: {result}")
                return result
            else:
                logger.error(f"Submit failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return None
    
    def solve_single_quiz(self, quiz_url):
        """Solve a single quiz task"""
        logger.info(f"Solving quiz: {quiz_url}")
        
        try:
            # Check remaining time
            if self.get_remaining_time() < 10:
                logger.warning("Not enough time remaining")
                return None
            
            # Fetch quiz page
            quiz_data = self.fetch_quiz_page(quiz_url)
            
            # Parse quiz with LLM
            quiz_info = self.parse_quiz_with_llm(quiz_data)
            
            # Process data if needed
            processed_data = None
            if quiz_info.get('data_source'):
                logger.info(f"Processing data from: {quiz_info['data_source']}")
                processed_data = self.data_processor.process_data_source(
                    quiz_info['data_source'],
                    quiz_info.get('question', '')
                )
            
            # Solve task with LLM
            answer = self.solve_task_with_llm(quiz_info, processed_data)
            
            # Submit answer
            submit_url = quiz_info.get('submit_url')
            if submit_url:
                result = self.submit_answer(submit_url, quiz_url, answer)
                return result
            else:
                logger.error("No submit URL found")
                return None
                
        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
            return None
    
    def solve_quiz_chain(self, initial_url):
        """Solve a chain of quiz tasks"""
        logger.info(f"Starting quiz chain from: {initial_url}")
        
        current_url = initial_url
        attempt = 0
        max_attempts = 20  # Prevent infinite loops
        
        while current_url and attempt < max_attempts:
            attempt += 1
            
            # Check time limit
            remaining = self.get_remaining_time()
            logger.info(f"Attempt {attempt}, Remaining time: {remaining:.1f}s")
            
            if remaining < 5:
                logger.warning("Time limit reached")
                break
            
            # Solve current quiz
            result = self.solve_single_quiz(current_url)
            
            if not result:
                logger.warning(f"Failed to solve quiz at {current_url}")
                break
            
            # Check if correct
            if result.get('correct'):
                logger.info(f"✓ Correct answer for {current_url}")
            else:
                logger.warning(f"✗ Incorrect answer: {result.get('reason', 'Unknown')}")
            
            # Get next URL
            next_url = result.get('url')
            if next_url:
                logger.info(f"Moving to next quiz: {next_url}")
                current_url = next_url
            else:
                logger.info("Quiz chain completed - no more URLs")
                break
        
        logger.info(f"Quiz chain finished after {attempt} attempts")
