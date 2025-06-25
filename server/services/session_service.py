# Session service for tracking dataset context across conversations
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and dataset context"""
    
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour
    
    def set_dataset_context(self, session_id: str, file_path: str, filename: str = None) -> None:
        """Set the current dataset context for a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        
        self.sessions[session_id].update({
            'dataset_file_path': file_path,
            'dataset_filename': filename or file_path.split('/')[-1],
            'last_activity': time.time(),
            'has_dataset': True
        })
        
        logger.info(f"Set dataset context for session {session_id}: {filename} -> {file_path}")
        logger.info(f"Session data: {self.sessions[session_id]}")
    
    def get_dataset_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current dataset context for a session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired
        if time.time() - session.get('last_activity', 0) > self.session_timeout:
            self.clear_session(session_id)
            return None
        
        # Update last activity
        session['last_activity'] = time.time()
        
        return session if session.get('has_dataset') else None
    
    def has_dataset_context(self, session_id: str) -> bool:
        """Check if session has active dataset context"""
        context = self.get_dataset_context(session_id)
        return context is not None
    
    def get_dataset_file_path(self, session_id: str) -> Optional[str]:
        """Get the dataset file path for a session"""
        logger.info(f"Getting dataset file path for session: {session_id}")
        context = self.get_dataset_context(session_id)
        result = context.get('dataset_file_path') if context else None
        logger.info(f"Returning dataset file path: {result}")
        return result
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.get('last_activity', 0) > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

# Global session service instance
session_service = SessionService()
