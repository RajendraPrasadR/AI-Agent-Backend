import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
app = Celery(
    "ai_agent_worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True)
def execute_task(self, task_type: str, params: dict = {}):
    """Placeholder task execution function"""
    print(f"Hello, I'm Worker Service executing task: {task_type}")
    
    if task_type == "test_task":
        return f"Worker Service completed test_task with params: {params}"
    elif task_type == "approve_batches":
        return "Worker Service: Batch approval task placeholder"
    else:
        return f"Worker Service: Unknown task type '{task_type}'"

@app.task
def health_check_task():
    """Health check task"""
    return "Worker Service is healthy"

if __name__ == "__main__":
    print("Hello, I'm Worker Service")
    print("Starting Celery worker...")
    app.start()
