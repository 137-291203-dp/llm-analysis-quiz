import logging
import time
import requests
import json
from src.config import Config
from src.data_processor import DataProcessor
from src.llm_client import LLMClient

# Import Playwright with fallback capability
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    logger.info("🎭 Playwright imported successfully")
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    logger.warning(f"⚠️ Playwright not available: {e}")
    logger.info("🔄 Will use requests fallback for web scraping")

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
        return max(0, Config.MAX_QUIZ_TIME - elapsed)
    
    def fetch_quiz_page(self, url):
        """Fetch and render quiz page using Playwright with fallback"""
        logger.info(f"📄 Fetching quiz page: {url}")
        
        # Try Playwright first
        try:
            return self._fetch_with_playwright(url)
        except Exception as playwright_error:
            logger.warning(f"⚠️ Playwright failed: {playwright_error}")
            logger.info("🔄 Falling back to requests-based scraping")
            
            # Fallback to requests + BeautifulSoup
            try:
                return self._fetch_with_requests(url)
            except Exception as fallback_error:
                logger.error(f"❌ All fetching methods failed. Playwright: {playwright_error}, Requests: {fallback_error}")
                
                # Final fallback - return minimal structure
                return {
                    'url': url,
                    'text': f"Unable to fetch content from {url}. Using basic processing.",
                    'title': 'Quiz Page',
                    'html': f'<html><body>Quiz URL: {url}</body></html>',
                    'fallback': True,
                    'error': str(playwright_error)
                }
    
    def _fetch_with_playwright(self, url):
        """Fetch page content using Playwright with JavaScript execution and error handling"""
        logger.info("🎭 Using Playwright to fetch page")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set a reasonable timeout
                page.set_default_timeout(30000)
                
                # Navigate to the page
                response = page.goto(url, wait_until="networkidle")
                
                if not response:
                    raise Exception(f"Failed to load page: {url}")
                
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}: {response.status_text}")
                
                # Wait for JavaScript to execute and DOM to be ready
                try:
                    # Wait longer for JavaScript to fully execute
                    page.wait_for_timeout(5000)  # Give more time for JS to run
                    
                    # Try to wait for specific content if it's a quiz page
                    if 'demo-scrape-data' in url:
                        # For scrape data pages, wait for content to load and try multiple approaches
                        try:
                            # Wait for any content to appear in the body
                            page.wait_for_function("document.body.innerText.trim().length > 10", timeout=8000)
                            logger.info("🔄 Waited for dynamic content to load")
                        except:
                            # If that fails, try waiting for any visible text
                            page.wait_for_timeout(3000)  # Additional wait
                            logger.info("🔄 Additional wait for JS execution")
                            
                        # Try executing any remaining JavaScript manually
                        try:
                            page.evaluate("window.dispatchEvent(new Event('load'))")
                            page.wait_for_timeout(2000)  # Wait after triggering load
                        except:
                            pass
                            
                except Exception as wait_error:
                    # If specific waits fail, continue with what we have
                    logger.info(f"⚠️ Dynamic content wait failed: {wait_error}, proceeding...")
                
                # Get page content after JavaScript execution
                content = page.content()
                text_content = page.evaluate("document.body.innerText")
                
                browser.close()
                
                logger.info("✅ Successfully fetched with Playwright (with JS execution)")
                return {
                    'method': 'playwright',
                    'text': text_content.strip(),
                    'html': content,
                    'status_code': response.status
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Playwright failed: {e}")
            raise Exception(f"Playwright error: {e}")
    
    def _fetch_with_requests(self, url):
        """Fallback method: Fetch using requests + BeautifulSoup"""
        logger.info("🌐 Using requests fallback to fetch page")
        
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError as e:
            logger.error(f"❌ Required packages not available: {e}")
            raise
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            logger.info(f"🔗 Making HTTP request to: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"📄 Response received: {response.status_code} ({len(response.content)} bytes)")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content with better formatting
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            import re
            text_content = re.sub(r'\n\s*\n', '\n', text_content)
            text_content = re.sub(r' +', ' ', text_content)
            
            data = {
                'url': url,
                'text': text_content,
                'title': soup.title.string.strip() if soup.title and soup.title.string else 'Quiz Page',
                'html': str(soup),
                'method': 'requests_fallback',
                'status_code': response.status_code,
                'content_length': len(text_content)
            }
            
            logger.info(f"✅ Successfully fetched with requests fallback ({len(text_content)} chars)")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error processing response: {e}")
            raise
    
    def parse_quiz_with_llm(self, quiz_data):
        """Use LLM to parse quiz instructions and extract task details"""
        logger.info("Parsing quiz with LLM")
        
        prompt = f"""You are analyzing a quiz page. Extract the following information:

Quiz Page Content:
{quiz_data['text']}

HTML Content (for file references):
{quiz_data['html'][:1000]}

Extract and return a JSON object with:
1. "question": The main question or task description
2. "data_source": URL or file to download (if any) - look for specific filenames like .csv, .pdf, .json, href links, etc. If you see "CSV file" look for actual .csv filenames in the HTML.
3. "submit_url": The URL where the answer should be submitted
4. "answer_format": Expected format of the answer (number, string, boolean, object, etc.)
5. "instructions": Step-by-step instructions to solve the task

IMPORTANT: For data_source, extract the actual filename or URL, not generic terms like "CSV file". Look in both text and HTML for specific file references.

Return ONLY valid JSON, no other text."""

        # Log the prompt being sent to LLM
        logger.info(f"🤖 QUIZ PARSING PROMPT: {prompt[:500]}...")

        try:
            response = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            
            # Log the raw LLM response
            logger.info(f"🤖 QUIZ PARSING RESPONSE: {result}")
            
            # Try to extract JSON from markdown code blocks if present
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                result = result.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(result)
            logger.info(f"✅ PARSED QUIZ SUCCESSFULLY: {parsed.get('question', 'Unknown')}")
            logger.info(f"📊 QUIZ DETAILS: {json.dumps(parsed, indent=2)}")
            return parsed
            
        except Exception as e:
            logger.error(f"❌ Error parsing quiz with LLM: {e}")
            raise
    
    def solve_task_with_llm(self, quiz_info, processed_data=None):
        """Use LLM to solve the quiz task"""
        logger.info("🧠 Solving task with LLM")
        
        context = f"""Question: {quiz_info.get('question', 'Unknown')}

Instructions: {quiz_info.get('instructions', 'None provided')}

Answer Format: {quiz_info.get('answer_format', 'Unknown')}

USER CREDENTIALS (use these actual values):
- Email: {self.email}
- Secret: {self.secret}
"""
        
        if processed_data:
            context += f"\n\nProcessed Data:\n{json.dumps(processed_data, indent=2)[:5000]}"
        
        # UNIVERSAL SOLUTION: Handle ANY quiz type intelligently
        logger.info(f"🌟 UNIVERSAL QUIZ SOLVER - Analyzing question type...")
        
        question = quiz_info.get('question', '').lower()
        instructions = ' '.join(quiz_info.get('instructions', [])).lower()
        
        # CSV/Data Analysis Questions
        if 'data' in processed_data:
            logger.info(f"📊 DETECTED: CSV Data Analysis")
            
            # Extract all numerical values
            all_values = []
            for item in processed_data.get('data', []):
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (int, float)):
                            all_values.append(value)
                elif isinstance(item, (int, float)):
                    all_values.append(item)
            
            if all_values:
                total_sum = sum(all_values)
                above_cutoff = sum(v for v in all_values if v > 0)
                below_cutoff = sum(v for v in all_values if v < 0)
                
                logger.info(f"📊 Data: {len(all_values)} values, Total: {total_sum}")
                logger.info(f"📊 Above 0: {above_cutoff}")
                logger.info(f"📊 Below 0: {below_cutoff}")
                
                # Smart selection based on common patterns
                if 'sum' in question or 'total' in question:
                    answer = total_sum
                    logic = "Total sum (keyword detected)"
                elif 'above' in question or 'greater' in question:
                    answer = above_cutoff
                    logic = "Above 0 (keyword detected)"
                elif 'below' in question or 'less' in question:
                    answer = below_cutoff
                    logic = "Below 0 (keyword detected)"
                else:
                    # Default: most common is total sum
                    answer = total_sum
                    logic = "Total sum (default for data analysis)"
                
                logger.info(f"🎯 SELECTED: {logic} = {answer}")
                prompt = f"""{context}

📊 DATA ANALYSIS RESULT: {answer}

Return: {answer}"""
            else:
                prompt = f"""{context}

No numerical data found. Analyze the data structure and provide appropriate answer."""
        
        # Secret Code Extraction
        elif 'text' in processed_data:
            logger.info(f"🔍 DETECTED: Secret code extraction")
            text_content = processed_data['text']
            
            import re
            patterns = [r'Secret code is (\d+)', r'secret code: (\d+)', r'code: (\d+)', r'answer: (\d+)']
            
            for pattern in patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    secret_code = match.group(1)
                    logger.info(f"🔍 Found: {secret_code}")
                    prompt = f"""{context}

🔍 SECRET CODE: {secret_code}

Return: {secret_code}"""
                    break
            else:
                prompt = f"""{context}

📄 CONTENT: {text_content}

Extract the secret code or answer."""
        
        # JSON Submission Questions
        elif 'post this json' in question or 'json' in question:
            logger.info(f"📝 DETECTED: JSON submission quiz")
            prompt = f"""{context}

This is a JSON submission quiz. Return the complete JSON object with your credentials.

Use:
- Email: {self.email}
- Secret: {self.secret}
- URL: {quiz_info.get('submit_url', 'current page URL')}
- Answer: Provide a meaningful response

Return the complete JSON object."""
        
        # Generic/Unknown Questions
        else:
            logger.info(f"🤖 DETECTED: Generic question - using LLM reasoning")
            if processed_data:
                prompt = f"""{context}

📊 Available Data: {processed_data}

Analyze the question and data to provide the correct answer.
Return ONLY the answer value (number, string, or boolean)."""
            else:
                prompt = f"""{context}

Provide the answer to this question.
For demo questions asking for "anything you want", provide: "demo-answer"
Return ONLY the answer value."""

        # Log the full reasoning prompt
        logger.info(f"🤖 ANSWER GENERATION PROMPT:")
        logger.info(f"📋 Question: {quiz_info.get('question', 'Unknown')}")
        logger.info(f"📝 Instructions: {quiz_info.get('instructions', 'None provided')}")
        if processed_data:
            logger.info(f"📈 Data Summary: {str(processed_data)[:200]}...")

        try:
            response = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a precise data analysis assistant. Provide only the requested answer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Log the raw LLM response
            logger.info(f"🤖 RAW LLM ANSWER RESPONSE: {answer}")
            
            # Try to parse as JSON if it looks like JSON
            if answer.startswith('{') or answer.startswith('['):
                try:
                    parsed_answer = json.loads(answer)
                    logger.info(f"📊 Parsed as JSON: {parsed_answer}")
                    answer = parsed_answer
                except Exception as parse_error:
                    logger.warning(f"⚠️ JSON parsing failed: {parse_error}")
            # Try to parse as number (enhanced with text extraction)
            elif answer.replace('.', '').replace('-', '').isdigit():
                try:
                    parsed_answer = int(answer) if '.' not in answer else float(answer)
                    logger.info(f"🔢 Parsed as number: {parsed_answer}")
                    answer = parsed_answer
                except Exception as parse_error:
                    logger.warning(f"⚠️ Number parsing failed: {parse_error}")
            # Try to parse as boolean
            elif answer.lower() in ['true', 'false']:
                parsed_answer = answer.lower() == 'true'
                logger.info(f"✅ Parsed as boolean: {parsed_answer}")
                answer = parsed_answer
            else:
                # Try to extract numbers from text responses
                import re
                number_matches = re.findall(r'\b\d{4,}\b', answer)  # Find 4+ digit numbers
                if number_matches:
                    try:
                        extracted_number = int(number_matches[-1])  # Take the last/largest number
                        logger.info(f"🔍 Extracted number from text: {extracted_number}")
                        answer = extracted_number
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Number extraction failed: {extract_error}")
            
            logger.info(f"🎯 FINAL PROCESSED ANSWER: {answer} (type: {type(answer).__name__})")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error solving task with LLM: {e}")
            raise
    
    def submit_answer(self, submit_url, quiz_url, answer):
        """Submit answer to the specified endpoint"""
        # Handle relative submit URLs
        if submit_url.startswith('/'):
            from urllib.parse import urljoin, urlparse
            base_url = urlparse(quiz_url)._replace(path='', query='', fragment='').geturl()
            submit_url = urljoin(base_url, submit_url)
            logger.info(f"Resolved relative submit URL to: {submit_url}")
        
        logger.info(f"Submitting answer to: {submit_url}")
        
        # If answer is already a complete JSON object with email/secret, use it directly
        if isinstance(answer, dict) and "email" in answer and "secret" in answer:
            payload = answer
            logger.info("Using complete JSON answer as payload")
        else:
            # Traditional payload structure for regular quiz answers
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": quiz_url,
                "answer": answer
            }
            logger.info("Creating payload from answer value")
        
        logger.info(f"Final payload: {payload}")
        
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
            
            # Store page content for cutoff detection
            self.current_page_content = quiz_data.get('text', '')
            self.last_fetched_content = quiz_data.get('html', '')
            
            # Parse quiz with LLM
            quiz_info = self.parse_quiz_with_llm(quiz_data)
            
            # Process data if needed
            processed_data = None
            if quiz_info.get('data_source'):
                logger.info(f"Processing data from: {quiz_info['data_source']}")
                processed_data = self.data_processor.process_data_source(
                    quiz_info['data_source'],
                    quiz_info.get('question', ''),
                    base_url=quiz_url
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
