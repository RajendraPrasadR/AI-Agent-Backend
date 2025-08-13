"""
Celery Client Configuration
Manages Celery app connection for the Orchestrator Service.
"""

import os
import sys
from pathlib import Path
import logging

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from celery import Celery
from config import REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

logger = logging.getLogger(__name__)

# Celery configuration
CELERY_CONFIG = {
    'broker_url': CELERY_BROKER_URL or REDIS_URL,
    'result_backend': CELERY_RESULT_BACKEND or REDIS_URL,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 30 * 60,  # 30 minutes
    'task_soft_time_limit': 25 * 60,  # 25 minutes
    'worker_prefetch_multiplier': 1,
    'task_acks_late': True,
    'worker_disable_rate_limits': False,
    'task_compression': 'gzip',
    'result_compression': 'gzip',
    'result_expires': 3600,  # 1 hour
    'task_routes': {
        'worker.*': {'queue': 'worker_queue'},
        'automation.*': {'queue': 'automation_queue'},
    },
    'task_default_queue': 'default',
    'task_default_exchange': 'default',
    'task_default_exchange_type': 'direct',
    'task_default_routing_key': 'default',
}

# Global Celery app instance
_celery_app = None

def create_celery_app() -> Celery:
    """
    Create and configure Celery application instance.
    
    Returns:
        Configured Celery application
    """
    try:
        logger.info("Creating Celery application...")
        
        app = Celery('ai_agent_orchestrator')
        app.config_from_object(CELERY_CONFIG)
        
        # Update configuration with any additional settings
        app.conf.update(
            broker_connection_retry_on_startup=True,
            broker_connection_retry=True,
            broker_connection_max_retries=10,
        )
        
        logger.info(f"Celery app created with broker: {CELERY_CONFIG['broker_url']}")
        logger.info(f"Result backend: {CELERY_CONFIG['result_backend']}")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Celery app: {str(e)}")
        raise

def get_celery_app() -> Celery:
    """
    Get or create the global Celery application instance.
    
    Returns:
        Celery application instance
    """
    global _celery_app
    
    if _celery_app is None:
        _celery_app = create_celery_app()
    
    return _celery_app

def test_celery_connection() -> bool:
    """
    Test the Celery broker connection.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        app = get_celery_app()
        
        # Test broker connection
        with app.connection() as conn:
            conn.ensure_connection(max_retries=3)
        
        logger.info("Celery broker connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Celery broker connection test failed: {str(e)}")
        return False

# Initialize Celery app on module import
try:
    _celery_app = create_celery_app()
    logger.info("Celery client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Celery client: {str(e)}")
    _celery_app = None
