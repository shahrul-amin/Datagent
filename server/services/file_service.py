# File handling service for uploads and management
import os
import logging
from werkzeug.utils import secure_filename
from typing import Optional, List
import sys
sys.path.append('..')
from models.chat_models import FileUpload
from datetime import datetime

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file uploads and management"""
    
    def __init__(self, upload_folder: str = 'datasets'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file) -> str:
        """Save uploaded file and return filename"""
        try:
            if not file or not file.filename:
                raise ValueError("No file provided")
                
            if not self.is_allowed_file(file.filename):
                raise ValueError(f"File type not allowed: {file.filename}")
            
            # Secure the filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            
            # Save the file
            file.save(file_path)
            
            logger.info(f"File saved successfully: {file_path}")
            return filename  # Return just the filename for use as file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file.filename if file else 'unknown'}: {e}")
            raise

    def save_uploaded_file_detailed(self, file, original_filename: str) -> FileUpload:
        """Save uploaded file and return FileUpload model"""
        try:
            if not self.is_allowed_file(original_filename):
                raise ValueError(f"File type not allowed: {original_filename}")
            
            # Secure the filename
            filename = secure_filename(original_filename)
            file_path = os.path.join(self.upload_folder, filename)
            
            # Save the file
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = filename.rsplit('.', 1)[1].lower()
            
            return FileUpload(
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_type,
                size=file_size
            )
            
        except Exception as e:
            logger.error(f"Error saving file {original_filename}: {e}")
            raise
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """Get the full path of an uploaded file"""
        file_path = os.path.join(self.upload_folder, filename)
        return file_path if os.path.exists(file_path) else None
    
    def delete_file(self, filename: str) -> bool:
        """Delete an uploaded file"""
        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def list_files(self) -> List[str]:
        """List all uploaded files"""
        try:
            return [f for f in os.listdir(self.upload_folder) 
                   if os.path.isfile(os.path.join(self.upload_folder, f))]
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
