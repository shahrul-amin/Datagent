# Chat controller for handling chat-related endpoints
import logging
from flask import request, jsonify
from typing import Dict, Any
import sys
import json
sys.path.append('..')
from models.chat_models import ChatRequest, ChatResponse
from services.gemini_service import GeminiService
from services.response_service import ResponseService
from services.file_service import FileService
from services.sequential_workflow_service import SequentialWorkflowManager

logger = logging.getLogger(__name__)

class ChatController:
    """Controller for chat-related operations"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.response_service = ResponseService()
        self.file_service = FileService()
        self.sequential_workflow = SequentialWorkflowManager()
    
    def handle_chat_request(self) -> Dict[str, Any]:
        """Handle incoming chat requests with sequential workflow support"""
        try:
            # Handle both JSON and FormData requests
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle file upload with FormData
                message = request.form.get('message')
                history_str = request.form.get('history', '[]')
                plot_images_str = request.form.get('plot_images', '[]')
                workflow_type = request.form.get('workflow_type', 'standard')
                session_id = request.form.get('session_id', 'default')
                
                try:
                    history = json.loads(history_str) if history_str else []
                except:
                    history = []
                try:
                    plot_images = json.loads(plot_images_str) if plot_images_str else []
                except:
                    plot_images = []
                    
                # Handle file upload
                uploaded_file_path = None
                if 'file' in request.files:
                    file = request.files['file']
                    if file and file.filename:
                        filename = self.file_service.save_uploaded_file(file)
                        uploaded_file_path = self.file_service.get_file_path(filename)
                        
                # Create chat request model
                chat_request = ChatRequest(message=message, history=history, file_path=uploaded_file_path)
                
            else:
                # Handle JSON request
                data = request.get_json()
                if not data:
                    return {'error': 'No data provided'}, 400
                    
                plot_images = data.get('plot_images', [])
                workflow_type = data.get('workflow_type', 'standard')
                session_id = data.get('session_id', 'default')
                
                # Create chat request model
                chat_request = ChatRequest.from_dict(data)
                uploaded_file_path = None
                if chat_request.file_path:
                    uploaded_file_path = self.file_service.get_file_path(chat_request.file_path)

            if not chat_request.message:
                return {'error': 'Message is required'}, 400

            # Determine if this is a dataset analysis request requiring sequential workflow
            is_dataset_analysis = (
                uploaded_file_path and 
                any(keyword in chat_request.message.lower() for keyword in [
                    'analyze', 'analysis', 'visualize', 'plot', 'chart', 'graph', 'dataset'
                ])
            ) or workflow_type == 'sequential'

            if is_dataset_analysis:
                # Use sequential workflow for comprehensive dataset analysis
                logger.info(f"Using sequential workflow for dataset analysis (session: {session_id})")
                processed_response = self.sequential_workflow.execute_sequential_analysis(
                    chat_request, 
                    uploaded_file_path, 
                    session_id
                )
            else:
                # Use standard workflow for regular chat
                logger.info("Using standard workflow for chat")
                # Generate response using Gemini, now with plot_images context
                gemini_response = self.gemini_service.generate_response(
                    chat_request, 
                    uploaded_file_path,
                    plot_images=plot_images
                )
                
                # Process the response with step-by-step plot generation
                processed_response = self.response_service.process_gemini_response_with_step_by_step_plots(
                    gemini_response, 
                    uploaded_file_path
                )
            
            return processed_response.to_dict(), 200
            
        except Exception as e:
            logger.error(f"Error in chat request: {e}")
            return {'error': 'Internal server error', 'details': str(e)}, 500
    
    def handle_health_check(self) -> Dict[str, Any]:
        """Handle health check requests"""
        return {'status': 'healthy', 'service': 'datagent-api'}, 200
