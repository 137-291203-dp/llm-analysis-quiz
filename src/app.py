from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import threading
import time
from src.config import Config
from src.quiz_solver import QuizSolver

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Validate configuration on startup
try:
    config.Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'LLM Analysis Quiz API',
        'email': config.Config.STUDENT_EMAIL
    }), 200

@app.route('/quiz', methods=['POST'])
def handle_quiz():
    """
    Main endpoint to receive quiz tasks
    Expected JSON payload:
    {
        "email": "student email",
        "secret": "student secret",
        "url": "quiz URL"
    }
    """
    start_time = time.time()
    
    # Validate JSON payload
    if not request.is_json:
        logger.warning("Invalid JSON received")
        return jsonify({'error': 'Invalid JSON payload'}), 400
    
    data = request.get_json()
    
    # Check required fields
    if not all(key in data for key in ['email', 'secret', 'url']):
        logger.warning("Missing required fields")
        return jsonify({'error': 'Missing required fields: email, secret, url'}), 400
    
    # Verify secret
    if data['secret'] != config.Config.STUDENT_SECRET:
        logger.warning(f"Invalid secret from {data.get('email')}")
        return jsonify({'error': 'Invalid secret'}), 403
    
    # Verify email
    if data['email'] != config.Config.STUDENT_EMAIL:
        logger.warning(f"Email mismatch: {data.get('email')} != {config.Config.STUDENT_EMAIL}")
        return jsonify({'error': 'Email mismatch'}), 403
    
    quiz_url = data['url']
    logger.info(f"Received quiz request for URL: {quiz_url}")
    
    # Start quiz solving in background thread
    def solve_quiz_async():
        try:
            solver = QuizSolver(
                email=config.Config.STUDENT_EMAIL,
                secret=config.Config.STUDENT_SECRET,
                start_time=start_time
            )
            solver.solve_quiz_chain(quiz_url)
        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
    
    thread = threading.Thread(target=solve_quiz_async, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Quiz solving started',
        'url': quiz_url
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import os
    
    # Create necessary directories
    os.makedirs(config.Config.DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(config.Config.TEMP_DIR, exist_ok=True)
    
    logger.info(f"Starting server on port {config.Config.PORT}")
    app.run(host='0.0.0.0', port=config.Config.PORT, debug=False)
