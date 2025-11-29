#!/usr/bin/env python3
"""
Main runner script for LLM Analysis Quiz
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import app for gunicorn
from app_with_swagger import app
from config import Config

if __name__ == "__main__":
    print("Starting LLM Analysis Quiz with Swagger UI")
    print(f"Server: http://localhost:{Config.PORT}")
    print(f"Swagger UI: http://localhost:{Config.PORT}/docs/")
    
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)