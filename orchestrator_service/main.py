"""
Orchestrator Service - Main FastAPI Application
Handles task assignment and result retrieval for AI Agent microservices.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add shared directory to Python path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio
import json

# Import shared modules
from config import REDIS_URL, LOG_LEVEL, FASTAPI_HOST, FASTAPI_PORT
from logging_config import setup_logging
from celery_client import get_celery_app

# Get API key from environment
API_KEY = os.getenv("API_KEY", "your_secret_key")

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Orchestrator Service",
    description="Orchestrates task assignment and result retrieval for AI Agent microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# API Key Authentication Middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Middleware to require API key authentication for all endpoints except /docs and /tasks/
    """
    # Skip authentication for docs only
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        response = await call_next(request)
        return response
    
    # Check for API key in headers
    api_key = request.headers.get("x-api-key")
    
    if not api_key or api_key != API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or missing API key. Include 'x-api-key' header."}
        )
    
    response = await call_next(request)
    return response

# Add CORS middleware for frontend integration - enable all origins for frontend-friendly access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Enable all origins for frontend integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Celery app
celery_app = get_celery_app()

# Create results directory for screenshots and downloads
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Mount static files for serving screenshots and results
app.mount("/static", StaticFiles(directory=str(results_dir)), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"WebSocket connected for task: {task_id}")

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"WebSocket disconnected for task: {task_id}")

    async def send_update(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update for task {task_id}: {e}")
                self.disconnect(task_id)

manager = ConnectionManager()

# Pydantic models
class TaskRequest(BaseModel):
    """Request model for task assignment"""
    task_type: str
    params: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    """Response model for task assignment"""
    task_id: str
    status: str
    message: str
    timestamp: str

class TaskResult(BaseModel):
    """Response model for task results"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: Optional[List[str]] = None
    screenshot_url: Optional[str] = None
    download_links: Optional[List[str]] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    timestamp: str

class ErrorResponse(BaseModel):
    """Structured error response model"""
    status: str = "error"
    message: str
    task_id: Optional[str] = None
    details: Dict[str, Any] = {}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "AI Agent Orchestrator Service",
        "service": "orchestrator_service",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/tasks/")
async def get_tasks() -> Dict[str, List[str]]:
    """
    Get list of available tasks for frontend discovery.
    This endpoint requires API key authentication.
    
    Returns:
        JSON with available_tasks list
    """
    try:
        logger.info("Fetching available tasks from worker service")
        
        # Get available tasks from worker service
        result = celery_app.send_task(
            name="worker.list_available_tasks",
            args=[],
            kwargs={}
        )
        
        # Wait for result with timeout
        task_info = result.get(timeout=10)
        available_tasks = task_info.get('available_tasks', [])
        
        logger.info(f"Retrieved {len(available_tasks)} available tasks")
        return {"available_tasks": available_tasks}
        
    except Exception as e:
        logger.error(f"Error fetching available tasks: {str(e)}")
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to fetch available tasks: {str(e)}",
                "task_id": None,
                "details": {"fallback_tasks": ["approve_batches", "test_task"]}
            }
        )

@app.post("/assign-task/", response_model=TaskResponse)
async def assign_task(task: TaskRequest):
    """
    Assign a task to the appropriate worker service via Celery
    
    Args:
        task: TaskRequest containing task_type and params
        
    Returns:
        TaskResponse with task_id and status
    """
    try:
        logger.info(f"Received task assignment request: {task.task_type}")
        
        # Send task to Celery worker using the new task name format
        celery_task = celery_app.send_task(
            name=f"worker.{task.task_type}",
            args=[task.params],
            kwargs={},
        )
        
        logger.info(f"Task {task.task_type} assigned with ID: {celery_task.id}")
        
        return TaskResponse(
            task_id=celery_task.id,
            status="assigned",
            message=f"Task '{task.task_type}' successfully assigned",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error assigning task {task.task_type}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to assign task: {str(e)}",
                "task_id": None,
                "details": {"task_type": task.task_type, "params": task.params}
            }
        )

@app.get("/result/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """
    Retrieve enhanced task result from Celery with logs, screenshots, and timestamps
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Enhanced TaskResult with logs, screenshot_url, download_links, timestamps
    """
    try:
        logger.info(f"Retrieving result for task: {task_id}")
        
        # Get task result from Celery
        async_result = celery_app.AsyncResult(task_id)
        
        # Base response structure
        base_response = {
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "logs": [],
            "screenshot_url": None,
            "download_links": [],
            "started_at": None,
            "finished_at": None
        }
        
        # Determine task status and extract enhanced information
        if async_result.ready():
            if async_result.successful():
                result_data = async_result.result or {}
                
                # Extract enhanced fields from result
                base_response.update({
                    "status": "completed",
                    "result": result_data,
                    "started_at": result_data.get("started_at"),
                    "finished_at": result_data.get("completed_at"),
                    "logs": result_data.get("logs", [])
                })
                
                # Handle screenshot URL
                if result_data.get("screenshot_path"):
                    screenshot_filename = Path(result_data["screenshot_path"]).name
                    base_response["screenshot_url"] = f"http://127.0.0.1:8000/static/{screenshot_filename}"
                
                # Handle download links
                if result_data.get("download_files"):
                    base_response["download_links"] = [
                        f"http://127.0.0.1:8000/static/{Path(file).name}" 
                        for file in result_data["download_files"]
                    ]
                
                return TaskResult(**base_response)
            else:
                # Handle failed tasks
                error_info = async_result.info or {}
                base_response.update({
                    "status": "failed",
                    "error": str(error_info.get("error", "Unknown error")),
                    "started_at": error_info.get("started_at"),
                    "finished_at": error_info.get("failed_at"),
                    "logs": error_info.get("logs", [])
                })
                
                # Handle error screenshot
                if error_info.get("screenshot_path"):
                    screenshot_filename = Path(error_info["screenshot_path"]).name
                    base_response["screenshot_url"] = f"http://127.0.0.1:8000/static/{screenshot_filename}"
                
                return TaskResult(**base_response)
        else:
            # Task is still pending/running
            task_info = async_result.info or {}
            base_response.update({
                "status": async_result.state.lower(),
                "started_at": task_info.get("started_at"),
                "logs": task_info.get("logs", [])
            })
            
            return TaskResult(**base_response)
            
    except Exception as e:
        logger.error(f"Error retrieving task result {task_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to retrieve task result: {str(e)}",
                "task_id": task_id,
                "details": {}
            }
        )

@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for live task updates
    
    Args:
        websocket: WebSocket connection
        task_id: Task ID to monitor
    """
    await manager.connect(websocket, task_id)
    try:
        while True:
            # Check task status and send updates
            async_result = celery_app.AsyncResult(task_id)
            
            update_message = {
                "task_id": task_id,
                "status": async_result.state.lower(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if async_result.info:
                update_message["progress"] = async_result.info.get("progress", 0)
                update_message["message"] = async_result.info.get("message", "")
            
            await manager.send_update(task_id, update_message)
            
            # If task is complete, send final update and close
            if async_result.ready():
                final_message = {
                    "task_id": task_id,
                    "status": "completed" if async_result.successful() else "failed",
                    "final": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_update(task_id, final_message)
                break
            
            # Wait before next update
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        manager.disconnect(task_id)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(task_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection via Celery
        celery_app.control.inspect().ping()
        redis_status = "healthy"
    except Exception as e:
        logger.warning(f"Redis health check failed: {str(e)}")
        redis_status = "unhealthy"
    
    return {
        "status": "ok",
        "service": "orchestrator",
        "version": "1.0.0",
        "redis_status": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Orchestrator Service starting up...")
    logger.info(f"Redis URL: {REDIS_URL}")
    logger.info(f"API Key authentication: {'Enabled' if API_KEY != 'your_secret_key' else 'Using default key'}")
    logger.info("Orchestrator Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Orchestrator Service shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False
    )
