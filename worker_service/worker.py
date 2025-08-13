"""
Worker Service - Celery Worker Entrypoint
Starts the Celery worker process for task execution.
"""

import os
import sys
import platform
from pathlib import Path
import logging

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from logging_config import setup_logging
from config import LOG_LEVEL

# Setup logging
setup_logging("worker_service")
logger = logging.getLogger(__name__)

def start_worker():
    """
    Start the Celery worker with appropriate configuration.
    """
    from tasks import app
    
    logger.info("Starting Celery worker...")
    logger.info(f"Platform: {platform.system()}")
    logger.info(f"Python version: {platform.python_version()}")
    
    # Determine worker configuration based on platform
    worker_args = [
        'worker',
        '--loglevel', LOG_LEVEL.lower(),
        '--concurrency', '1',  # Start with single worker for stability
        '--queues', 'worker_queue,automation_queue',
        '--hostname', f'worker@{platform.node()}',
    ]
    
    # Windows-specific configuration
    if platform.system() == 'Windows':
        worker_args.extend(['--pool', 'solo'])
        logger.info("Using solo pool for Windows compatibility")
    else:
        worker_args.extend(['--pool', 'prefork'])
        logger.info("Using prefork pool for Unix systems")
    
    # Add task routes
    worker_args.extend([
        '--queues', 'worker_queue,automation_queue,default'
    ])
    
    logger.info(f"Starting worker with args: {' '.join(worker_args)}")
    
    try:
        # Start the worker
        app.worker_main(worker_args)
    except KeyboardInterrupt:
        logger.info("Worker shutdown requested by user")
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        raise

def main():
    """
    Main entry point for the worker service.
    """
    try:
        logger.info("=" * 50)
        logger.info("AI Agent Worker Service Starting")
        logger.info("=" * 50)
        
        # Validate environment
        from config import REDIS_URL, CELERY_BROKER_URL
        logger.info(f"Broker URL: {CELERY_BROKER_URL or REDIS_URL}")
        
        # Import tasks to register them
        from tasks import TASK_MAPPING
        logger.info(f"Registered tasks: {list(TASK_MAPPING.keys())}")
        
        # Start worker
        start_worker()
        
    except Exception as e:
        logger.error(f"Failed to start worker service: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
