from flask import render_template, jsonify, request, Blueprint, current_app, redirect, url_for, send_from_directory, flash, session, flash, session
import hashlib
from functools import wraps
import json
import shutil
from app.models import Task, TaskLog, MarkerConfig
from app import db
from datetime import datetime, timezone, timedelta
import asyncio
import os
import time
from threading import Thread
import ftplib
from ftplib import FTP
import logging
import serial
import platform
import psutil
import subprocess
from .lift_control import Lift
from dotenv import load_dotenv, set_key
from loguru import logger
import os
from flask import stream_with_context, Response
import cv2

TASK_STATUS_READY        = 0
TASK_STATUS_INPROGRESS   = 1
TASK_STATUS_COMPLETED    = 2
TASK_STATUS_PARTIAL      = 3
TASK_STATUS_FAILED       = 4


def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['NEED_AUTH']:
            return f(*args, **kwargs)
        if 'authenticated' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

bp = Blueprint('main', __name__)

robot_all_apis_options = [
        {
            "title": "1.机器人移动功能",
            "url": "#",
            "cmd": "/api/move"
        },
        {
            "title": "2.移动取消功能", 
            "url": "#",
            "cmd": "/api/move/cancel"
        },
        {
            "title": "3.获取机器人当前全局状态",
            "url": "#",
            "cmd": "/api/robot_status"
        },
        {
            "title": "4.获取机器人信息接口",
            "url": "#",
            "cmd": "/api/robot_info"
        },
        {
            "title": "5.2获取marker点位列表",
            "url": "#",
            "cmd": "/api/markers/query_list"
        },
        # {
        #     "title": "6.机器人直接控制指令",
        #     "url": "#",
        #     "cmd": "/api/joy_control"
        # },
        # {
        #     "title": "7.机器人急停控制指令",
        #     "url": "#",
        #     "cmd": "/api/estop"
        # },
        {
            "title": "8.校正机器人当前位置",
            "url": "#",
            "cmd": "/api/position_adjust"
        },
        {
            "title": "9.请求机器人实时数据",
            "url": "#",
            "cmd": "/api/request_data"
        },
        # {
        #     "title": "11.设置参数",
        #     "url": "#",
        #     "cmd": "/api/set_params"
        # },
        # {
        #     "title": "12.获取参数",
        #     "url": "#",
        #     "cmd": "/api/get_params"
        # },
        {
            "title": "14.获取地图列表",
            "url": "#",
            "cmd": "/api/map/list"
        },
        {
            "title": "14.3获取当前地图",
            "url": "#",
            "cmd": "/api/map/get_current_map"
        },
        {
            "title": "15.关机重启接口",
            "url": "#",
            "cmd": "/api/shutdown"
        },
        # {
        #     "title": "17.设置灯带接口",
        #     "url": "#",
        #     "cmd": "/api/LED/set_luminance"
        # },
        # {
        #     "title": "18.自诊断接口",
        #     "url": "#",
        #     "cmd": "/api/diagnosis/get_result"
        # },
        # {
        #     "title": "19.获取电源状态接口",
        #     "url": "#",
        #     "cmd": "/api/get_power_status"
        # },
        {
            "title": "20.获取机器人全局路径接口",
            "url": "#",
            "cmd": "/api/get_planned_path"
        },
        # {
        #     "title": "21.获取电梯状态接口",
        #     "url": "#",
        #     "cmd": "/api/lift_status"
        # },
        # {
        #     "title": "22.获取两点间路径接口",
        #     "url": "#",
        #     "cmd": "/api/make_plan"
        # },
        {
            "title": "23.获取机器人当前位置接口",
            "url": "#",
            "cmd": "/api/get_current_location"
        }
    ]

@bp.route('/')
@login_required
def index():
    """调试界面主页"""
    return render_template('index.html', robot_all_apis_options=robot_all_apis_options)


@bp.route('/docs/<path:filename>')
def serve_docs(filename):
    return send_from_directory('static/docs', filename)


@bp.route('/tasks')
@login_required
def tasks_page():
    """盘点任务管理页面"""
    return render_template('task.html')

@bp.route('/task-logs')
@login_required
def task_logs_page():
    """任务日志列表页面"""
    return render_template('task-logs.html')


# common API for robot control, all commands can be sent through this endpoint
# api_request should be in the format of "cmd?params"
# returns info insert into opt-info container
@bp.route('/api/robot/cmd', methods=['POST'])
def robot_cmd():
    """发送机器人控制命令API"""
    data = request.get_json()
    logger.info(f"Received operation command: {data}")

    try:
        api_request = f"{data['cmd']}?{data['params']}"
        robot_control = current_app.robot_control
        result = robot_control.send_command(api_request) or {}
        
        # Operation results go to opt-info container
        return jsonify({
            "container": "opt-info",  # 指令操作结果容器
            "timestamp": time.time(),
            "command": data['cmd'],
            "status": result.get("status", "ERROR"),
            "error_message": result.get("error_message", "Unknown error"),
            "results": result.get("results", None)
        })
    except Exception as e:
        logger.error(f"Error in robot_cmd: {str(e)}")
        return jsonify({
            "container": "opt-info",
            "timestamp": time.time(),
            "command": data.get('cmd', 'unknown'),
            "status": "ERROR",
            "error_message": str(e),
            "results": None
        }), 500

@bp.route('/api/firefox/restart', methods=['POST'])
def restart_firefox():
    """重启Firefox进入全屏模式"""
    try:
        # 杀死现有Firefox进程
        subprocess.run(['taskkill', '/f', '/im', 'firefox.exe'], check=True)
        # 启动Firefox全屏模式
        subprocess.Popen(['firefox', '-kiosk', 'http://localhost:5000'])
        return jsonify({'status': 'OK', 'message': 'Firefox已重启进入全屏模式'})
    except Exception as e:
        logger.error(f"重启Firefox失败: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

@bp.route('/api/firefox/exit', methods=['POST'])
def exit_firefox():
    """退出Firefox全屏模式"""
    try:
        # 杀死现有Firefox进程
        subprocess.run(['taskkill', '/f', '/im', 'firefox.exe'], check=True)
        # 启动普通Firefox窗口
        subprocess.Popen(['firefox', 'http://localhost:5000'])
        return jsonify({'status': 'OK', 'message': '已退出Firefox全屏模式'})
    except Exception as e:
        logger.error(f"退出Firefox全屏模式失败: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500
