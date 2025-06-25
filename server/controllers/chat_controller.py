# Chat controller
import logging
import os
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
from services.session_service import session_service

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
                        # Set dataset context for this session
                        session_service.set_dataset_context(session_id, uploaded_file_path, filename)
                        logger.info(f"File uploaded and session context set: {filename} -> {uploaded_file_path}")
                        
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
                
                logger.info(f"JSON request received - session_id: {session_id}, has_file_path: {'file_path' in data}")
                
                # Create chat request model
                chat_request = ChatRequest.from_dict(data)
                uploaded_file_path = None
                if chat_request.file_path:
                    uploaded_file_path = self.file_service.get_file_path(chat_request.file_path)
                    # Set dataset context for this session when file is provided
                    if uploaded_file_path:
                        session_service.set_dataset_context(session_id, uploaded_file_path, chat_request.file_path)
                        logger.info(f"JSON file upload - session context set: {chat_request.file_path} -> {uploaded_file_path}")

            if not chat_request.message:
                return {'error': 'Message is required'}, 400            # For follow-up responses, check if there's a recent uploaded file available
            if not uploaded_file_path:
                logger.info(f"No file path provided, checking session context for session: {session_id}")
                # First check session context for dataset
                session_dataset_path = session_service.get_dataset_file_path(session_id)
                logger.info(f"Session service returned dataset path: {session_dataset_path}")
                if session_dataset_path and os.path.exists(session_dataset_path):
                    uploaded_file_path = session_dataset_path
                    logger.info(f"Using session dataset context: {uploaded_file_path}")
                else:
                    logger.info(f"Session dataset path not found or doesn't exist, checking recent files")
                    # Fallback: Check for the most recent file in the datasets folder
                    import glob
                    dataset_files = glob.glob(os.path.join('datasets', '*'))
                    logger.info(f"Found {len(dataset_files)} dataset files in folder")
                    if dataset_files:
                        # Get the most recently modified file
                        uploaded_file_path = max(dataset_files, key=os.path.getmtime)
                        # Update session context
                        session_service.set_dataset_context(session_id, uploaded_file_path)
                        logger.info(f"Using most recent dataset file: {uploaded_file_path}")
                    else:
                        logger.warning(f"No dataset files found in datasets folder")
            else:
                logger.info(f"File path already provided: {uploaded_file_path}")
                        
            logger.info(f"Final dataset path for processing: {uploaded_file_path}")

            # Determine if this is a dataset analysis request requiring sequential workflow
            # More comprehensive detection for dataset-related queries
            dataset_keywords = [
                'analyze', 'analysis', 'visualize', 'plot', 'chart', 'graph', 'dataset',
                'data', 'correlation', 'distribution', 'pattern', 'trend', 'insight',
                'statistics', 'summary', 'overview', 'explore', 'show', 'display',
                'feature', 'variable', 'column', 'relationship', 'comparison', 'visualization'
            ]
            
            # Initial comprehensive analysis indicators
            comprehensive_analysis_keywords = [
                'analyze my data', 'analysis of', 'comprehensive analysis', 'dataset analysis',
                'analyze the dataset', 'analyze this data', 'analyze the data', 'complete analysis'
            ]
            
            # Check if this is an initial comprehensive analysis request
            is_initial_analysis = any(phrase in chat_request.message.lower() for phrase in comprehensive_analysis_keywords)
            
            # Check if this is any dataset-related request
            is_dataset_related = uploaded_file_path and (
                any(keyword in chat_request.message.lower() for keyword in dataset_keywords) or
                session_service.has_dataset_context(session_id) or
                (chat_request.history and len(chat_request.history) > 0)
            )
            
            # Use sequential workflow ONLY for initial comprehensive analysis
            # Use standard workflow for follow-up questions (but with dataset context)
            is_dataset_analysis = is_initial_analysis or workflow_type == 'sequential'
            
            logger.info(f"Dataset analysis detection - has_file: {uploaded_file_path is not None}, "
                       f"is_initial: {is_initial_analysis}, "
                       f"is_dataset_related: {is_dataset_related}, "
                       f"has_history: {chat_request.history and len(chat_request.history) > 0}, "
                       f"has_session_context: {session_service.has_dataset_context(session_id)}, "
                       f"final_decision: {is_dataset_analysis}")

            if is_dataset_analysis:
                # Use sequential workflow for comprehensive dataset analysis
                logger.info(f"Using sequential workflow for INITIAL dataset analysis (session: {session_id}, file: {uploaded_file_path})")
                processed_response = self.sequential_workflow.execute_sequential_analysis(
                    chat_request, 
                    uploaded_file_path, 
                    session_id
                )
            elif is_dataset_related:
                # Use standard workflow for follow-up questions but with dataset context
                logger.info(f"Using standard workflow for FOLLOW-UP dataset question (session: {session_id}, has_dataset: {uploaded_file_path is not None})")
                
                # Ensure we have a dataset file for follow-up questions
                if not uploaded_file_path:
                    logger.warning(f"Follow-up dataset question but no file path available - attempting fallback")
                    import glob
                    dataset_files = glob.glob(os.path.join('datasets', '*'))
                    if dataset_files:
                        uploaded_file_path = max(dataset_files, key=os.path.getmtime)
                        logger.info(f"Using fallback dataset file for follow-up: {uploaded_file_path}")
                
                # Generate response using Gemini with dataset context
                gemini_response = self.gemini_service.generate_response(
                    chat_request, 
                    uploaded_file_path,
                    plot_images=plot_images
                )
                
                # Process the response with step-by-step plot generation
                # Extract just the filename for the code executor
                dataset_filename = os.path.basename(uploaded_file_path) if uploaded_file_path else None
                processed_response = self.response_service.process_gemini_response_with_step_by_step_plots(
                    gemini_response, 
                    dataset_filename
                )
            else:
                # Use standard workflow for regular chat
                logger.info(f"Using standard workflow for general chat (session: {session_id}, has_dataset: {uploaded_file_path is not None})")
                
                # Generate response using Gemini, now with plot_images context
                gemini_response = self.gemini_service.generate_response(
                    chat_request, 
                    uploaded_file_path,
                    plot_images=plot_images
                )
                
                # Process the response with step-by-step plot generation
                # Extract just the filename for the code executor
                dataset_filename = os.path.basename(uploaded_file_path) if uploaded_file_path else None
                processed_response = self.response_service.process_gemini_response_with_step_by_step_plots(
                    gemini_response, 
                    dataset_filename
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
            # Handle both GET and POST for EventSource compatibility
            if request.method == 'GET':
                # EventSource connection - return SSE headers
                def generate_initial():
                    yield f"data: {json.dumps({'type': 'connected'})}\n\n"
                
                return Response(
                    generate_initial(),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                    }
                )
            
            # Handle POST request with data
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
            
            # For POST streaming, handle the same way as regular chat but with streaming response
            # Check for dataset context
            uploaded_file_path = None
            session_dataset_path = session_service.get_dataset_file_path(session_id)
            if session_dataset_path and os.path.exists(session_dataset_path):
                uploaded_file_path = session_dataset_path
                logger.info(f"Using session dataset context for streaming: {uploaded_file_path}")
            
            # Create chat request
            chat_request = ChatRequest(message=message, history=history, file_path=uploaded_file_path)
            
            def generate_stream():
                """Generator function for streaming response"""
                try:
                    # Generate streaming response
                    for chunk in self.gemini_service.generate_response_stream(
                        chat_request, 
                        uploaded_file_path=uploaded_file_path,
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
    
    def debug_session_state(self, session_id: str = 'default') -> Dict[str, Any]:
        """Debug endpoint to check session state"""
        try:
            context = session_service.get_dataset_context(session_id)
            has_context = session_service.has_dataset_context(session_id)
            file_path = session_service.get_dataset_file_path(session_id)
            
            import glob
            dataset_files = glob.glob(os.path.join('datasets', '*'))
            
            return {
                'session_id': session_id,
                'has_dataset_context': has_context,
                'dataset_context': context,
                'dataset_file_path': file_path,
                'available_dataset_files': dataset_files,
                'session_data': getattr(session_service, 'sessions', {})
            }
        except Exception as e:
            return {'error': str(e)}
