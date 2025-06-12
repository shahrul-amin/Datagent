# Configuration management for Datagent application
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash')
    
    # Generation Configuration
    GENERATION_CONFIG = {
        "temperature": float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        "max_output_tokens": int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', '8192')),
        "candidate_count": int(os.getenv('GEMINI_CANDIDATE_COUNT', '1')),
        "top_p": float(os.getenv('GEMINI_TOP_P', '0.95')),
        "top_k": int(os.getenv('GEMINI_TOP_K', '40'))
    }
    
    # Safety Settings
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH", 
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
    
    # File Upload Configuration
    FILE_UPLOAD_CACHE_TTL = int(os.getenv('FILE_UPLOAD_CACHE_TTL', '3600'))  # 1 hour
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '20971520'))  # 20MB
    
    # Performance Configuration
    ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'true').lower() == 'true'
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in environment variables")
        return True

# Create global config instance
config = Config()
