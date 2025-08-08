# Orchestrator Service

## Description
The Orchestrator Service is responsible for coordinating tasks between different services in the AI Agent system. It receives task requests from the frontend and distributes them to appropriate worker services.

## Features
- Task assignment endpoint (`/assign-task/`)
- Task result retrieval endpoint (`/result/{task_id}`)
- Health check endpoint (`/health`)
- RESTful API built with FastAPI

## Running the Service
```bash
cd orchestrator_service
pip install -r requirements.txt
python main.py
```

The service will start on `http://localhost:8000`

## API Endpoints
- `GET /` - Service status
- `POST /assign-task/` - Assign a new task
- `GET /result/{task_id}` - Get task result
- `GET /health` - Health check
