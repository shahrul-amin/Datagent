# Backend data models for chat functionality
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from datetime import datetime
import uuid

@dataclass
class ChatMessage:
    """Represents a single chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }

@dataclass
class FileUpload:
    """Represents an uploaded file"""
    filename: str
    original_filename: str
    file_path: str
    file_type: str
    size: int
    upload_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'size': self.size,
            'upload_timestamp': self.upload_timestamp.isoformat()
        }

@dataclass
class CodeExecution:
    """Represents a code execution result"""
    code: str
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    plots: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'plots': self.plots,
            'success': self.error is None
        }

@dataclass
class ChatRequest:
    """Represents a chat request from the client"""
    message: str
    chat_id: Optional[str] = None
    file_path: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatRequest':
        return cls(
            message=data.get('message', ''),
            chat_id=data.get('chat_id'),
            file_path=data.get('file_path'),
            history=data.get('history', [])
        )

@dataclass
class ChatResponse:
    """Represents a response to be sent to the client"""
    message: str
    code_executions: List[CodeExecution] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': self.message,
            'code_executions': [exec.to_dict() for exec in self.code_executions],
            'metadata': self.metadata or {}
        }
