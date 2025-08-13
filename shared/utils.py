"""
Shared Utility Functions
Common helper functions used across all services.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path to ensure exists
        
    Returns:
        Path object of the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dir_path}")
    return dir_path

def timestamped_filename(base_name: str, extension: str = "", timestamp_format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Generate a timestamped filename.
    
    Args:
        base_name: Base name for the file
        extension: File extension (with or without dot)
        timestamp_format: Timestamp format string
        
    Returns:
        Timestamped filename
    """
    timestamp = datetime.now().strftime(timestamp_format)
    
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    filename = f"{base_name}_{timestamp}{extension}"
    logger.debug(f"Generated timestamped filename: {filename}")
    return filename

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default

def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string with fallback.
    
    Args:
        data: Data to serialize
        default: Default JSON string if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, default=str, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return default

def generate_hash(data: Union[str, bytes, Dict], algorithm: str = "sha256") -> str:
    """
    Generate hash for given data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm to use
        
    Returns:
        Hex digest of the hash
    """
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    
    return hash_obj.hexdigest()

def validate_file_path(file_path: Union[str, Path], must_exist: bool = False) -> bool:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        
    Returns:
        True if valid, False otherwise
    """
    try:
        path_obj = Path(file_path)
        
        if must_exist and not path_obj.exists():
            return False
        
        # Check if parent directory is valid
        if not path_obj.parent.exists():
            return False
        
        return True
    except Exception as e:
        logger.warning(f"Invalid file path {file_path}: {e}")
        return False

def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid chars with
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove invalid characters for most filesystems
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized

def format_bytes(bytes_count: int) -> str:
    """
    Format byte count as human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds as human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def retry_operation(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry operation with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
        
    Returns:
        Function result or raises last exception
    """
    import time
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                sleep_time = delay * (backoff ** attempt)
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {sleep_time:.1f}s: {e}")
                time.sleep(sleep_time)
            else:
                logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
    
    raise last_exception

def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": format_bytes(psutil.virtual_memory().total),
        "disk_usage": format_bytes(psutil.disk_usage('/').total) if os.name != 'nt' else format_bytes(psutil.disk_usage('C:\\').total),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"Starting {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(f"{self.name} completed in {format_duration(duration)}")
        else:
            logger.error(f"{self.name} failed after {format_duration(duration)}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds if timing is complete."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
