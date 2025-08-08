from fastapi import FastAPI
from pydantic import BaseModel
from tasks import execute_task
from celery.result import AsyncResult
from tasks import app as celery_app

app = FastAPI()

class TaskRequest(BaseModel):
    task_type: str  # Example: "approve_batches"
    params: dict = {}

# 1️⃣ Assign Task Endpoint
@app.post("/assign-task/")
def assign_task(task: TaskRequest):
    # Send the task to Celery worker
    task_result = execute_task.delay(task.task_type, task.params)
    return {
        "message": f"Task '{task.task_type}' assigned successfully!",
        "task_id": task_result.id  # Return task_id for tracking
    }

# 2️⃣ Task Status/Result Endpoint
@app.get("/result/{task_id}")
def get_task_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,   # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result    # Your task return value
    }
