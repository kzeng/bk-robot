#!/bin/bash

# 获取脚本所在目录，确保无论从哪里执行都能正确定位 logs 目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/../app/logs"

# 删除 logs 目录下所有 .log 日志文件
find "$LOGS_DIR" -type f -name "*.log" -delete

# 删除 logs 目录下所有 .zip 日志压缩包
find "$LOGS_DIR" -type f -name "*.zip" -delete

echo "所有 .log 日志文件和 .zip 日志压缩包已删除。"