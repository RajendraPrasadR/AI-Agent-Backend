"""
Shared Configuration Module
Loads environment variables and provides configuration constants for all services.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from .env.template as fallback
    template_path = Path(__file__).parent.parent / ".env.template"
    if template_path.exists():
        load_dotenv(template_path)

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# ESC Credentials (for future automation services)
ESC_USERNAME = os.getenv("ESC_USERNAME", "")
ESC_PASSWORD = os.getenv("ESC_PASSWORD", "")

# Browser Configuration
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "30"))

# File System Configuration
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "/tmp/downloads")

# API Security Configuration
API_KEY = os.getenv("API_KEY", "your_secret_key")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# FastAPI Configuration
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

# Service Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "ai-agent")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")

# Database Configuration (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# External API Configuration (for future integrations)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Monitoring Configuration
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))

def get_config_summary() -> dict:
    """
    Get a summary of current configuration (excluding sensitive data).
    
    Returns:
        Dictionary with configuration summary
    """
    return {
        "redis_url": REDIS_URL,
        "log_level": LOG_LEVEL,
        "fastapi_host": FASTAPI_HOST,
        "fastapi_port": FASTAPI_PORT,
        "headless": HEADLESS,
        "download_path": DOWNLOAD_PATH,
        "service_name": SERVICE_NAME,
        "service_version": SERVICE_VERSION,
        "enable_metrics": ENABLE_METRICS,
        "has_esc_credentials": bool(ESC_USERNAME and ESC_PASSWORD),
        "has_openai_key": bool(OPENAI_API_KEY),
        "has_anthropic_key": bool(ANTHROPIC_API_KEY),
    }

def validate_config() -> list:
    """
    Validate configuration and return list of issues.
    
    Returns:
        List of configuration issues (empty if all valid)
    """
    issues = []
    
    if not REDIS_URL:
        issues.append("REDIS_URL is not configured")
    
    if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        issues.append(f"Invalid LOG_LEVEL: {LOG_LEVEL}")
    
    if FASTAPI_PORT < 1 or FASTAPI_PORT > 65535:
        issues.append(f"Invalid FASTAPI_PORT: {FASTAPI_PORT}")
    
    if not os.path.exists(os.path.dirname(DOWNLOAD_PATH)):
        issues.append(f"Download path directory does not exist: {os.path.dirname(DOWNLOAD_PATH)}")
    
    return issues
