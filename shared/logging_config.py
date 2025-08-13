"""
Shared Logging Configuration Module
Provides centralized logging setup for all services.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from config import LOG_LEVEL

def setup_logging(service_name: str = "ai-agent", log_dir: str = None) -> None:
    """
    Setup logging configuration with rotating file handler and console handler.
    
    Args:
        service_name: Name of the service for log identification
        log_dir: Directory to store log files (defaults to logs/ in project root)
    """
    # Determine log directory
    if log_dir is None:
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
    else:
        log_dir = Path(log_dir)
    
    # Ensure log directory exists
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Setup rotating file handler
    log_file = log_dir / "automation.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Setup service-specific logger
    service_logger = logging.getLogger(service_name)
    service_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Log initial setup message
    logging.info(f"Logging configured for {service_name}")
    logging.info(f"Log level: {LOG_LEVEL}")
    logging.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_function_call(func_name: str, args: dict = None, kwargs: dict = None) -> None:
    """
    Log function call details for debugging.
    
    Args:
        func_name: Name of the function being called
        args: Function arguments
        kwargs: Function keyword arguments
    """
    logger = logging.getLogger("function_calls")
    
    call_details = f"Calling {func_name}"
    if args:
        call_details += f" with args: {args}"
    if kwargs:
        call_details += f" with kwargs: {kwargs}"
    
    logger.debug(call_details)

def log_performance(func_name: str, duration: float, success: bool = True) -> None:
    """
    Log performance metrics for function execution.
    
    Args:
        func_name: Name of the function
        duration: Execution duration in seconds
        success: Whether the function executed successfully
    """
    logger = logging.getLogger("performance")
    
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"{func_name} - {status} - Duration: {duration:.3f}s")

def log_error_with_context(error: Exception, context: dict = None) -> None:
    """
    Log error with additional context information.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger = logging.getLogger("errors")
    
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    
    logger.error(error_msg, exc_info=True)

class ContextualLogger:
    """
    Logger wrapper that adds contextual information to all log messages.
    """
    
    def __init__(self, logger_name: str, context: dict = None):
        self.logger = logging.getLogger(logger_name)
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context information."""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message), **kwargs)
    
    def add_context(self, **context):
        """Add additional context to the logger."""
        self.context.update(context)
    
    def clear_context(self):
        """Clear all context information."""
        self.context.clear()

# Configure logging on module import
try:
    setup_logging()
except Exception as e:
    print(f"Failed to setup logging: {e}")
    # Fallback to basic logging configuration
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
