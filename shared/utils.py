"""
Shared utilities for AI Agent services
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any

def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration for a service"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_file = os.path.join(log_dir, f"{service_name}.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(service_name)
    logger.info(f"Logging initialized for {service_name}")
    
    return logger

def get_service_info(service_name: str, version: str = "1.0.0") -> Dict[str, Any]:
    """Get standard service information"""
    return {
        "service": service_name,
        "version": version,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "message": f"Hello, I'm {service_name.replace('_', ' ').title()}"
    }

def validate_task_params(task_type: str, params: Dict[str, Any]) -> bool:
    """Validate task parameters (placeholder implementation)"""
    # This will be expanded based on specific task requirements
    if not isinstance(task_type, str) or not task_type.strip():
        return False
    
    if not isinstance(params, dict):
        return False
    
    return True

def format_error_response(error: Exception, service_name: str) -> Dict[str, Any]:
    """Format error response consistently across services"""
    return {
        "error": True,
        "service": service_name,
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "type": type(error).__name__
    }

class ServiceConfig:
    """Configuration management for services"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    def get_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return {
            "redis_url": self.redis_url,
            "log_level": self.log_level,
            "environment": self.environment
        }
