# File upload cache system for optimizing Gemini file uploads
import os
import time
import hashlib
import json
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from config import config

logger = logging.getLogger(__name__)

class FileUploadCache:
    """Cache system for Gemini file uploads to avoid re-uploading the same files"""
    
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        self.cache_file = os.path.join(self.cache_dir, 'file_cache.json')
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _load_cache(self):
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file based on path, size, and modification time"""
        try:
            stat = os.stat(file_path)
            content = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate file hash: {e}")
            return str(time.time())
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        try:
            # Check TTL
            if time.time() - cache_entry['timestamp'] > config.FILE_UPLOAD_CACHE_TTL:
                return False
            
            # Check if Gemini file still exists (this is optional - Gemini handles cleanup)
            # We'll assume it's valid within TTL
            return True
        except Exception:
            return False
    
    def get_cached_file(self, file_path: str) -> Optional[Any]:
        """Get cached Gemini file object if available"""
        try:
            file_hash = self._get_file_hash(file_path)
            
            if file_hash in self.cache:
                cache_entry = self.cache[file_hash]
                
                if self._is_cache_valid(cache_entry):
                    logger.info(f"Using cached file upload for: {os.path.basename(file_path)}")
                    # Return a mock file object with the cached URI
                    class CachedFile:
                        def __init__(self, uri, name, mime_type):
                            self.uri = uri
                            self.name = name
                            self.mime_type = mime_type
                    
                    return CachedFile(
                        cache_entry['uri'],
                        cache_entry['name'], 
                        cache_entry['mime_type']
                    )
                else:
                    # Remove expired cache entry
                    del self.cache[file_hash]
                    self._save_cache()
            
            return None
        except Exception as e:
            logger.error(f"Error checking cache for file {file_path}: {e}")
            return None
    
    def cache_file(self, file_path: str, gemini_file: Any, mime_type: str):
        """Cache a Gemini file upload"""
        try:
            file_hash = self._get_file_hash(file_path)
            
            cache_entry = {
                'uri': gemini_file.uri,
                'name': gemini_file.name,
                'mime_type': mime_type,
                'timestamp': time.time(),
                'file_path': file_path
            }
            
            self.cache[file_hash] = cache_entry
            self._save_cache()
            
            logger.info(f"Cached file upload: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"Error caching file {file_path}: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if current_time - entry['timestamp'] > config.FILE_UPLOAD_CACHE_TTL:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                self._save_cache()
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def clear_cache(self):
        """Clear all cache entries"""
        self.cache = {}
        self._save_cache()
        logger.info("File upload cache cleared")

# Global cache instance
file_upload_cache = FileUploadCache()
