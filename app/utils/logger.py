"""
Centralized logging configuration for bk-robot project.
"""
from loguru import logger
import sys
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, "bk-robot.log")

# 移除默认的处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 添加文件输出
logger.add(
    LOG_FILE,
    rotation="20 MB",  # 日志文件达到20MB时轮转
    retention="30 days",  # 保留30天的日志
    compression="zip",  # 压缩旧的日志文件
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO"
)

# 导出配置好的logger
configured_logger = logger
