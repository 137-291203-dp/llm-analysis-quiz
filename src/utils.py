"""
Utility functions for the LLM Analysis Quiz application
"""
import logging
import json
import os
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging(log_file='logs/app.log'):
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    # Remove path separators and special characters
    filename = os.path.basename(filename)
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    return filename

def get_file_hash(filepath):
    """Get SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_json(data, filepath):
    """Save data as JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON to {filepath}")

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"Loaded JSON from {filepath}")
    return data

def format_time_remaining(seconds):
    """Format seconds into human-readable time"""
    if seconds < 0:
        return "0s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"

def truncate_text(text, max_length=1000):
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def extract_urls(text):
    """Extract URLs from text"""
    import re
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return urls

def is_valid_url(url):
    """Check if URL is valid"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def parse_answer_type(answer):
    """Determine the type of answer"""
    if isinstance(answer, bool):
        return "boolean"
    elif isinstance(answer, int):
        return "integer"
    elif isinstance(answer, float):
        return "float"
    elif isinstance(answer, str):
        if answer.startswith("data:"):
            return "base64_uri"
        return "string"
    elif isinstance(answer, dict):
        return "object"
    elif isinstance(answer, list):
        return "array"
    else:
        return "unknown"

def estimate_tokens(text):
    """Rough estimate of token count"""
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4

def create_submission_payload(email, secret, url, answer):
    """Create standardized submission payload"""
    payload = {
        "email": email,
        "secret": secret,
        "url": url,
        "answer": answer
    }
    
    # Log payload size
    payload_json = json.dumps(payload)
    size_bytes = len(payload_json.encode('utf-8'))
    size_kb = size_bytes / 1024
    
    logger.info(f"Payload size: {size_kb:.2f} KB")
    
    if size_bytes > 1_000_000:  # 1MB limit
        logger.warning(f"Payload exceeds 1MB limit: {size_kb:.2f} KB")
    
    return payload

def log_quiz_attempt(quiz_url, answer, result, elapsed_time):
    """Log quiz attempt details"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "quiz_url": quiz_url,
        "answer": answer,
        "answer_type": parse_answer_type(answer),
        "correct": result.get("correct") if result else None,
        "reason": result.get("reason") if result else None,
        "elapsed_time": elapsed_time,
        "next_url": result.get("url") if result else None
    }
    
    # Save to log file
    log_file = "logs/quiz_attempts.jsonl"
    os.makedirs("logs", exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return log_entry

def get_quiz_statistics():
    """Get statistics from quiz attempts log"""
    log_file = "logs/quiz_attempts.jsonl"
    
    if not os.path.exists(log_file):
        return {
            "total_attempts": 0,
            "correct": 0,
            "incorrect": 0,
            "success_rate": 0.0
        }
    
    attempts = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                attempts.append(json.loads(line))
            except:
                pass
    
    total = len(attempts)
    correct = sum(1 for a in attempts if a.get("correct") == True)
    incorrect = sum(1 for a in attempts if a.get("correct") == False)
    
    stats = {
        "total_attempts": total,
        "correct": correct,
        "incorrect": incorrect,
        "success_rate": (correct / total * 100) if total > 0 else 0.0,
        "avg_time": sum(a.get("elapsed_time", 0) for a in attempts) / total if total > 0 else 0.0
    }
    
    return stats

def clean_temp_files(max_age_hours=24):
    """Clean old temporary files"""
    import time
    from src.config import Config
    
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    
    cleaned = 0
    for directory in [Config.DOWNLOAD_DIR, Config.TEMP_DIR]:
        if not os.path.exists(directory):
            continue
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        cleaned += 1
                        logger.info(f"Cleaned old file: {filepath}")
                    except Exception as e:
                        logger.error(f"Error cleaning {filepath}: {e}")
    
    logger.info(f"Cleaned {cleaned} old files")
    return cleaned
