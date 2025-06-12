import google.generativeai as genai
import os
import sys
sys.path.append('..')
from config import config

class GeminiModelFactory:
    @staticmethod
    def create_model(model_name: str = None):
        """Create a Gemini model with configuration"""
        if model_name is None:
            model_name = config.GEMINI_MODEL_NAME
            
        genai.configure(api_key=config.GEMINI_API_KEY)
        return genai.GenerativeModel(
            model_name,
            generation_config=config.GENERATION_CONFIG,
            safety_settings=config.SAFETY_SETTINGS
        )
    
    @staticmethod
    def generate_content_with_retry(model, content, max_retries: int = None):
        """Generate content with retry logic and generation config"""
        if max_retries is None:
            max_retries = config.MAX_RETRY_ATTEMPTS
            
        for attempt in range(max_retries + 1):
            try:
                return model.generate_content(content)
            except AttributeError as e:
                if 'DESCRIPTOR' in str(e) and attempt < max_retries:
                    genai.configure(api_key=config.GEMINI_API_KEY)
                    model = GeminiModelFactory.create_model()
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < max_retries:
                    continue
                raise
        raise RuntimeError("Failed to generate content after all retries")
    
    @staticmethod
    def generate_content_stream_with_retry(model, content, max_retries: int = None):
        """Generate streaming content with retry logic"""
        if max_retries is None:
            max_retries = config.MAX_RETRY_ATTEMPTS
            
        for attempt in range(max_retries + 1):
            try:
                return model.generate_content(content, stream=True)
            except AttributeError as e:
                if 'DESCRIPTOR' in str(e) and attempt < max_retries:
                    genai.configure(api_key=config.GEMINI_API_KEY)
                    model = GeminiModelFactory.create_model()
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < max_retries:
                    continue
                raise
        raise RuntimeError("Failed to generate streaming content after all retries")
