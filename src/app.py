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
    Config.validate()
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
        'email': Config.STUDENT_EMAIL
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
    if data['secret'] != Config.STUDENT_SECRET:
        logger.warning(f"Invalid secret from {data.get('email')}")
        return jsonify({'error': 'Invalid secret'}), 403
    
    # Verify email
    if data['email'] != Config.STUDENT_EMAIL:
        logger.warning(f"Email mismatch: {data.get('email')} != {Config.STUDENT_EMAIL}")
        return jsonify({'error': 'Email mismatch'}), 403
    
    quiz_url = data['url']
    logger.info(f"Received quiz request for URL: {quiz_url}")
    
    # Start quiz solving in background thread
    def solve_quiz_async():
        try:
            solver = QuizSolver(
                email=Config.STUDENT_EMAIL,
                secret=Config.STUDENT_SECRET,
                start_time=start_time
            )
            solver.solve_quiz_chain(quiz_url)
        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
    
    thread = threading.Thread(target=solve_quiz_async, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Quiz solving started (with checkpoint support)',
        'url': quiz_url
    }), 200

@app.route('/checkpoint', methods=['GET', 'DELETE'])
def manage_checkpoint():
    """
    Manage quiz checkpoint
    GET: Check if checkpoint exists
    DELETE: Clear checkpoint
    """
    try:
        # Create a temporary solver to access checkpoint methods
        solver = QuizSolver(
            email=Config.STUDENT_EMAIL,
            secret=Config.STUDENT_SECRET,
            start_time=time.time()
        )
        
        if request.method == 'GET':
            # Get checkpoint info
            checkpoint = solver.load_checkpoint()
            return jsonify({
                "exists": checkpoint is not None,
                "checkpoint": checkpoint,
                "message": f"Checkpoint {'found' if checkpoint else 'not found'}"
            }), 200
        
        elif request.method == 'DELETE':
            # Clear checkpoint
            solver.clear_checkpoint()
            return jsonify({
                "message": "Checkpoint cleared",
                "exists": False
            }), 200
            
    except Exception as e:
        logger.error(f"Error in checkpoint endpoint: {e}")
        return jsonify({"error": str(e)}), 500

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
    os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    logger.info(f"Starting server on port {Config.PORT}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
