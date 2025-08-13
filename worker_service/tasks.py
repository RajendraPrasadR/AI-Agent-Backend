"""
Worker Service - Celery Tasks
Generic task execution with mapping to automation service functions.
"""

import os
import sys
from pathlib import Path
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Add shared and automation service directories to Python path
project_root = Path(__file__).parent.parent
shared_path = project_root / "shared"
automation_path = project_root / "automation_service"
sys.path.insert(0, str(shared_path))
sys.path.insert(0, str(automation_path))

from celery import Celery
from config import REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from logging_config import setup_logging
from utils import Timer, ensure_dir

# Setup logging
setup_logging("worker_service")
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery('ai_agent_worker')

# Celery configuration
app.conf.update(
    broker_url=CELERY_BROKER_URL or REDIS_URL,
    result_backend=CELERY_RESULT_BACKEND or REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression='gzip',
    result_compression='gzip',
    result_expires=3600,  # 1 hour
    task_routes={
        'worker.*': {'queue': 'worker_queue'},
        'automation.*': {'queue': 'automation_queue'},
    },
    task_default_queue='worker_queue',
    task_default_exchange='worker_queue',
    task_default_exchange_type='direct',
    task_default_routing_key='worker_queue',
)

# Import automation service functions
try:
    import batch_approval_service
except ImportError:
    batch_approval_service = None
    logger.warning("batch_approval_service not available")

# Task mapping - maps task names to their functions
# 
# HOW TO ADD NEW TASKS:
# 1. Import your service module at the top (e.g., import certificate_service)
# 2. Add your task to this dictionary: "task_name": module.function_name
# 3. The task will be automatically registered with Celery on startup
# 4. No need to restart services - just restart the worker process
# 
# Example:
#   import certificate_service
#   task_map = {
#       "approve_batches": batch_approval_service.approve_batches,
#       "generate_certificates": certificate_service.generate_certificates,
#       "send_notifications": notification_service.send_bulk_notifications
#   }
#
task_map = {
    "approve_batches": batch_approval_service.approve_batches if batch_approval_service else None,
    # "generate_certificates": certificate_service.generate_certificates,  # Example for future tasks
    "test_task": None,  # Will be set to local function below
}

# Legacy mapping for backward compatibility
TASK_MAPPING = {
    'approve_batches': 'batch_approval_service.approve_batches',
    'test_task': 'test_automation_task',
}

def get_automation_function(task_name: str) -> Optional[callable]:
    """
    Get automation function from task_map.
    
    Args:
        task_name: Name of the task to execute
        
    Returns:
        Function to execute or None if not found
    """
    if task_name not in task_map:
        logger.error(f"Unknown task name: {task_name}")
        return None
    
    func = task_map[task_name]
    if func is None:
        logger.error(f"Task function not available for: {task_name}")
        return None
    
    logger.info(f"Retrieved function for task: {task_name}")
    return func

def test_automation_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test automation task for development and testing.
    
    Args:
        params: Task parameters
        
    Returns:
        Test result dictionary
    """
    import time
    import random
    
    logger.info(f"Executing test automation task with params: {params}")
    
    # Simulate work
    work_duration = params.get('duration', random.uniform(1, 5))
    time.sleep(work_duration)
    
    # Simulate success/failure
    success_rate = params.get('success_rate', 0.8)
    success = random.random() < success_rate
    
    if success:
        return {
            'status': 'completed',
            'approved_count': random.randint(1, 10),
            'details': [
                {
                    'item': f'test_item_{i}',
                    'action': 'approved',
                    'timestamp': datetime.utcnow().isoformat()
                } for i in range(random.randint(1, 5))
            ],
            'summary': f'Test task completed successfully in {work_duration:.2f}s',
            'execution_time': work_duration
        }
    else:
        raise Exception("Test task failed (simulated failure)")

@app.task(bind=True, name='worker.execute_task')
def execute_task(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic task executor that maps task types to automation functions.
    
    Args:
        task_type: Type of task to execute
        params: Task parameters
        
    Returns:
        Task execution result
    """
    task_id = self.request.id
    start_timestamp = datetime.utcnow().isoformat()
    
    # Enhanced logging with task ID and timestamp
    logger.info(f"[TASK_START] Task ID: {task_id} | Type: {task_type} | Started: {start_timestamp}")
    
    try:
        with Timer(f"Task {task_type}") as timer:
            # Get automation function from task_map
            automation_func = get_automation_function(task_type)
            if not automation_func:
                raise ValueError(f"No automation function found for task: {task_type}")
            
            # Update task state
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'running',
                    'task_type': task_type,
                    'started_at': start_timestamp
                }
            )
            
            # Execute automation function
            logger.info(f"[TASK_EXECUTING] Task ID: {task_id} | Executing function for {task_type}")
            result = automation_func(params)
            
            # Ensure result has required structure
            if not isinstance(result, dict):
                result = {'result': result}
            
            # Add metadata to result
            completed_timestamp = datetime.utcnow().isoformat()
            result.update({
                'task_id': task_id,
                'task_type': task_type,
                'status': 'completed',
                'started_at': start_timestamp,
                'completed_at': completed_timestamp,
                'execution_time': timer.duration
            })
            
            # Enhanced success logging
            logger.info(f"[TASK_SUCCESS] Task ID: {task_id} | Type: {task_type} | Completed: {completed_timestamp} | Duration: {timer.duration:.2f}s")
            return result
            
    except Exception as e:
        error_msg = str(e)
        failed_timestamp = datetime.utcnow().isoformat()
        
        # Enhanced error logging with task ID and timestamp
        logger.error(f"[TASK_FAILED] Task ID: {task_id} | Type: {task_type} | Failed: {failed_timestamp} | Error: {error_msg}")
        
        # Save error screenshot if available
        screenshot_path = None
        try:
            # Try to get screenshot from automation service if it's a Selenium error
            if 'automation_service' in sys.modules:
                screenshot_dir = ensure_dir(project_root / "logs" / "screenshots")
                screenshot_path = str(screenshot_dir / f"error_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                # This would be implemented in the automation service
        except Exception as screenshot_error:
            logger.warning(f"[TASK_SCREENSHOT_ERROR] Task ID: {task_id} | Failed to capture error screenshot: {screenshot_error}")
        
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'task_type': task_type,
                'error': error_msg,
                'started_at': start_timestamp,
                'failed_at': failed_timestamp,
                'screenshot_path': screenshot_path
            }
        )
        
        # Re-raise the exception so Celery marks the task as failed
        raise

@app.task(name='worker.health_check')
def health_check() -> Dict[str, Any]:
    """
    Worker health check task.
    
    Returns:
        Health status information
    """
    logger.info("Worker health check requested")
    
    return {
        'status': 'healthy',
        'worker_id': os.getpid(),
        'timestamp': datetime.utcnow().isoformat(),
        'available_tasks': list(TASK_MAPPING.keys()),
        'celery_version': app.version
    }

# Register task mapping for monitoring
@app.task(name='worker.list_available_tasks')
def list_available_tasks() -> Dict[str, Any]:
    """
    List all available task types and their mappings.
    
    Returns:
        Dictionary of available tasks
    """
    return {
        'available_tasks': list(task_map.keys()),
        'task_mapping': TASK_MAPPING,
        'total_count': len(task_map),
        'timestamp': datetime.utcnow().isoformat()
    }

# Set local test_task function in task_map after definition
task_map["test_task"] = test_automation_task

# Dynamic task registration
def register_tasks():
    """
    Dynamically register Celery tasks from task_map.
    """
    for task_name in task_map.keys():
        if task_map[task_name] is not None:  # Only register available tasks
            # Create a dynamic task for each entry in task_map
            task_func = app.task(bind=True, name=f'worker.{task_name}')(
                lambda self, params, tn=task_name: execute_task(self, tn, params)
            )
            logger.info(f"Registered dynamic task: worker.{task_name}")
        else:
            logger.warning(f"Skipping registration for unavailable task: {task_name}")

# Register all tasks dynamically
register_tasks()

if __name__ == '__main__':
    # For testing purposes
    logger.info("Worker service tasks module loaded")
    logger.info(f"Available tasks: {list(task_map.keys())}")
    logger.info(f"Legacy task mapping: {list(TASK_MAPPING.keys())}")
