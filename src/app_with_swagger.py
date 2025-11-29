from flask import Flask
from flask_restx import Api, Resource, fields
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

# Create Flask app
app = Flask(__name__)
CORS(app)

# Create API with Swagger documentation
api = Api(
    app,
    version='1.0',
    title='LLM Analysis Quiz API',
    description='Automated quiz solving with AI and data processing',
    doc='/docs/',  # Swagger UI will be at /docs/
    prefix='/api/v1'
)

# Create namespace
ns = api.namespace('quiz', description='Quiz operations')

# Define request/response models
quiz_request_model = api.model('QuizRequest', {
    'email': fields.String(required=True, description='Student email address', example='student@example.com'),
    'secret': fields.String(required=True, description='Student secret string', example='my-secret-123'),
    'url': fields.String(required=True, description='Quiz URL to solve', example='https://example.com/quiz-123')
})

success_response_model = api.model('SuccessResponse', {
    'status': fields.String(description='Status of the request', example='accepted'),
    'message': fields.String(description='Response message', example='Quiz solving started'),
    'url': fields.String(description='Quiz URL being processed', example='https://example.com/quiz-123')
})

error_response_model = api.model('ErrorResponse', {
    'error': fields.String(description='Error message', example='Invalid secret')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='Service status', example='running'),
    'message': fields.String(description='Service message', example='LLM Analysis Quiz API'),
    'email': fields.String(description='Configured student email', example='student@example.com'),
    'llm_provider': fields.String(description='LLM provider being used', example='AI Pipe (FREE)')
})

# Validate configuration on startup
try:
    Config.validate()
    logger.info("Configuration validated successfully")
    if Config.use_aipipe():
        logger.info("✅ Using AI Pipe (FREE) - Perfect for students!")
    else:
        logger.info("💳 Using OpenAI (PAID)")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

@ns.route('/health')
class Health(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_response_model)
    def get(self):
        """Health check endpoint - Check if the service is running"""
        llm_provider = "AI Pipe (FREE)" if Config.use_aipipe() else "OpenAI (PAID)"
        return {
            'status': 'running',
            'message': 'LLM Analysis Quiz API',
            'email': Config.STUDENT_EMAIL,
            'llm_provider': llm_provider
        }, 200

@ns.route('/solve')
class QuizSolver(Resource):
    @api.doc('solve_quiz')
    @api.expect(quiz_request_model)
    @api.response(200, 'Success', success_response_model)
    @api.response(400, 'Bad Request', error_response_model)
    @api.response(403, 'Forbidden', error_response_model)
    @api.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Solve a quiz task
        
        Submit a quiz URL and credentials to start the automated solving process.
        The system will:
        1. Fetch the quiz page using headless browser
        2. Parse instructions with AI
        3. Download and process any required data
        4. Generate and submit the answer
        5. Follow quiz chains if needed
        
        All within a 3-minute time limit.
        """
        start_time = time.time()
        
        try:
            data = api.payload
            
            # Check required fields
            if not all(key in data for key in ['email', 'secret', 'url']):
                logger.warning("Missing required fields")
                return {'error': 'Missing required fields: email, secret, url'}, 400
            
            # Verify secret
            if data['secret'] != Config.STUDENT_SECRET:
                logger.warning(f"Invalid secret from {data.get('email')}")
                return {'error': 'Invalid secret'}, 403
            
            # Verify email
            if data['email'] != Config.STUDENT_EMAIL:
                logger.warning(f"Email mismatch: {data.get('email')} != {Config.STUDENT_EMAIL}")
                return {'error': 'Email mismatch'}, 403
            
            quiz_url = data['url']
            logger.info(f"Received quiz request for URL: {quiz_url}")
            
            # Start quiz solving in background thread
            def solve_quiz_async():
                try:
                    from src.quiz_solver import QuizSolver
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
            
            return {
                'status': 'accepted',
                'message': 'Quiz solving started',
                'url': quiz_url
            }, 200
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {'error': 'Internal server error'}, 500

# Add a root redirect to docs
@app.route('/')
def redirect_to_docs():
    """Redirect root to Swagger documentation"""
    from flask import redirect
    return redirect('/docs/')

# Legacy endpoint for compatibility
@app.route('/quiz', methods=['POST'])
def legacy_quiz_endpoint():
    """Legacy endpoint - redirects to /api/v1/quiz/solve"""
    from flask import request, jsonify
    return QuizSolver().post()

if __name__ == '__main__':
    import os
    
    # Create necessary directories
    os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    logger.info(f"Starting server on port {Config.PORT}")
    logger.info(f"Swagger UI available at: http://localhost:{Config.PORT}/docs/")
    logger.info(f"API endpoints at: http://localhost:{Config.PORT}/api/v1/")
    
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
