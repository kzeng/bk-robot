"""
Centralized logging configuration for bk-robot project.
"""

# loguru支持的日志级别如下（按严重程度从低到高）：

# 1. TRACE (level=5) - 比DEBUG更详细的跟踪信息
# 2. DEBUG (level=10) - 调试信息，开发时使用
# 3. INFO (level=20) - 常规运行信息
# 4. SUCCESS (level=25) - 成功操作信息（loguru特有）
# 5. WARNING (level=30) - 警告信息，不影响运行
# 6. ERROR (level=40) - 错误信息，影响部分功能
# 7. CRITICAL (level=50) - 严重错误，可能导致系统停止

# 当前项目配置：

# - 主要使用DEBUG和INFO级别
# - 生产环境建议使用INFO及以上级别
# - 关键错误会自动记录ERROR和CRITICAL级别

# 日志级别选择建议：

# - 开发环境：DEBUG或TRACE
# - 生产环境：INFO或WARNING
# - 关键系统：ERROR及以上

# 可通过修改logger.add()中的level参数调整日志级别。


# from loguru import logger
# import sys
# import os

# # Get project root directory and create logs directory
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# LOGS_DIR = os.path.join(PROJECT_ROOT, "app", "logs")
# os.makedirs(LOGS_DIR, exist_ok=True)

# # Define log files
# LOG_FILE = os.path.join(LOGS_DIR, "app.log")
# DAILY_LOG_FILE = os.path.join(LOGS_DIR, "app.{time:YYYY-MM-DD}.log")

# # Remove default handler
# logger.remove()

# # Add console output handler with colors
# logger.add(
#     sys.stderr, 
#     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
#     level="WARNING",
#     enqueue=True,  # Thread-safe
#     backtrace=False,  # Disable detailed tracebacks
#     diagnose=False  # Disable exception diagnosis
# )

# # Add size-based rotation handler
# logger.add(
#     LOG_FILE,
#     rotation="20 MB",  # Rotate when size reaches 20MB
#     retention="30 days",  # Keep logs for 30 days
#     compression="zip",  # Compress rotated files
#     encoding="utf-8",
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
#     level="WARNING",
#     enqueue=True,  # Thread-safe
#     backtrace=False,  # Disable detailed tracebacks
#     diagnose=False,  # Disable exception diagnosis
#     catch=True  # Catch exceptions within the logging system
# )

# # Add time-based rotation handler (daily at midnight)
# logger.add(
#     DAILY_LOG_FILE,
#     rotation="00:00",  # Rotate daily at midnight
#     retention="30 days",
#     compression="zip",
#     encoding="utf-8",
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
#     level="WARNING",
#     enqueue=True,
#     backtrace=True,
#     diagnose=True,
#     catch=True
# )

# # Add size-based rotation handler as backup
# logger.add(
#     os.path.join(LOGS_DIR, "app.size_rotated.log"),
#     rotation="200 MB",  # Rotate when reaches 200MB
#     retention="30 days",
#     compression="zip",
#     encoding="utf-8",
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
#     level="WARNING",
#     enqueue=True,
#     backtrace=True,
#     diagnose=True,
#     catch=True
# )
# configured_logger = logger



from loguru import logger
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "app", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "app.log")
CONSOLE_LOG_LEVEL = os.environ.get("BK_ROBOT_CONSOLE_LOG_LEVEL", "INFO")
FILE_LOG_LEVEL = os.environ.get("BK_ROBOT_FILE_LOG_LEVEL", "DEBUG")
LOG_ROTATION = os.environ.get("BK_ROBOT_LOG_ROTATION", "20 MB")
LOG_RETENTION = os.environ.get("BK_ROBOT_LOG_RETENTION", "30 days")
LOG_COMPRESSION = os.environ.get("BK_ROBOT_LOG_COMPRESSION", "zip")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"

logger.remove()
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level=CONSOLE_LOG_LEVEL,
    enqueue=False,
    backtrace=False,
    diagnose=False,
)
logger.add(
    LOG_FILE,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression=LOG_COMPRESSION,
    encoding="utf-8",
    format=LOG_FORMAT,
    level=FILE_LOG_LEVEL,
    enqueue=False,
    backtrace=True,
    diagnose=False,
    catch=True,
)

configured_logger = logger
