# Flask application
from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
import matplotlib
matplotlib.use('Agg')
import google.generativeai as genai
import sys
sys.path.append('.')
from controllers import ChatController
from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Validate configuration
config.validate_config()

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize controllers
chat_controller = ChatController()

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        response, status_code = chat_controller.handle_health_check()
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        response, status_code = chat_controller.handle_chat_request()
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint for real-time responses"""
    try:
        return chat_controller.handle_chat_stream()
    except Exception as e:
        logger.error(f"Error in streaming chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)