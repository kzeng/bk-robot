#!/bin/bash

# 参数检查
if [ $# -ne 2 ]; then
  echo "用法: $0 <旧提交ID> <新提交ID>"
  exit 1
fi

OLD_COMMIT=$1
NEW_COMMIT=$2
OUTPUT_DIR=./patches
TEMP_DIR=$(mktemp -d)

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取变更文件列表并复制到临时目录
git diff --name-only --diff-filter=ACMRT "$OLD_COMMIT" "$NEW_COMMIT" | while read -r file; do
  # 创建目标目录
  target_dir="$TEMP_DIR/$(dirname "$file")"
  mkdir -p "$target_dir"
  
  # 复制文件（保持原路径）
  if [ -f "$file" ]; then
    cp -v --parents "$file" "$TEMP_DIR"
  else
    echo "警告: 文件 $file 不存在，可能是重命名或删除操作" >&2
  fi
done

# 打包文件
timestamp=$(date +%Y%m%d%H%M%S)
package_name="patch_${timestamp}.tar.gz"
tar -czf "$OUTPUT_DIR/$package_name" -C "$TEMP_DIR" .

echo "========================================"
echo "补丁包已创建: $OUTPUT_DIR/$package_name"
echo "包含 $(find "$TEMP_DIR" -type f | wc -l) 个文件"
echo "临时目录: $TEMP_DIR (可手动清理)"

# 可选：自动清理临时目录
# rm -rf "$TEMP_DIR"