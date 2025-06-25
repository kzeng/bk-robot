"""
Centralized logging configuration for bk-robot project.
"""
from loguru import logger
import sys
import os

# Get project root directory and create logs directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "app", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Define log files
LOG_FILE = os.path.join(LOGS_DIR, "app.log")
DAILY_LOG_FILE = os.path.join(LOGS_DIR, "app.{time:YYYY-MM-DD}.log")

# Remove default handler
logger.remove()

# Add console output handler with colors
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="DEBUG",
    enqueue=True,  # Thread-safe
    backtrace=True,  # Include variables in tracebacks
    diagnose=True  # Enable exception diagnosis
)

# Add size-based rotation handler
logger.add(
    LOG_FILE,
    rotation="20 MB",  # Rotate when size reaches 20MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated files
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    enqueue=True,  # Thread-safe
    backtrace=True,  # Include variables in tracebacks
    diagnose=True,  # Enable exception diagnosis
    catch=True  # Catch exceptions within the logging system
)

# Add daily rotation handler
logger.add(
    DAILY_LOG_FILE,
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated files
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    catch=True
)

# Export configured logger
configured_logger = logger
