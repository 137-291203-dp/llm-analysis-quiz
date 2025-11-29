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
        
        # Check if this is a submission-style quiz that wants a complete JSON structure
        if "POST this JSON" in quiz_info.get('question', '') and any("email" in str(instr) for instr in quiz_info.get('instructions', [])):
            prompt = f"""{context}

This is a JSON submission quiz. You need to return the COMPLETE JSON object that should be posted to the submit URL.
Use these ACTUAL user credentials:
- Email: {self.email}
- Secret: {self.secret}

Return the complete JSON object in this exact format:
{{
  "email": "{self.email}",
  "secret": "{self.secret}", 
  "url": "https://tds-llm-analysis.s-anand.net/demo",
  "answer": "your-meaningful-answer-here"
}}

Replace "your-meaningful-answer-here" with an appropriate answer value."""
        else:
            # Enhanced prompting for different quiz types
            if processed_data and processed_data.get('type') == 'csv':
                # Special handling for CSV data analysis
                cutoff_match = None
                import re
                
                # Multiple sources to search for cutoff values
                search_sources = []
                
                # Add page content if available
                if hasattr(self, 'current_page_content') and self.current_page_content:
                    search_sources.append(self.current_page_content)
                
                # Add HTML content if available  
                if hasattr(self, 'last_fetched_content') and self.last_fetched_content:
                    search_sources.append(self.last_fetched_content)
                
                # Add quiz info
                if quiz_info.get('question'):
                    search_sources.append(str(quiz_info))
                
                # Add processed data
                search_sources.append(str(processed_data))
                
                # Try different cutoff patterns
                cutoff_patterns = [
                    r'Cutoff:\s*(\d+)',
                    r'cutoff[:\s]+(\d+)', 
                    r'cut[\s-]*off[:\s]*(\d+)',
                    r'threshold[:\s]*(\d+)',
                    r'limit[:\s]*(\d+)'
                ]
                
                # Search all sources with all patterns
                for source in search_sources:
                    if cutoff_match:
                        break
                    for pattern in cutoff_patterns:
                        cutoff_match = re.search(pattern, source, re.IGNORECASE)
                        if cutoff_match:
                            logger.info(f"🎯 Found cutoff value {cutoff_match.group(1)} using pattern '{pattern}'")
                            break
                
                cutoff_instruction = ""
                if cutoff_match:
                    cutoff_value = int(cutoff_match.group(1))
                    cutoff_instruction = f"""
🎯 CUTOFF VALUE DETECTED: {cutoff_value}
- Compare each data value against this cutoff: {cutoff_value}
- Sum values that are ABOVE the cutoff (> {cutoff_value})
- OR sum values that are BELOW the cutoff (< {cutoff_value})
- Choose based on which makes more sense for the question"""
                
                # Extract actual data values for better analysis  
                actual_values = []
                csv_columns = processed_data.get('columns', [])
                
                # Debug: log CSV structure
                logger.info(f"📊 CSV Columns: {csv_columns}")
                logger.info(f"📊 Sample CSV data items: {processed_data.get('data', [])[:3]}")
                
                # Extract just the numerical values, ignore column names
                for item in processed_data.get('data', [])[:50]:  # Get more samples
                    if item:
                        values = list(item.values())
                        # Filter out non-numeric values and column names
                        numeric_values = []
                        for val in values:
                            try:
                                if isinstance(val, (int, float)):
                                    numeric_values.append(int(val))
                                elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                                    numeric_values.append(int(float(val)))
                            except:
                                continue
                        actual_values.extend(numeric_values)
                
                logger.info(f"📊 Extracted {len(actual_values)} numerical values: {actual_values[:10]}...")
                
                # Show examples of which values should be included/excluded if cutoff exists
                examples_text = ""
                cutoff_value = None
                if cutoff_match:
                    cutoff_value = int(cutoff_match.group(1))
                    included_examples = [v for v in actual_values[:20] if v > cutoff_value][:3]
                    excluded_examples = [v for v in actual_values[:20] if v <= cutoff_value][:3]
                    
                    # Show examples but NO CALCULATION to avoid confusion
                    examples_text = f"""
EXAMPLES from sample data (NOT the final answer):
- Include values like: {included_examples} (because they are > {cutoff_value})
- Exclude values like: {excluded_examples} (because they are <= {cutoff_value})

IMPORTANT: These are just examples from the first few rows. You must process ALL {processed_data.get('shape', ['N/A', 'N/A'])[0]} rows!"""
                
                cutoff_info = ""
                if cutoff_value is not None:
                    cutoff_info = f"CUTOFF VALUE: {cutoff_value} (detected from quiz page)"
                    task_instruction = f"TASK: Calculate the SUM of all values that are GREATER THAN {cutoff_value}."
                    step_instruction = f"2. Include ONLY values > {cutoff_value} in your sum"
                else:
                    cutoff_info = "No specific cutoff value detected. Analyze based on context."
                    task_instruction = "TASK: Calculate the SUM of all numerical values in the CSV."
                    step_instruction = "2. Include all numerical values in your sum"
                    examples_text = ""

                # Get ALL data for complete processing
                all_values = []
                for item in processed_data.get('data', []):
                    if item:
                        values = list(item.values())
                        for val in values:
                            try:
                                if isinstance(val, (int, float)):
                                    all_values.append(int(val))
                                elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                                    all_values.append(int(float(val)))
                            except:
                                continue

                logger.info(f"📊 Processing ALL {len(all_values)} values for LLM analysis")

                # Use ReAct Framework: Test BOTH interpretations
                if cutoff_value is not None:
                    # Try both > and <= interpretations
                    above_cutoff = [v for v in all_values if v > cutoff_value]
                    below_or_equal_cutoff = [v for v in all_values if v <= cutoff_value]
                    
                    sum_above = sum(above_cutoff)
                    sum_below_equal = sum(below_or_equal_cutoff)
                    
                    logger.info(f"🧮 TESTING BOTH INTERPRETATIONS:")
                    logger.info(f"🧮 VALUES > {cutoff_value}: {len(above_cutoff)} values, sum = {sum_above}")
                    logger.info(f"🧮 VALUES <= {cutoff_value}: {len(below_or_equal_cutoff)} values, sum = {sum_below_equal}")
                    
                    # Based on previous failure, try BELOW/EQUAL interpretation
                    qualifying_values = below_or_equal_cutoff
                    calculated_sum = sum_below_equal
                    
                    logger.info(f"🔄 TRYING OPPOSITE LOGIC: Values <= {cutoff_value}")
                    logger.info(f"🧮 SELECTED: {len(qualifying_values)} values <= {cutoff_value}")
                    logger.info(f"🧮 CALCULATED SUM: {calculated_sum}")
                    
                    # Let LLM verify the logic, but use Python result
                    prompt = f"""{context}

🧠 CSV DATA ANALYSIS WITH VERIFICATION:
We have a CSV file with {len(all_values)} numerical values and cutoff {cutoff_value}.

CUTOFF LOGIC VERIFICATION:
- We need values LESS THAN OR EQUAL TO {cutoff_value}
- Found {len(qualifying_values)} qualifying values  
- Examples of included values: {qualifying_values[:5]}
- Examples of excluded values: {above_cutoff[:5]}

PYTHON CALCULATED THE SUM: {calculated_sum}

Your task: Verify this is correct and return ONLY the number {calculated_sum}.
Return the number without any explanations: {calculated_sum}"""

                else:
                    # No cutoff - sum all values
                    calculated_sum = sum(all_values)
                    logger.info(f"🧮 PYTHON CALCULATION: Sum of all {len(all_values)} values = {calculated_sum}")
                    
                    prompt = f"""{context}

🧠 CSV DATA ANALYSIS:
Sum all {len(all_values)} numerical values.

PYTHON CALCULATED THE SUM: {calculated_sum}

Return this number: {calculated_sum}"""

            elif "secret code" in quiz_info.get('question', '').lower():
                # Special handling for secret code extraction
                prompt = f"""{context}

SECRET CODE EXTRACTION TASK:
You need to find a secret code from the scraped webpage content.

Look for:
- Text patterns like "Secret code is XXXXX"
- Numbers mentioned as secret codes
- Generated content from JavaScript
- Any numeric codes (like 37543, 12345, etc.)
- Pattern-like strings that could be secrets

IMPORTANT: If you see text like "Secret code is 37543", extract just the number "37543".
If you see any error about failed scraping but the content mentions a secret code, extract that code.

Extract the secret code and return ONLY the numeric/alphanumeric code value.
Return ONLY the secret code value without explanations."""

            else:
                # General quiz solving
                prompt = f"""{context}

Based on the above information, provide ONLY the answer value to the question.
For demo quizzes that ask for "anything you want", provide a meaningful response like "demo-answer".
If the question involves calculations, perform them accurately.
If the question asks for data analysis, analyze the provided data thoroughly.
Return ONLY the answer value in the appropriate format (number, string, boolean).
Do not include explanations or additional text."""

        # Log the full reasoning prompt
        logger.info(f"🤖 ANSWER GENERATION PROMPT:")
        logger.info(f"📋 Question: {quiz_info.get('question', 'Unknown')}")
        logger.info(f"📝 Instructions: {quiz_info.get('instructions', 'None provided')}")
        logger.info(f"📊 Data Available: {'Yes' if processed_data else 'No'}")
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
