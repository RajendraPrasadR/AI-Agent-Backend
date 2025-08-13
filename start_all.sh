#!/bin/bash
# AI Agent Backend - Linux/macOS Startup Script
# Starts Redis, Orchestrator Service, and Worker Service locally

set -e  # Exit on any error

echo "========================================"
echo "AI Agent Backend - Local Startup"
echo "========================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.template to .env and configure your settings."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH!"
    echo "Please install Python 3.10+ and ensure it's in your PATH."
    exit 1
fi

# Check if Redis is available
if ! command -v redis-server &> /dev/null; then
    echo "WARNING: Redis is not installed or not in PATH!"
    echo "Please install Redis or use Docker Compose instead."
    echo ""
    echo "To install Redis:"
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  CentOS/RHEL: sudo yum install redis"
    echo "  macOS: brew install redis"
    echo "  Or use Docker: docker run -d -p 6379:6379 redis:7-alpine"
    echo ""
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Shutting down services..."
    
    # Kill background processes
    if [ ! -z "$REDIS_PID" ]; then
        kill $REDIS_PID 2>/dev/null || true
        echo "Redis server stopped"
    fi
    
    if [ ! -z "$ORCHESTRATOR_PID" ]; then
        kill $ORCHESTRATOR_PID 2>/dev/null || true
        echo "Orchestrator service stopped"
    fi
    
    if [ ! -z "$WORKER_PID" ]; then
        kill $WORKER_PID 2>/dev/null || true
        echo "Worker service stopped"
    fi
    
    echo "All services stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies!"
    exit 1
fi

echo ""
echo "Starting services..."
echo ""

# Start Redis in background
echo "Starting Redis server..."
redis-server --daemonize yes --port 6379
sleep 2

# Test Redis connection
if ! redis-cli ping > /dev/null 2>&1; then
    echo "ERROR: Redis server failed to start or is not responding!"
    exit 1
fi
echo "Redis server started successfully!"

# Get Redis PID for cleanup
REDIS_PID=$(pgrep redis-server)

# Start Orchestrator Service in background
echo "Starting Orchestrator Service..."
cd orchestrator_service
python3 main.py &
ORCHESTRATOR_PID=$!
cd ..
sleep 5

# Test Orchestrator Service
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "WARNING: Orchestrator Service may not be ready yet."
    echo "Please wait a moment and check http://localhost:8000/health"
else
    echo "Orchestrator Service started successfully!"
fi

# Start Worker Service in background
echo "Starting Worker Service..."
cd worker_service
python3 worker.py &
WORKER_PID=$!
cd ..
sleep 3

echo ""
echo "========================================"
echo "All services started successfully!"
echo "========================================"
echo ""
echo "Service URLs:"
echo "- Orchestrator API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
echo ""
echo "Service PIDs:"
echo "- Redis: $REDIS_PID"
echo "- Orchestrator: $ORCHESTRATOR_PID"
echo "- Worker: $WORKER_PID"
echo ""
echo "To stop all services, press Ctrl+C"
echo ""

# Keep script running and wait for user interrupt
echo "Services are running. Press Ctrl+C to stop all services..."
while true; do
    sleep 1
    
    # Check if services are still running
    if ! kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
        echo "WARNING: Orchestrator service has stopped unexpectedly!"
    fi
    
    if ! kill -0 $WORKER_PID 2>/dev/null; then
        echo "WARNING: Worker service has stopped unexpectedly!"
    fi
    
    if ! kill -0 $REDIS_PID 2>/dev/null; then
        echo "WARNING: Redis server has stopped unexpectedly!"
    fi
done
