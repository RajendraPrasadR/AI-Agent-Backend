import os
from celery import Celery
from services.batch_approval_service import approve_batches

app = Celery(
    "ai_agent",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Enables result tracking
)

@app.task(bind=True)
def execute_task(self, task_type: str, params: dict = {}):
    if task_type == "approve_batches":
        approve_batches()
        return "✅ ESC batch approval completed."
    else:
        return f"⚠️ Unknown task type: {task_type}"
