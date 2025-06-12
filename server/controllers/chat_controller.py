# Chat controller for handling chat-related endpoints
import logging
from flask import request, jsonify, Response
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
    
    def handle_chat_stream(self):
        """Handle streaming chat requests for real-time response generation"""
        try:
            # Parse request data
            if request.content_type and 'application/json' in request.content_type:
                data = request.get_json()
                message = data.get('message')
                history = data.get('history', [])
                plot_images = data.get('plot_images', [])
                session_id = data.get('session_id', 'default')
            else:
                return {'error': 'Content-Type must be application/json for streaming'}, 400
            
            if not message:
                return {'error': 'Message is required'}, 400
            
            # Create chat request
            chat_request = ChatRequest(message=message, history=history)
            
            def generate_stream():
                """Generator function for streaming response"""
                try:
                    # Generate streaming response
                    for chunk in self.gemini_service.generate_response_stream(
                        chat_request, 
                        uploaded_file_path=None,  # File uploads not supported in streaming yet
                        plot_images=plot_images
                    ):
                        # Format as Server-Sent Events
                        yield f"data: {json.dumps({'chunk': chunk, 'type': 'text'})}\n\n"
                    
                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                    
                except Exception as e:
                    # Send error in stream
                    yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
            
            return Response(
                generate_stream(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                }
            )
            
        except Exception as e:
            logger.error(f"Error in streaming chat request: {e}")
            return {'error': 'Internal server error', 'details': str(e)}, 500
    
    def handle_chat_request_stream(self) -> Response:
        """Handle streaming chat requests"""
        try:
            # Parse request data
            data = request.get_json()
            if not data:
                return Response("Invalid request data", status=400)
            
            message = data.get('message')
            if not message:
                return Response("Message is required", status=400)
            
            history = data.get('history', [])
            session_id = data.get('session_id', 'default')
            
            # Create request object
            chat_request = ChatRequest(
                message=message,
                history=history
            )
            
            # Get uploaded file path if available
            uploaded_file_path = self.file_service.get_latest_uploaded_file()
            
            # Get plot images from previous conversation
            plot_images = self.sequential_workflow.get_session_plots_for_gemini(session_id)
            
            def generate_response():
                """Generator function for streaming response"""
                try:
                    # Stream response from Gemini
                    for chunk in self.gemini_service.generate_response_stream(
                        chat_request, 
                        uploaded_file_path, 
                        plot_images
                    ):
                        if chunk:
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                    
                    # Signal end of stream
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in streaming response: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return Response(
                generate_response(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
            
        except Exception as e:
            logger.error(f"Error in streaming chat request: {e}")
            return Response(f"Error: {str(e)}", status=500)
