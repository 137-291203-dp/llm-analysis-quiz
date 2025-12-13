import logging
import requests
import os
import json
import base64
from io import BytesIO
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from src.config import Config

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data sourcing, processing, analysis, and visualization"""
    
    def __init__(self):
        self.download_dir = Config.DOWNLOAD_DIR
        self.temp_dir = Config.TEMP_DIR
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_data_source(self, source_url, question_context="", base_url=None):
        """Process data from various sources - main entry point"""
        logger.info(f"📊 Processing data source: {source_url}")
        
        try:
            # Handle different data types based on URL/extension
            source_url_lower = source_url.lower()
            
            if source_url_lower.endswith('.csv'):
                logger.info("📈 Processing CSV file")
                filepath = self.download_file(source_url, base_url=base_url)
                df = self.read_csv(filepath)
                return {
                    'type': 'csv',
                    'data': df.to_dict('records') if len(df) <= 1000 else df.head(1000).to_dict('records'),
                    'summary': self.analyze_dataframe(df),
                    'shape': df.shape,
                    'columns': list(df.columns)
                }
            
            elif source_url_lower.endswith('.pdf'):
                logger.info("📄 Processing PDF file")
                filepath = self.download_file(source_url, base_url=base_url)
                return self.read_pdf(filepath)
            
            elif source_url_lower.endswith('.json'):
                logger.info("📊 Processing JSON file")
                filepath = self.download_file(source_url, base_url=base_url)
                return self.read_json(filepath)
            
            elif source_url_lower.endswith(('.xls', '.xlsx')):
                logger.info("📊 Processing Excel file")
                filepath = self.download_file(source_url, base_url=base_url)
                return self.read_excel(filepath)
            
            elif source_url_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                logger.info("🖼️ Processing image file")
                filepath = self.download_file(source_url, base_url=base_url)
                return {'type': 'image', 'path': filepath, 'description': 'Image file downloaded'}
            
            elif 'api' in source_url_lower:
                logger.info("🔗 Processing API endpoint")
                return self.fetch_api(source_url)
            
            else:
                # Try to determine type from content or treat as webpage
                logger.info("🌐 Processing as webpage")
                return self.scrape_webpage(source_url, base_url=base_url)
                
        except Exception as e:
            logger.error(f"❌ Error processing data source: {e}")
            return {"error": str(e), "source": source_url, "fallback": "Standard processing failed"}
    
    def download_file(self, url, filename=None, base_url=None):
        """Download a file from URL with relative URL support"""
        # Handle relative URLs
        if not url.startswith(('http://', 'https://')):
            if base_url:
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
                logger.info(f"Resolved relative file URL to: {url}")
            else:
                # Default to https scheme if no base URL provided
                url = f"https://tds-llm-analysis.s-anand.net/{url.lstrip('/')}"
                logger.info(f"Applied default base to relative file URL: {url}")
        
        logger.info(f"Downloading file from: {url}")
        
        try:
            response = requests.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if not filename:
                # Try to get filename from URL or Content-Disposition
                if 'Content-Disposition' in response.headers:
                    content_disp = response.headers['Content-Disposition']
                    if 'filename=' in content_disp:
                        filename = content_disp.split('filename=')[1].strip('"')
                else:
                    filename = url.split('/')[-1].split('?')[0] or 'downloaded_file'
            
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    def read_pdf(self, filepath):
        """Extract text and tables from PDF"""
        logger.info(f"Reading PDF: {filepath}")
        
        try:
            reader = PdfReader(filepath)
            data = {
                'num_pages': len(reader.pages),
                'pages': []
            }
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                data['pages'].append({
                    'page_num': i + 1,
                    'text': text
                })
            
            logger.info(f"Extracted {len(data['pages'])} pages from PDF")
            return data
            
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
    
    def read_csv(self, filepath):
        """Read CSV file"""
        logger.info(f"Reading CSV: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Read CSV with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            raise
    
    def read_excel(self, filepath):
        """Read Excel file"""
        logger.info(f"Reading Excel: {filepath}")
        
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(filepath)
            data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                data[sheet_name] = df
                logger.info(f"Read sheet '{sheet_name}' with shape: {df.shape}")
            
            return data
        except Exception as e:
            logger.error(f"Error reading Excel: {e}")
            raise
    
    def read_json(self, filepath):
        """Read JSON file"""
        logger.info(f"Reading JSON: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Read JSON successfully")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
            raise
    
    def scrape_webpage(self, url, base_url=None):
        """Scrape webpage content with support for relative URLs and aggressive JS execution"""
        # Handle relative URLs
        if url.startswith('/') and base_url:
            from urllib.parse import urljoin
            url = urljoin(base_url, url)
            logger.info(f"Resolved relative URL to: {url}")
        elif url.startswith('/'):
            # Default to https scheme if no base URL provided
            url = f"https://tds-llm-analysis.s-anand.net{url}"
            logger.info(f"Applied default base to relative URL: {url}")
        
        logger.info(f"Scraping webpage: {url}")
        
        try:
            # Try Playwright for JavaScript-heavy pages first
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Set a faster timeout for speed
                page.set_default_timeout(15000)
                
                response = page.goto(url, wait_until="networkidle")
                
                if response and response.status < 400:
                    # AGGRESSIVE JavaScript execution for secret code extraction
                    logger.info("🔄 Starting aggressive JavaScript execution for content extraction")
                    
                    # Multiple rounds of waiting and execution
                    for attempt in range(3):
                        page.wait_for_timeout(4000)  # Wait 4 seconds each round
                        
                        # Try multiple JavaScript triggers
                        try:
                            page.evaluate("window.dispatchEvent(new Event('DOMContentLoaded'))")
                            page.evaluate("window.dispatchEvent(new Event('load'))")
                            page.evaluate("window.dispatchEvent(new Event('readystatechange'))")
                            
                            # If this is a secret extraction page, try to execute module scripts
                            if 'demo-scrape-data' in url:
                                try:
                                    # Try to manually load and execute the demo-scrape.js if possible
                                    script_content = page.evaluate("""
                                        (() => {
                                            // Try to get any generated content
                                            const scripts = document.querySelectorAll('script[src]');
                                            for (const script of scripts) {
                                                console.log('Found script:', script.src);
                                            }
                                            
                                            // Try to find any dynamically generated text
                                            const allText = document.body.innerText || document.body.textContent || '';
                                            return allText;
                                        })()
                                    """)
                                    logger.info(f"🔍 Script evaluation attempt {attempt + 1}: {script_content[:100]}...")
                                except Exception as script_error:
                                    logger.info(f"⚠️ Script evaluation {attempt + 1} failed: {script_error}")
                            
                        except Exception as trigger_error:
                            logger.info(f"⚠️ JavaScript trigger {attempt + 1} failed: {trigger_error}")
                        
                        # Check if content has appeared
                        current_text = page.evaluate("document.body.innerText || document.body.textContent || ''")
                        if len(current_text.strip()) > 20:  # If we got substantial content
                            logger.info(f"✅ Content appeared after attempt {attempt + 1}")
                            break
                    
                    content = page.content()
                    text_content = page.evaluate("document.body.innerText || document.body.textContent || ''")
                    
                    # Additional attempt to extract any hidden or generated content
                    try:
                        all_content = page.evaluate("""
                            (() => {
                                const allText = [];
                                
                                // Get all text content including hidden elements
                                const walker = document.createTreeWalker(
                                    document.body,
                                    NodeFilter.SHOW_TEXT,
                                    null,
                                    false
                                );
                                
                                let node;
                                while (node = walker.nextNode()) {
                                    if (node.nodeValue.trim()) {
                                        allText.push(node.nodeValue.trim());
                                    }
                                }
                                
                                return allText.join(' ');
                            })()
                        """)
                        
                        if len(all_content) > len(text_content):
                            logger.info("🔍 Found additional content via DOM traversal")
                            text_content = all_content
                            
                    except Exception as extract_error:
                        logger.info(f"⚠️ Additional content extraction failed: {extract_error}")
                    
                    browser.close()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    tables = self._extract_tables(soup)
                    
                    logger.info(f"Scraped webpage with {len(tables)} tables, text length: {len(text_content)}")
                    logger.info(f"🔍 Extracted text content: {text_content[:200]}...")
                    
                    # Special handling for secret code extraction
                    if 'demo-scrape-data' in url and text_content:
                        # Try to extract secret code patterns directly
                        import re
                        secret_patterns = [
                            r'Secret code is (\d+)',
                            r'secret code:\s*(\d+)',
                            r'code:\s*(\d+)',
                            r'(\d{5,})'  # 5+ digit numbers
                        ]
                        
                        for pattern in secret_patterns:
                            match = re.search(pattern, text_content, re.IGNORECASE)
                            if match:
                                secret_code = match.group(1)
                                logger.info(f"🔍 Extracted secret code using pattern '{pattern}': {secret_code}")
                                # Add the secret code to the text for better LLM extraction
                                text_content = f"SECRET CODE FOUND: {secret_code}\n\nOriginal content:\n{text_content}"
                                break
                    
                    return {
                        'text': text_content.strip(),
                        'html': content,
                        'tables': tables,
                        'method': 'playwright_aggressive'
                    }
                else:
                    browser.close()
                    raise Exception(f"Failed to load with Playwright: {response.status if response else 'No response'}")
                    
        except Exception as playwright_error:
            logger.warning(f"Playwright scraping failed: {playwright_error}")
            
            # Fallback to requests
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text(separator='\n', strip=True)
                tables = self._extract_tables(soup)
                
                logger.info(f"Scraped webpage with {len(tables)} tables")
                return {
                    'text': text_content,
                    'html': str(soup),
                    'tables': tables,
                    'method': 'requests_fallback'
                }
                
            except Exception as requests_error:
                logger.error(f"Both Playwright and requests failed: {requests_error}")
                return {
                    'text': f"Failed to scrape {url}",
                    'html': '',
                    'tables': [],
                    'error': str(requests_error),
                    'method': 'failed'
                }
    
    def _extract_tables(self, soup):
        """Extract tables from BeautifulSoup object"""
        try:
            tables = []
            table_elements = soup.find_all('table')
            
            for i, table in enumerate(table_elements):
                # Convert table to pandas DataFrame
                try:
                    df = pd.read_html(str(table))[0]
                    tables.append({
                        'table_id': i,
                        'data': df.to_dict('records'),
                        'shape': df.shape,
                        'columns': list(df.columns)
                    })
                except Exception as table_error:
                    logger.warning(f"Failed to parse table {i}: {table_error}")
                    
            return tables
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
            return []
    
    def fetch_api(self, url, headers=None, params=None):
        """Fetch data from API"""
        logger.info(f"Fetching from API: {url}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                data = response.json()
            except:
                data = response.text
            
            logger.info(f"Fetched API data successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching API: {e}")
            raise
    
    def analyze_dataframe(self, df):
        """Perform basic analysis on DataFrame"""
        logger.info("Analyzing DataFrame")
        
        try:
            analysis = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'summary': df.describe().to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'sample_data': df.head(10).to_dict('records')
            }
            
            # Add numeric column statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis['numeric_stats'] = {
                    col: {
                        'sum': float(df[col].sum()),
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max())
                    }
                    for col in numeric_cols
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing DataFrame: {e}")
            raise
    
    def create_visualization(self, df, chart_type='bar', x_col=None, y_col=None):
        """Create visualization from DataFrame"""
        logger.info(f"Creating {chart_type} visualization")
        
        try:
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'bar' and x_col and y_col:
                plt.bar(df[x_col], df[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            elif chart_type == 'line' and x_col and y_col:
                plt.plot(df[x_col], df[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            elif chart_type == 'scatter' and x_col and y_col:
                plt.scatter(df[x_col], df[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
            elif chart_type == 'hist' and x_col:
                plt.hist(df[x_col], bins=20)
                plt.xlabel(x_col)
                plt.ylabel('Frequency')
            else:
                # Default: plot first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df[numeric_cols[0]].plot(kind='bar')
            
            plt.title(f'{chart_type.capitalize()} Chart')
            plt.tight_layout()
            
            # Save to bytes
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close()
            
            # Convert to base64
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            data_uri = f"data:image/png;base64,{img_base64}"
            
            logger.info("Visualization created successfully")
            return data_uri
            if ext == '.pdf':
                pdf_data = self.read_pdf(filepath)
                # If question mentions specific page, extract that
                if 'page' in question_context.lower():
                    import re
                    page_match = re.search(r'page\s+(\d+)', question_context.lower())
                    if page_match:
                        page_num = int(page_match.group(1))
                        if page_num <= len(pdf_data['pages']):
                            return pdf_data['pages'][page_num - 1]
                return pdf_data
                
            elif ext == '.csv':
                df = self.read_csv(filepath)
                return self.analyze_dataframe(df)
                
            elif ext in ['.xlsx', '.xls']:
                excel_data = self.read_excel(filepath)
                # Analyze each sheet
                result = {}
                for sheet_name, df in excel_data.items():
                    result[sheet_name] = self.analyze_dataframe(df)
                return result
                
            elif ext == '.json':
                return self.read_json(filepath)
                
            elif ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    return {'text': f.read()}
            
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return {'error': f'Unsupported file type: {ext}'}
                
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise
