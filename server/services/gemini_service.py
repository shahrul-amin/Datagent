# Gemini AI service for chat completions
import os
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List, Generator
import sys
sys.path.append('..')
from models.chat_models import ChatMessage, ChatRequest, ChatResponse
from utils.prompts import GeminiPrompts
from utils.gemini_factory import GeminiModelFactory
from utils.file_upload_cache import file_upload_cache
from config import config

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for handling Gemini AI interactions"""
    def __init__(self):
        self.model_factory = GeminiModelFactory()
        self.prompts = GeminiPrompts()
        
    def generate_response(self, request: ChatRequest, uploaded_file_path: Optional[str] = None, plot_images: Optional[List] = None) -> str:
        """Generate a response using Gemini AI with plot context"""
        try:
            # Create the model
            model = self.model_factory.create_model()
            
            # Prepare the content (prompt + file + plot images if any)
            content = self._prepare_content_with_plot_history(
                request.message, 
                uploaded_file_path, 
                request.history, 
                plot_images
            )
            
            # Generate response (non-streaming for compatibility)
            if config.ENABLE_STREAMING:
                # For now, we'll collect streaming response and return as string
                # Frontend streaming implementation can be added later
                response_chunks = []
                stream = self.model_factory.generate_content_stream_with_retry(model, content)
                for chunk in stream:
                    if chunk.text:
                        response_chunks.append(chunk.text)
                response_text = ''.join(response_chunks)
            else:
                response = self.model_factory.generate_content_with_retry(model, content)
                response_text = response.text
            
            if not response_text:
                raise ValueError("Empty response from Gemini")
                
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise

    def generate_response_stream(self, request: ChatRequest, uploaded_file_path: Optional[str] = None, plot_images: Optional[List] = None) -> Generator[str, None, None]:
        """Generate a streaming response using Gemini AI"""
        try:
            # Create the model
            model = self.model_factory.create_model()
            
            # Prepare the content
            content = self._prepare_content_with_plot_history(
                request.message, 
                uploaded_file_path, 
                request.history, 
                plot_images
            )
            
            # Generate streaming response
            stream = self.model_factory.generate_content_stream_with_retry(model, content)
            
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error generating streaming Gemini response: {e}")
            yield f"Error: {str(e)}"

    def _prepare_prompt(self, user_message: str, uploaded_file_path: Optional[str] = None, history: Optional[List] = None, plot_images: Optional[List] = None) -> str:
        """Prepare the prompt for Gemini with plot context"""
        logger.info(f"Preparing prompt - has_file: {uploaded_file_path is not None}, file_path: {uploaded_file_path}")
        logger.info(f"User message: {user_message[:100]}...")  # First 100 chars for debugging
        
        if uploaded_file_path:
            # Filter out PIL Image objects from plot_images for text prompt
            plot_metadata = []
            if plot_images:
                for item in plot_images:
                    if isinstance(item, dict):
                        plot_metadata.append(item)
                    # PIL Image objects are handled separately in _prepare_content_with_plot_history
            logger.info(f"Using data analysis prompt for dataset context")
            return self.prompts.get_data_analysis_prompt(user_message, uploaded_file_path, history, plot_metadata)
        else:
            logger.info(f"Using chat prompt for general conversation")
            return self.prompts.get_chat_prompt(user_message, history)
    
    def _prepare_content(self, user_message: str, uploaded_file_path: Optional[str] = None, history: Optional[List] = None, plot_images: Optional[List] = None):
        """Prepare content for Gemini, including file uploads and plot images if needed"""
        # Limit conversation history to prevent token overflow
        limited_history = self._limit_conversation_history(history)
        prompt = self._prepare_prompt(user_message, uploaded_file_path, limited_history, plot_images)
        
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            try:
                # Determine the correct MIME type based on file extension
                mime_type = self._get_mime_type(uploaded_file_path)
                
                # Check cache first
                try:
                    cached_file = file_upload_cache.get_cached_file(uploaded_file_path)
                    if cached_file:
                        logger.info(f"Using cached file upload: {cached_file.name}")
                        return [prompt, cached_file]
                    else:
                        # Upload file to Gemini with correct MIME type
                        uploaded_file = genai.upload_file(path=uploaded_file_path, mime_type=mime_type)
                        logger.info(f"Uploaded file to Gemini: {uploaded_file.name} with MIME type: {mime_type}")
                        
                        # Cache the uploaded file
                        file_upload_cache.cache_file(uploaded_file_path, uploaded_file, mime_type)
                        
                        # Return content with both text and file
                        return [prompt, uploaded_file]
                except Exception as cache_error:
                    logger.error(f"Cache operation failed, proceeding without cache: {cache_error}")
                    # Fallback: upload without cache
                    uploaded_file = genai.upload_file(path=uploaded_file_path, mime_type=mime_type)
                    logger.info(f"Uploaded file to Gemini without cache: {uploaded_file.name} with MIME type: {mime_type}")
                    return [prompt, uploaded_file]
                
            except Exception as e:
                logger.error(f"Error uploading file to Gemini: {e}")                # Fall back to text only
                return prompt
        else:
            return prompt
    
    def _prepare_content_with_plot_history(self, user_message: str, uploaded_file_path: Optional[str] = None,
                                         history: Optional[List] = None, plot_images: Optional[List] = None):
        """Prepare content for Gemini, including plot images from conversation history"""
        # Limit conversation history to prevent token overflow
        limited_history = self._limit_conversation_history(history)
        prompt = self._prepare_prompt(user_message, uploaded_file_path, limited_history, plot_images)
        content_parts = [prompt]
        
        # Add plot images from conversation history using PIL Images
        if plot_images:
            logger.info(f"Adding {len(plot_images)} plot images to Gemini context")
            
            # If plot_images contains PIL Image objects (from PlotContextService)
            if isinstance(plot_images, list) and plot_images:
                for idx, img in enumerate(plot_images):
                    try:
                        # PIL Images can be directly used with Gemini
                        content_parts.append(img)
                        logger.info(f"Added PIL plot image {idx + 1} to Gemini context")
                    except Exception as e:
                        logger.error(f"Error adding PIL plot image to context: {e}")
            
            # If plot_images contains base64 data (legacy support)
            elif isinstance(plot_images, list):
                for idx, plot_data in enumerate(plot_images):
                    if isinstance(plot_data, dict) and plot_data.get('type') == 'matplotlib':
                        try:
                            # Convert base64 matplotlib image to PIL Image
                            import base64
                            from PIL import Image
                            import io
                            
                            image_bytes = base64.b64decode(plot_data['data'])
                            pil_image = Image.open(io.BytesIO(image_bytes))
                            content_parts.append(pil_image)
                            
                            logger.info(f"Added base64 plot image {idx + 1} to Gemini context")
                        except Exception as e:
                            logger.error(f"Error adding base64 plot image to context: {e}")
        
        # Add uploaded dataset file if present
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            try:
                mime_type = self._get_mime_type(uploaded_file_path)
                
                # Check cache first
                try:
                    cached_file = file_upload_cache.get_cached_file(uploaded_file_path)
                    if cached_file:
                        content_parts.append(cached_file)
                        logger.info(f"Using cached file upload: {cached_file.name}")
                    else:
                        # Upload new file and cache it
                        uploaded_file = genai.upload_file(path=uploaded_file_path, mime_type=mime_type)
                        content_parts.append(uploaded_file)
                          # Cache the uploaded file
                        file_upload_cache.cache_file(uploaded_file_path, uploaded_file, mime_type)
                        logger.info(f"Uploaded and cached file: {uploaded_file.name}")
                except Exception as cache_error:
                    logger.error(f"Cache operation failed, proceeding without cache: {cache_error}")
                    # Fallback: upload without cache
                    uploaded_file = genai.upload_file(path=uploaded_file_path, mime_type=mime_type)
                    content_parts.append(uploaded_file)
                    logger.info(f"Uploaded file without cache: {uploaded_file.name}")
                    
            except Exception as e:
                logger.error(f"Error uploading dataset file to Gemini: {e}")

        return content_parts if len(content_parts) > 1 else content_parts[0]
    
    def _limit_conversation_history(self, history: Optional[List], max_messages: int = 3) -> Optional[List]:
        """Limit conversation history to prevent token overflow"""
        if not history:
            return history
            
        original_length = len(history)
        
        # Keep only the most recent messages
        if original_length > max_messages:
            limited_history = history[-max_messages:]
            logger.info(f"Limited conversation history from {original_length} to {len(limited_history)} messages to prevent token overflow")
            return limited_history
        
        # Additional safety: estimate token count and trim if needed
        estimated_tokens = self._estimate_token_count(history)
        if estimated_tokens > 800000:  # Conservative limit to stay well below 1M tokens
            # If still too many tokens, reduce to fewer messages
            while len(history) > 1 and estimated_tokens > 800000:
                history = history[-2:]  # Keep only last 2 messages
                estimated_tokens = self._estimate_token_count(history)
            logger.info(f"Further limited conversation history due to high token count (estimated: {estimated_tokens})")
        
        return history
    
    def _estimate_token_count(self, history: Optional[List]) -> int:
        """Estimate token count for conversation history (rough approximation)"""
        if not history:
            return 0
        
        total_chars = 0
        for msg in history:
            content = msg.get('content', '')
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, dict) and 'message' in content:
                total_chars += len(str(content['message']))
        
        # Rough estimation: 1 token ≈ 4 characters (this can vary)
        estimated_tokens = total_chars // 4
        return estimated_tokens
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get the correct MIME type for the file"""
        file_extension = file_path.split('.')[-1].lower()
        
        mime_types = {
            'csv': 'text/csv',
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif'
        }
        
        return mime_types.get(file_extension, 'text/plain')