"""
Shared constants for AI Agent services
"""

# Service Names
ORCHESTRATOR_SERVICE = "orchestrator_service"
WORKER_SERVICE = "worker_service"
AUTOMATION_SERVICE = "automation_service"
FRONTEND_SERVICE = "frontend_service"

# Service Ports
ORCHESTRATOR_PORT = 8000
FRONTEND_PORT = 8080

# Task Types
TASK_APPROVE_BATCHES = "approve_batches"
TASK_GENERATE_CERTIFICATES = "generate_certificates"
TASK_DOWNLOAD_REPORTS = "download_reports"
TASK_TEST = "test_task"

# Task Status
STATUS_PENDING = "PENDING"
STATUS_STARTED = "STARTED"
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILURE = "FAILURE"
STATUS_RETRY = "RETRY"

# Redis Configuration
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
REDIS_TASK_QUEUE = "ai_agent_tasks"
REDIS_RESULT_BACKEND = "ai_agent_results"

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"

# File Paths
LOGS_DIR = "logs"
SCREENSHOTS_DIR = "screenshots"
DOWNLOADS_DIR = "downloads"

# Automation Configuration
DEFAULT_SELENIUM_TIMEOUT = 30
DEFAULT_PAGE_LOAD_TIMEOUT = 30
SCREENSHOT_ON_ERROR = True

# API Response Messages
MSG_TASK_ASSIGNED = "Task assigned successfully"
MSG_TASK_COMPLETED = "Task completed successfully"
MSG_TASK_FAILED = "Task execution failed"
MSG_SERVICE_HEALTHY = "Service is healthy"
MSG_UNKNOWN_TASK = "Unknown task type"
