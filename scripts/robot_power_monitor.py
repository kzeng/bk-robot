# robot_power_monitor.py
# Robot Power Monitor
# 每隔一段时间（一分钟）检查一次电池电量，并在低于阈值时发出警告（播放音频）或自动充电

# 获取机器人当前全局状态 /api/robot_status
# "charge_state"为未充电状态 并且 "power_percent" 小于 25% 播放音频 alert.mp3
# "charge_state"为未充电状态 并且 "power_percent" 小于 10% 中断当前任务，自动充电 /api/robot_recharge

# pip install playsound
# sudo apt-get install mpg123 ,  # os.system("mpg123 alert.mp3")



# @bp.route('/api/robot/status')
# def robot_status():
#     """获取机器人当前状态API"""
#     robot_control = current_app.robot_control
#     status = robot_control.get_status()
    
#     results = status.get("results", {})
#     response = {
#         "move_target": results.get("move_target", ""),
#         "move_status": results.get("move_status", ""),
#         "running_status": results.get("running_status", ""),
#         "charge_state": results.get("charge_state", False),
#         "estop_state": results.get("estop_state", False),
#         "power_percent": results.get("power_percent", 0)
#     }
    
#     return jsonify(response)

# venv is python virtual environment

# Constants for power thresholds


# FOR TEST
# source /home/bk/BOKU-SERVICE-HOME/bk-robot/venv/bin/activate
# python /home/bk/BOKU-SERVICE-HOME/bk-robot/scripts/robot_power_monitor.py

######################################################################################

# 创建 systemd 服务文件
# 创建一个服务文件，例如 /etc/systemd/system/robot_power_monitor.service：
# sudo nano /etc/systemd/system/robot_power_monitor.service



# 

######################################################################################
# [Unit]
# Description=Robot Power Monitor Service
# After=network.target

# [Service]
# Type=simple
# User=bk
# WorkingDirectory=/home/bk/BOKU-SERVICE-HOME/bk-robot/scripts
# ExecStart=/home/bk/BOKU-SERVICE-HOME/bk-robot/venv/bin/python /home/bk/BOKU-SERVICE-HOME/bk-robot/scripts/robot_power_monitor.py
# Restart=always

# [Install]
# WantedBy=multi-user.target

#####################################################################################
# User=your_username：替换为运行脚本的用户名。
# # WorkingDirectory=/path/to/robot_power_monitor_directory：替换为脚本所在目录。
# # ExecStart=/path/to/venv/bin/python /path/to/robot_power_monitor.py：替换为虚拟环境的 Python 路径和脚本路径。
# # 3. 重新加载 systemd 配置
# # 运行以下命令以重新加载 systemd 配置：
# # sudo systemctl daemon-reload
# # 4. 启动服务并设置为开机自启动
# # 启动服务：
# # sudo systemctl start robot_power_monitor.service
# # 设置为开机自启动：
# # sudo systemctl enable robot_power_monitor.service
# # 5. 检查服务状态
# # 检查服务是否正常运行：
# # sudo systemctl status robot_power_monitor.service
# # 6. 日志查看
# # 如果需要查看脚本的运行日志，可以使用以下命令：
# # journalctl -u robot_power_monitor.service -f
# # 注意事项
# # 确保脚本路径和虚拟环境路径正确。
# # 如果脚本需要访问特定资源（如音频设备），确保用户有相应权限。
# # 如果脚本依赖网络，请确保 After=network.target 保证网络服务已启动。
# # 完成以上步骤后，脚本将在系统启动时自动运行。

# 安装依赖
# pip install pydub

# from pydub import AudioSegment
# from pydub.playback import play
# song = AudioSegment.from_mp3("alert2.mp3")
# play(song)


# pip install python-vlc
import vlc
# player = vlc.MediaPlayer("sound.mp3")
# player.play()
# 等待播放完成
# import time
# time.sleep(10)  # 根据音频长度调整

import time
import requests
import os


# from pydub import AudioSegment
# from pydub.playback import play


P1 = 20
P2 = 30
CHECK_INTERVAL = 60  # Check every 60 seconds

def get_robot_status():
    """Fetch the robot's current status from the API."""
    response = requests.get("http://127.0.0.1:5000/api/robot/status")
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch robot status.")
        return None

def play_audio_alert(file_name):
    """Play an audio alert when battery is low."""
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, file_name)
    print(full_path)  
    for i in range(3):    
        player = vlc.MediaPlayer(full_path)
        player.play()
        time.sleep(8)


def trigger_recharge():
    """Trigger the robot to start recharging."""
    response = requests.post("http://127.0.0.1:5000/api/robot/recharge")
    if response.status_code == 200:
        print("Recharge triggered successfully.")
    else:
        print("Failed to trigger recharge.")

def terminate_current_task():
    """Terminate the robot's current task."""
    response = requests.post("http://127.0.0.1:5000/api/move/cancel")
    if response.status_code == 200:
        print("Current task terminated successfully.")
    else:
        print("Failed to terminate the current task.")

def monitor_power():
    """Monitor the robot's power level periodically."""

    while True:
        status = get_robot_status()
        print("Current robot raw status:", status)
      
        if status:
            charge_state =  status.get("charge_state", True)  # Convert to 'not charging' logic
            power_percent = status.get("power_percent", 100)

            print(('-------------------------------------'))
            print("Checking power level...")
            print("Charge state:",  charge_state)
            print("Power percent:", power_percent)
            print(('-------------------------------------'))


            if not charge_state:  # If not charging
                if power_percent < P1:
                    print(f"Power below {P1}%. Terminating current task.")
                    terminate_current_task()  # Terminate the current task

                    print(f"Power below {P1}%. Playing alert.")
                    play_audio_alert("alert2.mp3")
                    time.sleep(1)

                    print(f"Power below {P1}%. Triggering recharge...")
                    trigger_recharge()
                elif power_percent < P2:
                    print(f"Power below {P2}%. Playing alert.")
                    play_audio_alert("alert1.mp3")
            else:
                # Reset the flag if the robot is charging
                print("Robot is charging status.")

        time.sleep(CHECK_INTERVAL)  # Wait for the check interval before the next check


if __name__ == "__main__":
    monitor_power()

