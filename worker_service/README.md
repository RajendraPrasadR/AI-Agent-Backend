# Worker Service

## Description
The Worker Service runs Celery workers that execute tasks assigned by the Orchestrator Service. It processes tasks asynchronously using Redis as the message broker and result backend.

## Features
- Celery-based task execution
- Redis integration for task queue management
- Asynchronous task processing
- Health check tasks

## Running the Service
```bash
cd worker_service
pip install -r requirements.txt
celery -A main worker --loglevel=info
```

## Available Tasks
- `execute_task` - Main task execution function
- `health_check_task` - Health check task

## Configuration
The service uses environment variables for configuration:
- `REDIS_URL` - Redis connection URL (default: redis://localhost:6379/0)
