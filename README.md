# AI Agent Backend - Frontend-Ready Microservices

A production-ready Python microservices backend for AI Agent automation with full frontend integration support. Features dynamic task management, WebSocket live updates, and structured JSON APIs.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │───▶│  Orchestrator   │───▶│   Celery/Redis  │
│   (Lovable AI)  │    │    Service      │    │   Task Queue    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Shared      │    │  Worker Services│
                       │   Components    │    │   (Part B)      │
                       └─────────────────┘    └─────────────────┘
```

## Project Structure

```
ai-agent-backend/
├── orchestrator_service/          # FastAPI REST API service
│   ├── main.py                   # Main application with WebSocket support
│   ├── celery_client.py          # Celery configuration
│   └── requirements.txt          # Service dependencies
├── worker_service/                # Celery worker service
│   ├── tasks.py                  # Task definitions and dynamic registration
│   └── main.py                   # Worker startup
├── automation_service/            # Selenium automation service
│   ├── batch_approval_service.py # Batch approval automation
│   └── __init__.py               # Service initialization
├── shared/                        # Shared utilities and configuration
│   ├── config.py                 # Environment configuration
│   ├── logging_config.py         # Logging setup
│   ├── utils.py                  # Common utility functions
│   └── celery_client.py          # Celery client configuration
├── results/                       # Screenshots and download files
├── logs/                          # Application logs and screenshots
├── .env                          # Environment variables
├── requirements.txt              # Combined dependencies
└── README.md                     # This documentation
```

## ✨ Features

### Core Architecture
- ✅ **Orchestrator Service**: FastAPI-based REST API for task coordination
- ✅ **Worker Service**: Celery-based distributed task processing
- ✅ **Automation Service**: Selenium-based batch approval automation
- ✅ **Shared Components**: Configuration, logging, and utilities
- ✅ **Redis Integration**: Task queue and result backend

### Frontend-Ready APIs
- ✅ **JSON-Only Responses**: All endpoints return structured JSON (no HTML)
- ✅ **Dynamic Task Discovery**: `/tasks/` endpoint for available task types
- ✅ **Enhanced Results**: Logs, screenshots, timestamps, and download links
- ✅ **WebSocket Support**: Live task updates via `/ws/task/{task_id}`
- ✅ **Static File Serving**: Screenshots and results accessible via `/static/`
- ✅ **CORS Enabled**: Full cross-origin support for web frontends

### Security & Error Handling
- ✅ **API Key Authentication**: Secure endpoint access with `x-api-key` header
- ✅ **Structured Error Responses**: Consistent error JSON format
- ✅ **Comprehensive Logging**: Task lifecycle tracking with timestamps
- ✅ **Screenshot Capture**: Automatic error and success screenshots

### Task Management
- ✅ **Modular Task System**: Easy addition of new tasks via `task_map`
- ✅ **Dynamic Registration**: No service restart needed for new tasks
- ✅ **Selenium Automation**: Configurable timeout and robust error handling

### Part B (Future Implementation)

- ⏳ Worker services for specific automation tasks
- ⏳ ESC system integration
- ⏳ Batch processing capabilities
- ⏳ Additional task types and handlers

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Redis (if running locally)

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd ai-agent-backend
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Choose your deployment method**:

#### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f orchestrator

# Stop services
docker-compose down
```

#### Option B: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis
redis-server

# Start orchestrator service
cd orchestrator_service
python main.py
```

### Verification

1. **Check service health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **View API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test task assignment**:
   ```bash
   curl -X POST http://localhost:8000/assign-task/ \
     -H "Content-Type: application/json" \
     -d '{"task_type": "test_task", "params": {"test": true}}'
   ```

## Configuration

### Environment Variables

Copy `.env.template` to `.env` and configure:

```env
# Redis Configuration
REDIS_URL=redis://redis:6379/0

# ESC Credentials (for future automation services)
ESC_USERNAME=your_username
ESC_PASSWORD=your_password

# Browser Configuration
HEADLESS=true

# File System Configuration
DOWNLOAD_PATH=/tmp/downloads

# Logging Configuration
LOG_LEVEL=INFO

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

### Service Configuration

Each service can be configured independently:
- **Orchestrator**: Port, CORS settings, task routing
- **Redis**: Memory limits, persistence, clustering
- **Celery**: Worker concurrency, task timeouts, queues

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| POST | `/assign-task/` | Assign task to workers |
| GET | `/result/{task_id}` | Get task result |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |

### Task Assignment

**POST /assign-task/**

```json
{
  "task_type": "approve_batches",
  "params": {
    "batch_ids": [1, 2, 3],
    "auto_approve": true
  }
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "assigned",
  "message": "Task 'approve_batches' successfully assigned",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Monitoring

### Service Health

- **Health Endpoint**: `/health` provides service and Redis status
- **Logs**: Structured logging with rotation in `logs/automation.log`
- **Flower**: Optional Celery monitoring at http://localhost:5555

### Docker Monitoring

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Monitor resource usage
docker stats
```

## Development

### Adding New Services

1. Create service directory with required files
2. Add service to `docker-compose.yml`
3. Update shared configuration if needed
4. Add service-specific documentation

### Code Standards

- **Python 3.10+** compatibility
- **Type hints** for all functions
- **Comprehensive logging** with structured messages
- **Error handling** with proper HTTP status codes
- **Documentation** for all public APIs

### Testing

```bash
# Run tests (when implemented)
pytest

# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis status
   docker-compose ps redis
   
   # View Redis logs
   docker-compose logs redis
   
   # Restart Redis
   docker-compose restart redis
   ```

2. **Orchestrator Service Won't Start**
   ```bash
   # Check environment variables
   cat .env
   
   # View service logs
   docker-compose logs orchestrator
   
   # Check port conflicts
   netstat -tulpn | grep 8000
   ```

3. **Task Assignment Fails**
   ```bash
   # Check Celery worker status
   docker-compose ps
   
   # View task logs
   docker-compose logs -f orchestrator
   
   # Test Redis connectivity
   redis-cli ping
   ```

### Performance Tuning

- **Redis**: Adjust memory settings and persistence
- **Celery**: Configure worker concurrency and prefetch
- **FastAPI**: Enable async endpoints and connection pooling
- **Docker**: Set appropriate resource limits

## Security Considerations

- **Environment Variables**: Never commit `.env` files
- **API Keys**: Use secure key management
- **Network**: Configure appropriate firewall rules
- **CORS**: Restrict origins in production
- **Authentication**: Implement JWT or similar (future enhancement)

## Integration with Frontend

This backend is designed to integrate seamlessly with frontend applications built in Lovable AI or other frameworks:

1. **CORS Enabled**: Ready for cross-origin requests
2. **REST API**: Standard HTTP methods and JSON responses
3. **OpenAPI Spec**: Auto-generated documentation for client generation
4. **Error Handling**: Consistent error response format

### Frontend Integration Example

```javascript
// Assign task
const response = await fetch('http://localhost:8000/assign-task/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_type: 'approve_batches',
    params: { batch_ids: [1, 2, 3] }
  })
});

const { task_id } = await response.json();

// Poll for result
const result = await fetch(`http://localhost:8000/result/${task_id}`);
const taskResult = await result.json();
```

## Roadmap

### Part B Implementation
- Worker service implementation
- ESC system integration
- Batch processing automation
- Additional task types

### Future Enhancements
- Authentication and authorization
- Rate limiting and throttling
- Metrics and monitoring (Prometheus)
- Database integration
- WebSocket support for real-time updates

## Contributing

1. Follow the established code structure
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure Docker compatibility
5. Follow semantic versioning

## License

This project is open-source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review service-specific README files
3. Check Docker and service logs
4. Ensure environment configuration is correct

---

**Part A Status**: ✅ Complete and Production Ready  
**Part B Status**: ⏳ Pending Implementation  

This backend provides a solid foundation for AI Agent automation with room for expansion and integration with additional services.
