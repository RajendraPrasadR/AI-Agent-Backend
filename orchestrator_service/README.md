# Orchestrator Service

## Description
The Orchestrator Service is responsible for coordinating tasks between different services in the AI Agent system. It receives task requests from the frontend and distributes them to appropriate worker services.

## Features

- **Task Assignment**: Accept task requests and distribute them to appropriate worker services
- **Result Retrieval**: Fetch task results and status from Celery workers
- **Health Monitoring**: Monitor Redis connectivity and service health
- **CORS Support**: Ready for frontend integration
- **Comprehensive Logging**: Detailed logging with rotating file handlers
- **Error Handling**: Robust error handling with proper HTTP status codes

## Architecture

```
Frontend → Orchestrator Service → Celery/Redis → Worker Services
```

## API Endpoints

### Core Endpoints

- `GET /` - Service information and status
- `POST /assign-task/` - Assign a new task to worker services
- `GET /result/{task_id}` - Get task result by Celery task ID
- `GET /health` - Health check with Redis connectivity status

### API Documentation

- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - ReDoc API documentation

## Request/Response Models

### Task Assignment

**POST /assign-task/**

Request:
```json
{
  "task_type": "approve_batches",
  "params": {
    "batch_ids": [1, 2, 3],
    "auto_approve": true
  }
}
```

Response:
```json
{
  "task_id": "celery-task-uuid",
  "status": "assigned",
  "message": "Task 'approve_batches' successfully assigned",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Result Retrieval

**GET /result/{task_id}**

Response (Completed):
```json
{
  "task_id": "celery-task-uuid",
  "status": "completed",
  "result": {
    "processed_batches": 3,
    "approved": 2,
    "rejected": 1
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

Response (Failed):
```json
{
  "task_id": "celery-task-uuid",
  "status": "failed",
  "error": "Connection timeout to ESC system",
  "timestamp": "2024-01-01T12:05:00Z"
}
```

## Configuration

The service uses environment variables loaded from `.env` file:

```env
REDIS_URL=redis://redis:6379/0
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

## Running the Service

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp ../.env.template ../.env
# Edit .env with your configuration
```

3. Start Redis (if running locally):
```bash
redis-server
```

4. Run the service:
```bash
python main.py
```

The service will be available at http://localhost:8000

### Docker

Build and run with Docker:
```bash
docker build -t ai-agent-orchestrator .
docker run -p 8000:8000 --env-file ../.env ai-agent-orchestrator
```

### Docker Compose

Run with the full stack:
```bash
cd ..
docker-compose up orchestrator
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization

## Logging

Logs are written to:
- Console: Real-time development feedback
- File: `../logs/automation.log` with rotation (10MB, 5 backups)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Health Checks

The service provides health checks at `/health` endpoint:
- Service status
- Redis connectivity
- Timestamp information

## Error Handling

All endpoints include comprehensive error handling:
- Input validation errors (400)
- Task assignment failures (500)
- Result retrieval errors (500)
- Proper error messages and logging

## Integration

This service is designed to integrate with:
- Frontend applications (React, Vue, etc.)
- Worker services (Part B implementation)
- Monitoring tools (Flower, Prometheus)

## Development

### Code Structure

```
orchestrator_service/
├── main.py              # FastAPI application
├── celery_client.py     # Celery configuration
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```

### Adding New Endpoints

1. Add endpoint function to `main.py`
2. Define Pydantic models for request/response
3. Add proper error handling and logging
4. Update this documentation

### Testing

Run the service and test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Assign task
curl -X POST http://localhost:8000/assign-task/ \
  -H "Content-Type: application/json" \
  -d '{"task_type": "test_task", "params": {}}'

# Get result
curl http://localhost:8000/result/{task_id}
