# Frontend Service

## Description
The Frontend Service provides a web-based user interface for interacting with the AI Agent system. It allows users to trigger tasks, monitor their progress, and view results.

## Features
- Web-based UI built with FastAPI and Jinja2 templates
- Task management interface
- Real-time status monitoring
- Result display and visualization
- RESTful API endpoints

## Running the Service
```bash
cd frontend_service
pip install -r requirements.txt
python main.py
```

The service will start on `http://localhost:8080`

## API Endpoints
- `GET /` - Main UI interface
- `GET /api/status` - Service status
- `GET /health` - Health check

## Directory Structure
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JavaScript, and other static files
- `main.py` - FastAPI application entry point
