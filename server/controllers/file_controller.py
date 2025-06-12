# File upload controller
import logging
from flask import request, jsonify
from typing import Dict, Any
import sys
sys.path.append('..')
from services.file_service import FileService

logger = logging.getLogger(__name__)

class FileController:
    """Controller for file-related operations"""
    
    def __init__(self):
        self.file_service = FileService()
    
    def handle_file_upload(self) -> Dict[str, Any]:
        """Handle file upload requests"""
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            
            # Check if file is selected
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Save the file
            file_upload = self.file_service.save_uploaded_file(file, file.filename)
            
            return {
                'message': 'File uploaded successfully',
                'file': file_upload.to_dict()
            }, 200
            
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {'error': 'Failed to upload file', 'details': str(e)}, 500
    
    def handle_file_list(self) -> Dict[str, Any]:
        """Handle request to list uploaded files"""
        try:
            files = self.file_service.list_files()
            return {'files': files}, 200
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {'error': 'Failed to list files', 'details': str(e)}, 500
    
    def handle_file_delete(self, filename: str) -> Dict[str, Any]:
        """Handle file deletion requests"""
        try:
            success = self.file_service.delete_file(filename)
            if success:
                return {'message': f'File {filename} deleted successfully'}, 200
            else:
                return {'error': f'File {filename} not found'}, 404
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return {'error': 'Failed to delete file', 'details': str(e)}, 500
