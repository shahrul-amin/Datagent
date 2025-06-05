# Clean Flask application using MVVM architecture
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import matplotlib
matplotlib.use('Agg')
import google.generativeai as genai
import sys
sys.path.append('.')
from controllers import ChatController, FileController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize controllers
chat_controller = ChatController()
file_controller = FileController()

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

@app.route('/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
    try:
        response, status_code = file_controller.handle_file_upload()
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    """List uploaded files endpoint"""
    try:
        response, status_code = file_controller.handle_file_list()
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in files list endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete file endpoint"""
    try:
        response, status_code = file_controller.handle_file_delete(filename)
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in file delete endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/sequential', methods=['POST'])
def chat_sequential():
    """Sequential analysis endpoint with plot feedback"""
    try:
        response, status_code = chat_controller.handle_chat_request()
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in sequential chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/context/<session_id>', methods=['GET'])
def get_chat_context(session_id):
    """Get plot context for a session"""
    try:
        from services.plot_context_service import PlotContextService
        context_service = PlotContextService()
        plots = context_service.get_session_plots(session_id)
        summary = context_service.create_plot_summary(session_id)
        
        return jsonify({
            'session_id': session_id,
            'plot_count': len(plots),
            'plots': plots,
            'summary': summary
        }), 200
    except Exception as e:
        logger.error(f"Error getting chat context: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/context/<session_id>', methods=['DELETE'])
def clear_chat_context(session_id):
    """Clear plot context for a session"""
    try:
        from services.plot_context_service import PlotContextService
        context_service = PlotContextService()
        context_service.clear_session_context(session_id)
        
        return jsonify({
            'message': f'Context cleared for session {session_id}'
        }), 200
    except Exception as e:
        logger.error(f"Error clearing chat context: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)