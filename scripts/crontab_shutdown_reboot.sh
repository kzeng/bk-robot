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

# Send shutdown command with specified delay
/usr/bin/curl -s -X POST http://127.0.0.1:5000/api/robot/cmd  -H "Content-Type: application/json" -d '{"cmd": "/api/shutdown", "params": "reboot=true&delay=720"}'


