#!/bin/bash

#########################################################################
# 脚本功能：定时关机重启
# 拷贝该脚本到 /home/bk/
# chmod +x crontab_shutdown_reboot.sh
#
# cron job with `crontab -e`
# 每日19:00执行任务 720分钟即12小时后自动开机 即早上7点开机
# 0 19 * * * /bin/bash /home/bk/crontab_shutdown_reboot.sh 720
#
########################################################################


# Set necessary environment variables
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Check if delay parameter is provided and is numeric
if [ $# -eq 0 ]; then
    echo "Error: Delay parameter is required" >&2
    echo "Usage: $0 <delay_in_minutes>" >&2
    exit 1
fi

# Validate numeric delay
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Error: Delay must be a positive integer (minutes)" >&2
    exit 1
fi

DELAY="$1"

# Send shutdown command with specified delay
if ! /usr/bin/curl -X POST http://127.0.0.1:5000/api/robot/cmd \
  -d '{"cmd": "/api/shutdown", "params": "reboot=true&delay='"$DELAY"'"}' >/dev/null 2>&1; then
    echo "Error: Failed to send reboot command" >&2
    exit 1
fi
