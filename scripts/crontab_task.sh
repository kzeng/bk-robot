#!/bin/bash

# 设置必要的环境变量
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Check if task_id parameter is provided
if [ $# -eq 0 ]; then
    echo "Error: Task ID is required" >> /tmp/crontab_task.log 2>&1
    echo "Usage: $0 <task_id>" >> /tmp/crontab_task.log 2>&1
    exit 1
fi

TASK_ID="$1"
API_URL="http://127.0.0.1:5000/api/tasks/${TASK_ID}/run"

# 使用完整路径的 curl 命令
/usr/bin/curl -s -X POST "$API_URL" >> /tmp/crontab_task.log 2>&1


# Kzeng note:# This script is designed to be run as a cron job to trigger a specific task via an API
# copy this script to /home/bk/crontab_task.sh
# and make it executable
# chmod +x /home/bk/crontab_task.sh

# Add the following lines to your crontab file using `crontab -e`

#每天上午10点执行任务
# 0 10 * * * /bin/bash /home/bk/crontab_task.sh 8

#每周二 10:00执行任务
# 0 10 * * 2 /bin/bash /home/bk/crontab_task.sh 8

#每月15日 10:00执行任务
# 0 10 15 * * /bin/bash /home/bk/crontab_task.sh 8





# - **cron** 是一个守护进程，负责在后台运行并按计划执行任务。
# - **crontab** 是用户用来定义这些定时任务的配置文件，包含了任务的执行时间和具体命令。

# ### crontab 的基本格式
# 每行 crontab 条目由 6 个字段组成：
# ```
# * * * * *  命令
# | | | | |
# | | | | +--- 星期（0-6，0表示星期天）
# | | | +----- 月（1-12）
# | | +------- 日（1-31）
# | +--------- 小时（0-23）
# +----------- 分钟（0-59）
# ```
# - 每个字段可以用数字、范围（例如 `1-5`）、列表（例如 `1,3,5`）或 `*`（表示任意值）来定义。
# - 后面的“命令”是要执行的脚本或命令。

# ### 示例
# 1. 每天凌晨 2:30 执行备份脚本：
#    ```
#    30 2 * * * /bin/bash /home/user/backup.sh
#    ```
# 2. 每小时的第 0 分钟运行检查程序：
#    ```
#    0 * * * * /usr/bin/check_status
#    ```

# ### 常用命令
# - `crontab -e`：编辑当前用户的 crontab 文件。
# - `crontab -l`：查看当前用户的 crontab 内容。
# - `crontab -r`：删除当前用户的 crontab 文件。

# ### 注意事项
# - 确保命令路径是绝对路径（如 `/bin/bash`），因为 cron 的环境变量有限。
# - cron 的日志通常在 `/var/log/cron` 或 `/var/log/syslog` 中，方便排查问题。
# - 不同用户有独立的 crontab，root 用户可以管理所有用户的 crontab。

# 简单来说，**crontab 是用于自动化定时任务的工具**，广泛用于服务器维护、数据备份、日志清理等场景。