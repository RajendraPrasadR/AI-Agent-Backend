@echo off
REM AI Agent Backend - Windows Startup Script
REM Starts Redis, Orchestrator Service, and Worker Service locally

echo ========================================
echo AI Agent Backend - Local Startup
echo ========================================

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.template to .env and configure your settings.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.10+ and add it to your PATH.
    pause
    exit /b 1
)

REM Check if Redis is available
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not installed or not in PATH!
    echo Please install Redis or use Docker Compose instead.
    echo.
    echo To install Redis on Windows:
    echo 1. Download Redis from https://github.com/microsoftarchive/redis/releases
    echo 2. Or use Windows Subsystem for Linux (WSL)
    echo 3. Or use Docker: docker run -d -p 6379:6379 redis:7-alpine
    echo.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)

echo.
echo Starting services...
echo.

REM Start Redis in background
echo Starting Redis server...
start "Redis Server" redis-server
timeout /t 3 /nobreak >nul

REM Test Redis connection
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ERROR: Redis server failed to start or is not responding!
    pause
    exit /b 1
)
echo Redis server started successfully!

REM Start Orchestrator Service in background
echo Starting Orchestrator Service...
cd orchestrator_service
start "Orchestrator Service" python main.py
cd ..
timeout /t 5 /nobreak >nul

REM Test Orchestrator Service
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Orchestrator Service may not be ready yet.
    echo Please wait a moment and check http://localhost:8000/health
)
echo Orchestrator Service started!

REM Start Worker Service in background
echo Starting Worker Service...
cd worker_service
start "Worker Service" python worker.py
cd ..
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Service URLs:
echo - Orchestrator API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo.
echo To stop services:
echo 1. Close the Redis Server window
echo 2. Close the Orchestrator Service window
echo 3. Close the Worker Service window
echo.
echo Press any key to open the API documentation...
pause >nul

REM Open API documentation in default browser
start http://localhost:8000/docs

echo.
echo Services are running in background windows.
echo Check the individual service windows for logs.
echo.
pause
