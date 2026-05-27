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
from threading import Thread, Lock
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
import re

TASK_STATUS_READY        = 0
TASK_STATUS_INPROGRESS   = 1
TASK_STATUS_COMPLETED    = 2
TASK_STATUS_PARTIAL      = 3
TASK_STATUS_FAILED       = 4

# Task execution lock to prevent concurrent task execution
task_exec_lock = Lock()

MOVE_STALL_TIMEOUT_SECONDS = 90
MOVE_STALL_RETRY_DELTA = 3
MOVE_POSE_EPSILON = 0.02
MOVE_CANCEL_SETTLE_TIMEOUT_SECONDS = 15


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
            "title": "14.2设置当前地图",
            "url": "#",
            "cmd": "/api/map/set_current_map"
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
        {
            "title": "17.1 设置灯带亮度",
            "url": "#",
            "cmd": "/api/LED/set_luminance"
        },
        {
            "title": "17.2 设置灯带颜色",
            "url": "#",
            "cmd": "/api/LED/set_color"
        },
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



@bp.route('/api/robot/poll_status')
def poll_robot_status():
    """轮询机器人状态API"""
    robot_control = current_app.robot_control
    status = robot_control.get_status()
    
    # Polled status always goes to status-info container
    response = {
        "container": "status-info",  # 状态信息容器
        "timestamp": time.time(),
        "type": status.get("type", "response"),
        "command": status.get("command", "/api/robot_status"),
        "status": status.get("status", "ERROR"),
        "error_message": status.get("error_message", ""),
        "results": status.get("results", None)
    }
    
    return jsonify(response)



@bp.route('/api/obs/start_recording', methods=['POST'])
def start_recording():
    """开始录制API"""
    camera_control = current_app.camera_control
    
    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            connect_result = camera_control.connect()
            if connect_result["status"] != "OK":
                return jsonify(connect_result), 500
        
        # Start recording and return result
        result = camera_control.start_recording()
        if result["status"] != "OK":
            return jsonify(result), 500
            
        logger.info("Recording started successfully.")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return jsonify({
            "status": "ERROR",
            "message": f"Failed to start recording: {str(e)}"
        }), 500

@bp.route('/api/obs/stop_recording', methods=['POST'])
def stop_recording():
    """停止录制API"""
    camera_control = current_app.camera_control

    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            connect_result = camera_control.connect()
            if connect_result["status"] != "OK":
                return jsonify(connect_result), 500
        
        # Stop recording and get result
        result = camera_control.stop_recording()
        logger.info(f"Stop recording result: {result}")
        
        if result["status"] != "OK":
            return jsonify(result), 500

        # Return success response
        file_path = ""
        if isinstance(result.get("file_paths"), list) and result["file_paths"]:
            # For OpenCV control that returns multiple file paths
            file_path = result["file_paths"][0]
        else:
            # For OBS control that returns a single file path
            file_path = result.get("file_path", "")
            
        return jsonify({
            "status": "OK",
            "message": "Recording stopped successfully",
            "file_path": file_path
        })

    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return jsonify({
            "status": "ERROR",
            "message": f"Error stopping recording: {str(e)}"
        }), 500



@bp.route('/api/obs/screenshot', methods=['POST'])
def take_screenshot():
    """拍摄截图API
    
    Args:
        position_info (str, optional): 坐标点的别名(marker name)，用于在文件名中标识拍摄位置。默认为空。
    """
    # 检查内容类型
    if request.is_json:
        data = request.get_json()
        position_info = data.get('position_info', '') if data else ''
    else:
        position_info = ''
    
    timestamp = str(int(time.time()))

    camera_control = current_app.camera_control
    
    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            result = camera_control.connect()
            if result["status"] != "OK":
                return jsonify(result), 500
                
        # Take screenshots
        result = camera_control.take_photo_all_cameras(position_info=position_info, timestamp=timestamp)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return jsonify({
            "status": "ERROR",
            "message": f"Failed to take screenshot: {str(e)}"
        }), 500




@bp.route('/api/tasks', methods=['GET'])
@bp.route('/tasks', methods=['GET'])
def list_tasks():
    """获取所有盘点任务"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        
        if page < 1 or size < 1:
            return jsonify({
                'status': 'ERROR',
                'message': 'Invalid page or size parameters'
            }), 400

        # Get paginated tasks
        tasks = Task.query.order_by(
            Task.task_id.desc()
        ).paginate(page=page, per_page=size, error_out=False)

        return jsonify({
            'status': 'OK',
            'data': [{
                'task_id': task.task_id,
                'marker': task.marker,
                'action': task.action,
                'create_at': task.create_at.strftime("%Y-%m-%d %H:%M:%S") if task.create_at else None,
                'update_at': task.update_at.strftime("%Y-%m-%d %H:%M:%S") if task.update_at else None,
                'description': task.description,
                'lift': task.lift
            } for task in tasks.items],
            'pagination': {
                'page': page,
                'size': size,
                'total': tasks.total,
                'pages': tasks.pages
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get tasks: {str(e)}'
        }), 500



@bp.route('/api/tasks', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
def create_task():
    """创建新盘点任务"""
    try:
        # Log request headers and raw data
        # logger.info(f"Request headers: {dict(request.headers)}")
        # logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Raw request data: {request.data}")
        
        try:
            data = request.get_json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            return jsonify({'status': 'ERROR', 'message': 'Invalid JSON format'}), 400
            
        logger.info(f"Creating new task with data: {data}")
        
        task = Task(
            marker=data.get('marker', ''),
            action=data.get('action', 0),
            description=data.get('description', ''),
            lift=data.get('lift', 'L2'),
            create_at=datetime.now(timezone(timedelta(hours=8)))  # Use Shanghai timezone
        )

        db.session.add(task)
        db.session.commit()
        
        logger.info(f"Successfully created task ID: {task.task_id}")
        return jsonify({
            'status': 'OK', 
            'task_id': task.task_id,
            'message': 'Task created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to create task: {str(e)}'
        }), 500

@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取单个盘点任务，增加返回最新执行状态status"""

    # Refresh session to ensure we get latest data
    db.session.expire_all()
    
    task = Task.query.get_or_404(task_id)
    # 获取最新的任务日志（按 end_time 和 start_time 排序，确保拿到最新的）
    task_log = TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.end_time.desc(), TaskLog.start_time.desc()).first()
    status = task_log.status if task_log else None
    return jsonify({
        'task_id': task.task_id,
        'marker': task.marker,
        'action': task.action,
        'create_at': task.create_at.strftime("%Y-%m-%d %H:%M:%S") if task.create_at else None,
        'update_at': task.update_at.strftime("%Y-%m-%d %H:%M:%S") if task.update_at else None,
        'description': task.description,
        'lift': task.lift,
        'status': status
    })

@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新盘点任务"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.marker = data.get('marker', task.marker)
    task.action = data.get('action', task.action)
    task.description = data.get('description', task.description)
    task.lift = data.get('lift', task.lift)
    task.update_at = datetime.now()
    
    db.session.commit()
    return jsonify({'status': 'OK'})

@bp.route('/api/tasks/<int:task_id>/run', methods=['POST'])
def run_task(task_id):
    """启动盘点任务执行
        
    Args:
        task_id (int): 要执行的任务ID
            
    Returns:
        JSON响应包含:
        - status: 'OK' 或 'ERROR'
        - message: 操作结果描述
        - task_log_id: 任务日志ID用于跟踪执行过程
    """
    task = Task.query.get_or_404(task_id)

    # 检查是否有其他任务正在执行
    if not task_exec_lock.acquire(blocking=False):
        logger.warning(f"Task {task_id} rejected: another task is already running")
        return jsonify({
            'status': 'ERROR',
            'message': 'Another task is already running, please wait for it to complete'
        })

    # 创建任务执行日志
    current_time = datetime.now()
    task_log = TaskLog(
        task_id=task_id,
        marker=task.marker,
        action=task.action,
        start_time=current_time,
        end_time=current_time,  # 初始化 end_time 为开始时间，后续会在任务完成时更新
        status=1,  # 1 = in progress
        file_count=0,
        file_paths='[]'
    )
    db.session.add(task_log)
    db.session.commit()
    
    # 启动后台执行线程
    thread = Thread(target=async_run_task, args=(current_app._get_current_object(), task.task_id))
    thread.start()
    
    return jsonify({
        'status': 'OK',
        'message': 'Task execution started',
        'task_log_id': task_log.log_id  # 返回正确的task_log_id
    })

def _pose_changed_enough(previous_pose, current_pose, epsilon=MOVE_POSE_EPSILON):
    if not previous_pose or not current_pose:
        return True

    for axis in ("x", "y"):
        try:
            previous_value = float(previous_pose.get(axis, 0))
            current_value = float(current_pose.get(axis, 0))
        except (TypeError, ValueError):
            return True
        if abs(current_value - previous_value) >= epsilon:
            return True

    return False


def _is_robot_busy_response(response):
    if not response:
        return False

    status = str(response.get('status', '')).upper()
    error_message = str(response.get('error_message') or response.get('message') or '')
    return (
        status == 'BUSY_NOW'
        or 'Last move task is running' in error_message
        or 'Robot is busy' in error_message
        or 'busy' in error_message.lower()
    )


def cancel_robot_move_for_retry(robot_control, target_marker, reason):
    logger.warning(f"Cancelling active robot move for {target_marker}: {reason}")

    try:
        cancel_result = robot_control.cancel_move()
    except Exception as exc:
        logger.error(f"Failed to send move cancel for {target_marker}: {exc}")
        return False

    if not cancel_result or cancel_result.get('status') != 'OK':
        logger.error(f"Move cancel failed for {target_marker}: {cancel_result}")
        return False

    deadline = time.time() + MOVE_CANCEL_SETTLE_TIMEOUT_SECONDS
    while time.time() < deadline:
        try:
            robot_status = robot_control.send_command("/api/robot_status")
        except Exception as exc:
            logger.warning(f"Failed to verify move cancel for {target_marker}: {exc}")
            time.sleep(1)
            continue

        if not robot_status or robot_status.get('status') != 'OK':
            logger.warning(f"Robot status unavailable after move cancel for {target_marker}: {robot_status}")
            time.sleep(1)
            continue

        results = robot_status.get('results', {})
        move_target = results.get('move_target')
        move_status = results.get('move_status')
        running_status = results.get('running_status')

        if move_status in ['canceled', 'failed', 'succeeded', None, ''] or running_status == 'idle':
            logger.info(
                f"Move cancel settled for {target_marker}: "
                f"move_target={move_target}, move_status={move_status}, running_status={running_status}"
            )
            return True

        logger.info(
            f"Waiting for move cancel to settle for {target_marker}: "
            f"move_status={move_status}, running_status={running_status}"
        )
        time.sleep(0.5)

    logger.warning(f"Move cancel did not settle for {target_marker} within {MOVE_CANCEL_SETTLE_TIMEOUT_SECONDS}s")
    return False


def wait_for_robot_move(robot_control, target_marker, max_duration=300, max_consecutive_failures=10):
    """轮询机器人状态，等待移动到目标点位完成。

    改进点：
    - 使用绝对超时时间（默认5分钟），而不是对连续检查计数
    - 跟踪连续失败次数，用于检测网络/通信故障
    - "移动中"状态不消耗超时计数器

    Args:
        robot_control: 机器人控制实例
        target_marker: 目标点位
        max_duration: 最大等待时间（秒），默认300秒（5分钟）
        max_consecutive_failures: 最大连续状态检查失败次数，默认10次

    Returns:
        True 表示移动成功，False 表示超时

    Raises:
        Exception: 当机器人报告移动失败或取消时抛出
    """
    start_time = time.time()
    consecutive_failures = 0
    last_progress_time = start_time
    last_progress_pose = None
    retry_count_at_last_progress = None

    while True:
        # 绝对超时检查——防止无限循环
        elapsed = time.time() - start_time
        if elapsed > max_duration:
            logger.warning(
                f"Movement to {target_marker} timed out after {elapsed:.0f}s "
                f"(exceeded {max_duration}s limit)"
            )
            return False

        robot_status = robot_control.send_command("/api/robot_status")

        if not robot_status or robot_status.get('status') != 'OK':
            consecutive_failures += 1
            logger.warning(
                f"Failed to get OK robot status for {target_marker}: {robot_status} "
                f"(consecutive failure {consecutive_failures}/{max_consecutive_failures})"
            )
            if consecutive_failures >= max_consecutive_failures:
                logger.error(
                    f"Too many consecutive status check failures ({consecutive_failures}), "
                    f"aborting move to {target_marker}"
                )
                return False
            time.sleep(1)
            continue

        consecutive_failures = 0  # 成功获取状态，重置失败计数
        logger.debug(f"Robot status: {robot_status}")

        results = robot_status.get('results', {})
        actual_marker = results.get('move_target')
        move_status = results.get('move_status')
        current_pose = results.get('current_pose')
        move_retry_times = results.get('move_retry_times')

        if move_status == 'succeeded' and actual_marker == target_marker:
            logger.info(f"Robot successfully reached marker {target_marker}")
            return True
        elif move_status in ['failed', 'canceled']:
            raise Exception(f"Movement {move_status} at {target_marker}")

        if actual_marker == target_marker and move_status in ['running', 'moving']:
            now = time.time()
            if _pose_changed_enough(last_progress_pose, current_pose):
                last_progress_pose = current_pose
                last_progress_time = now
                retry_count_at_last_progress = move_retry_times
            else:
                stalled_for = now - last_progress_time
                retry_delta = 0
                if isinstance(move_retry_times, int) and isinstance(retry_count_at_last_progress, int):
                    retry_delta = move_retry_times - retry_count_at_last_progress

                if stalled_for >= MOVE_STALL_TIMEOUT_SECONDS and retry_delta >= MOVE_STALL_RETRY_DELTA:
                    logger.warning(
                        f"Movement to {target_marker} appears stuck: "
                        f"pose={current_pose}, stalled_for={stalled_for:.0f}s, "
                        f"move_retry_times={move_retry_times}, retry_delta={retry_delta}"
                    )
                    return False
        # 其他状态（如 'running'/'moving'）表示仍在移动中，继续轮询

        time.sleep(0.5)  # 轮询间隔，防止紧循环


def async_run_task(app, task_id):
    """在后台线程中执行任务"""
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            try:
                task_exec_lock.release()
                logger.info("Task execution lock released because task was not found")
            except Exception:
                pass
            return
        
        timestamp = str(int(time.time()))
        marker_list = task.marker.split(',') if task.marker else []
        marker_list = [marker.strip() for marker in marker_list if marker.strip()]

        logger.info(f"Running task {task_id} with SHORT markers: {marker_list}")

        # 替换 marker_list 中的简写点位mid_short（如 M1, M2）为实际全称点位mid（如： 01020301041，01020301042），CD 保持不变
        if marker_list:
            # 查询所有 marker_config，构建简写到全称的映射
            marker_map = {c.mid_short: c.mid for c in MarkerConfig.query.all()}
            # 替换 marker_list
            marker_list = [
                marker_map.get(m, m) if m != 'CD' else m
                for m in marker_list
            ]
        # 处理 CD 的位置
        #check CD in marker_list， make sure CD is always last
        if 'CD' in marker_list:
            marker_list.remove('CD')
            marker_list.append('CD')
        else:
            marker_list.append('CD')    


        logger.info(f"Final marker list for task {task_id}: {marker_list}")

        if not marker_list:
            # 获取最新的任务日志并更新状态
            task_log = TaskLog.query.filter_by(task_id=task_id)\
                                  .order_by(TaskLog.start_time.desc())\
                                  .first()
            if task_log:
                task_log.status = TASK_STATUS_FAILED  # 任务失败
                task_log.end_time = datetime.now()
                db.session.commit()
            return
            
    
        status = TASK_STATUS_INPROGRESS  # 1 = in progress
        file_paths = []
        task_log = TaskLog.query.filter_by(task_id=task_id)\
                               .order_by(TaskLog.start_time.desc())\
                               .first()
        
        try:
            lift_was_raised = False  # Track whether lift was raised for safe lowering

            # move lift to per-task configured height before starting the task
            if app.lift:
                logger.info(f"Moving lift to position for task lift={task.lift} ...")
                if not move_lift_to_configured_height(task.lift):
                    raise Exception("Failed to move lift to configured height")
                time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))  # wait for lift to reach position
                lift_was_raised = True  # Mark lift as raised
            else:
                logger.error("Lift control not initialized, please check")
                raise Exception("Lift control not initialized, please check")


            if task.action == 0:  # 拍照
                logger.info("Starting movement through markers for photo task ......")
                current_marker_index = 0
                while current_marker_index < len(marker_list):
                    target_marker = marker_list[current_marker_index]
                    logger.info(f"Moving to target marker: {target_marker} (sequence {current_marker_index+1}/{len(marker_list)})")

                    logger.info(f"Want to move target {target_marker}")
                    if target_marker == "CD":
                        logger.info("Next marker is CD, moving lift to position one...")
                        app.lift.move_to_position_one()
                        time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))  # Wait for lift to physically reach position one before moving robot


                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.send_command(f"/api/move?marker={target_marker}")
                        
                        if not move_result or move_result.get('status') != 'OK':
                            logger.error(f"Failed to start moving to {target_marker} (attempt {retry_count + 1}): {move_result}")
                            if _is_robot_busy_response(move_result):
                                cancel_robot_move_for_retry(
                                    app.robot_control,
                                    target_marker,
                                    "move start was rejected because another move is still active"
                                )
                            retry_count += 1
                            time.sleep(1)
                            continue
                            
                        logger.info(f"Movement result: {move_result}")

                        # Wait for the robot to finish moving with improved timeout handling
                        move_complete = wait_for_robot_move(app.robot_control, target_marker)

                        if move_complete:
                            logger.info(f"Robot successfully reached marker {target_marker}")

                            # if target_marker is CD, skip taking photos
                            if target_marker == "CD":
                                logger.info("Skipping photo taking at CD")
                            else:
                                # take photos at the target marker
                                logger.info(f"Taking photos at marker {target_marker}")
                                time.sleep(2)  # Give some time for the robot to stabilize at the marker

                                photo_result = app.camera_control.take_photo_all_cameras(position_info=target_marker, timestamp=timestamp)
                                logger.debug(f"Raw photo result: {photo_result}")

                                if photo_result.get('status') == 'OK':
                                    # 从 results 中提取所有成功的文件路径
                                    new_files = [r['filepath'] for r in photo_result.get('results', [])
                                                if r.get('status') == 'OK' and 'filepath' in r]

                                    if new_files:
                                        file_paths.extend(new_files)
                                        logger.info(f"Saved {len(new_files)} photos at {target_marker}")
                                    else:
                                        status = TASK_STATUS_PARTIAL
                                        logger.warning(f"No photos saved at {target_marker} despite OK status")
                                else:
                                    status = TASK_STATUS_PARTIAL
                                    logger.warning(f"Photo failed at {target_marker}: {photo_result.get('message')}")
                                    logger.debug(f"Photo result: {photo_result}")

                            move_success = True
                            current_marker_index += 1  # Only advance to next marker after confirmed success
                        else:
                            logger.warning(f"Movement to {target_marker} not completed (attempt {retry_count + 1})")
                            cancel_robot_move_for_retry(
                                app.robot_control,
                                target_marker,
                                "move did not complete before retry"
                            )
                            retry_count += 1
                            
                    # # Check if next marker is CD and lift needs to be lowered
                    # if current_marker_index == len(marker_list) - 2:  # Second last marker (before CD)
                    #     logger.info("Next marker is CD, moving lift to position one...")
                    #     app.lift.move_to_position_one()
                    #     # time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))

                    if not move_success:
                        raise Exception(f"Failed to move to {target_marker} after {max_retries} attempts")
             

            elif task.action == 1:  # 录像
                logger.info("Starting video recording task...")
                start_timestamp = int(time.time())
                recording_started = False
                camera_ids = [1, 2, 3, 4, 5, 6]  # 使用前6个IP摄像头
                start_marker = marker_list[0]  # 记录开始点位
                
                current_marker_index = 0
                while current_marker_index < len(marker_list):
                    target_marker = marker_list[current_marker_index]
                    logger.info(f"Moving to target marker: {target_marker} (sequence {current_marker_index+1}/{len(marker_list)})")

                    # Check if target is CD and adjust lift position
                    if target_marker == "CD":
                        logger.info("Next marker is CD, moving lift to position one...")
                        app.lift.move_to_position_one()
                        time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))  # Wait for lift to physically reach position one before moving robot


                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.send_command(f"/api/move?marker={target_marker}")
                        
                        if not move_result or move_result.get('status') != 'OK':
                            logger.error(f"Failed to start moving to {target_marker} (attempt {retry_count + 1}): {move_result}")
                            if _is_robot_busy_response(move_result):
                                cancel_robot_move_for_retry(
                                    app.robot_control,
                                    target_marker,
                                    "move start was rejected because another move is still active"
                                )
                            retry_count += 1
                            time.sleep(1)
                            continue
                            
                        # Wait for the robot to finish moving with improved timeout handling
                        move_complete = wait_for_robot_move(app.robot_control, target_marker)

                        if move_complete:
                            logger.info(f"Robot successfully reached marker {target_marker}")

                            # Start recording after reaching first marker (except if it's CD)
                            if current_marker_index == 0 and target_marker != "CD":
                                logger.info("Starting video recording at first marker...")
                                for cam_id in camera_ids:
                                    try:
                                        recording_result = app.camera_control.start_recording(
                                            camera_id=cam_id,
                                            task_id=task_id,
                                            marker=target_marker
                                        )
                                        if recording_result.get('status') == 'OK':
                                            recording_started = True
                                        else:
                                            logger.error(f"Failed to start recording on camera {cam_id}")
                                            status = TASK_STATUS_PARTIAL
                                    except Exception as e:
                                        logger.error(f"Error starting recording on camera {cam_id}: {str(e)}")
                                        status = TASK_STATUS_PARTIAL

                            move_success = True
                            current_marker_index += 1
                        else:
                            logger.warning(f"Movement to {target_marker} not completed (attempt {retry_count + 1})")
                            cancel_robot_move_for_retry(
                                app.robot_control,
                                target_marker,
                                "move did not complete before retry"
                            )
                            retry_count += 1

                    if not move_success:
                        raise Exception(f"Failed to move to {target_marker} after {max_retries} attempts")

                    # Stop recording before the last marker (which should be CD)
                    if current_marker_index == len(marker_list) - 1 and recording_started:
                        end_timestamp = int(time.time())
                        end_marker = marker_list[current_marker_index - 1]  # 记录结束点位
                        logger.info("Stopping video recording before CD...")
                        
                        for cam_id in camera_ids:
                            try:
                                stop_result = app.camera_control.stop_recording(
                                    camera_id=cam_id,
                                    task_id=task_id,
                                    start_marker=start_marker,
                                    start_timestamp=start_timestamp,
                                    end_marker=end_marker
                                )
                                if stop_result.get('status') == 'OK':
                                    video_file = stop_result.get('filepath')  # Use the filepath from the response
                                    if video_file:
                                        file_paths.append(video_file)
                                else:
                                    logger.error(f"Failed to stop recording on camera {cam_id}")
                                    status = TASK_STATUS_PARTIAL
                            except Exception as e:
                                logger.error(f"Error stopping recording on camera {cam_id}: {str(e)}")
                                status = TASK_STATUS_PARTIAL
            elif task.action == 99:  # Move only
                current_marker_index = 0
                while current_marker_index < len(marker_list):
                    target_marker = marker_list[current_marker_index]
                    logger.info(f"Moving to target marker: {target_marker} (sequence {current_marker_index+1}/{len(marker_list)})")

                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.send_command(f"/api/move?marker={target_marker}")
                        
                        if not move_result or move_result.get('status') != 'OK':
                            logger.error(f"Failed to start moving to {target_marker} (attempt {retry_count + 1}): {move_result}")
                            if _is_robot_busy_response(move_result):
                                cancel_robot_move_for_retry(
                                    app.robot_control,
                                    target_marker,
                                    "move start was rejected because another move is still active"
                                )
                            retry_count += 1
                            time.sleep(1)
                            continue
                            
                        logger.info(f"Movement result: {move_result}")

                        # Wait for the robot to finish moving with improved timeout handling
                        move_complete = wait_for_robot_move(app.robot_control, target_marker)

                        if move_complete:
                            logger.info(f"Robot successfully reached marker {target_marker}")
                            move_success = True
                            current_marker_index += 1  # Only advance to next marker after confirmed success
                        else:
                            logger.warning(f"Movement to {target_marker} not completed (attempt {retry_count + 1})")
                            cancel_robot_move_for_retry(
                                app.robot_control,
                                target_marker,
                                "move did not complete before retry"
                            )
                            retry_count += 1
                            
                    if not move_success:
                        raise Exception(f"Failed to move to {target_marker} after {max_retries} attempts")
            else:
                status = 4
                raise Exception(f"Unknown action type: {task.action}")
            
            if status == TASK_STATUS_INPROGRESS:
                status = TASK_STATUS_COMPLETED
        except Exception as e:
            status = 4
            logger.error(f"Error executing task {task_id}: {str(e)}")
            # 安全降柱：只在升降柱确实升起过的情况下执行
            try:
                if app.lift and lift_was_raised:
                    logger.info("Moving lift to position one due to task failure...")
                    app.lift.move_to_position_one()
            except Exception as lift_error:
                logger.error(f"Failed to move lift to position one in error handler: {str(lift_error)}")
            
            # if task.action == 1 and 'recording_started' in locals() and recording_started:
            #     try:
            #         stop_result = app.obs_control.stop_recording()
            #         if stop_result.get('status') == 'OK':
            #             file_paths.extend(stop_result.get('file_paths', []))
            #     except Exception as stop_error:
            #         logger.error(f"Error stopping recording after failure: stop_error")
        finally:
            # Release task execution lock
            try:
                task_exec_lock.release()
                logger.info("Task execution lock released")
            except Exception:
                pass  # Lock may not have been acquired

            if task_log:
                task_log.status = status
                task_log.end_time = datetime.now()
                task_log.file_count = len(file_paths)
                task_log.file_paths = json.dumps(file_paths)
                db.session.commit()
                logger.info(f"Task log updated - Status: {status}, Files: {len(file_paths)}")


@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除盘点任务"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'status': 'OK'})


@bp.route('/api/tasks/<int:task_id>/logs', methods=['GET'])
def get_task_logs(task_id):
    """Get all execution logs for a task"""
    logs = TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.start_time.desc()).all()
    return jsonify([{
        'log_id': log.log_id,
        'start_time': log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': log.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        'status': log.status,
        'file_count': log.file_count
    } for log in logs])

@bp.route('/api/task-logs', methods=['GET'])
def get_paginated_task_logs():
    """获取分页任务日志"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        
        if page < 1 or size < 1:
            return jsonify({
                'status': 'ERROR',
                'message': 'Invalid page or size parameters'
            }), 400

        # Get paginated logs
        logs = TaskLog.query.order_by(
            TaskLog.start_time.desc()
        ).paginate(page=page, per_page=size, error_out=False)

        return jsonify({
            'status': 'OK',
            'data': [{
                'log_id': log.log_id,
                'task_id': log.task_id,
                'start_time': log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'end_time': log.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': log.status,
                'file_count': log.file_count
            } for log in logs.items],
            'pagination': {
                'page': page,
                'size': size,
                'total': logs.total,
                'pages': logs.pages
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get task logs: {str(e)}'
        }), 500

@bp.route('/api/task-logs/clear', methods=['POST'])
def clear_task_logs():
    """清空所有任务日志"""
    try:
        num_deleted = db.session.query(TaskLog).delete()
        db.session.commit()
        return jsonify({
            'status': 'OK',
            'message': f'成功删除 {num_deleted} 条日志'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'message': f'清空日志失败: {str(e)}'
        }), 500

@bp.route('/task-logs/<int:log_id>', methods=['GET'])
def task_log_detail_page(log_id):
    """单个任务日志详情页面"""
    return render_template('task-log-detail.html', log_id=log_id)

@bp.route('/api/task-logs/<int:log_id>', methods=['GET'])
def get_task_log_detail(log_id):
    """获取单个任务日志详情"""
    log = TaskLog.query.get_or_404(log_id)
    task = Task.query.get(log.task_id)
    return jsonify({
        'log_id': log.log_id,
        'task_id': log.task_id,
        'marker': log.marker,
        'action': log.action,
        'description': task.description if task else '',
        'start_time': log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': log.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        'status': log.status,
        'file_count': log.file_count,
        'file_paths': json.loads(log.file_paths)
    })


### LIFT  ROUTES ###########################################################################################

def get_lift():
    """获取Lift实例，按需初始化，避免全局current_app错误"""
    from .lift_control import Lift
    port = current_app.config.get('LIFT_PORT', '/dev/ttyUSB0')
    baudrate = 115200
    try:
        return Lift(port=port, baudrate=baudrate)
    except Exception as e:
        logger.error(f"Failed to initialize Lift: {e}")
        return None

@bp.route('/api/lift/status', methods=['GET'])
def lift_status():
    """Check lift connection status"""
    lift = get_lift()
    if lift is None:
        return jsonify({
            'status': 'error',
            'message': 'Lift not initialized',
            'connected': False
        }), 503
    try:
        connected = lift.serial_connection.is_open
        return jsonify({
            'status': 'success',
            'message': 'Lift is connected' if connected else 'Lift is disconnected',
            'connected': connected
        })
    except Exception as e:
        logger.error(f"Error checking lift status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'connected': False
        }), 500

@bp.route('/api/lift/<command>', methods=['POST'])
def lift_command(command):
    lift = get_lift()
    if lift is None:
        return jsonify({'error': 'Lift not initialized'}), 503
    try:
        if command == 'move_to_position_one':
            lift.move_to_position_one()
        elif command == 'move_to_position_two':
            lift.move_to_position_two()
        elif command == 'move_to_position_three':
            lift.move_to_position_three()
        elif command == 'move_up':
            lift.move_up()
        elif command == 'move_down':
            lift.move_down()
        elif command == 'reset':
            lift.reset()
        elif command == 'stop_moving_up':
            lift.stop_moving_up()
        elif command == 'stop_moving_down':
            lift.stop_moving_down()
        else:
            return jsonify({'error': 'Invalid command'}), 400
        return jsonify({'status': 'success', 'command': command})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['NEED_AUTH']:
            return f(*args, **kwargs)
        if 'authenticated' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if not current_app.config['NEED_AUTH']:
        return redirect(url_for('main.tasks_page'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin':
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            if hashed_password == current_app.config['ADMIN_PASSWORD']:
                session['authenticated'] = True
                session['role'] = 'admin'
                session['username'] = username
                return redirect(url_for('main.tasks_page'))

        elif username == 'su':
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            if hashed_password == current_app.config['SUPER_USER_PASSWORD']:
                session['authenticated'] = True
                session['role'] = 'super_user'
                session['username'] = username
                return redirect(url_for('main.index'))

        flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('authenticated', None)
    session.pop('role', None)
    session.pop('username', None)
    flash('已退出登录', 'info')
    return redirect(url_for('main.login'))

@bp.route('/settings')
@login_required
def settings():
    """设置页面"""
    env_path = os.path.join(current_app.config['BASEDIR'], '.env')
    
    # 获取环境变量，如果不存在则使用Config中的默认值
    env_vars = {
        # 基础摄像头配置
        'CAMERA_WIDTH': str(current_app.config['CAMERA_CONFIG']['resolution']['width']),
        'CAMERA_HEIGHT': str(current_app.config['CAMERA_CONFIG']['resolution']['height']),
        'CAMERA_FPS': str(current_app.config['CAMERA_CONFIG']['fps']),
        'CAMERA_JPEG_QUALITY': str(current_app.config['CAMERA_CONFIG']['jpeg_quality']),
        'CAMERA_BUFFER_SIZE': str(current_app.config['CAMERA_CONFIG']['buffer_size']),
        'PHOTO_MODE': str(current_app.config.get('PHOTO_MODE', '0')),
        'CAMERA_URLS': '',

        # 高级相机参数
        'CAMERA_BRIGHTNESS': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('brightness', '16')),
        'CAMERA_CONTRAST': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('contrast', '40')),
        'CAMERA_SATURATION': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('saturation', '80')),
        'CAMERA_SHARPNESS': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('sharpness', '6')),
        'CAMERA_GAMMA': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('gamma', '120')),
        'CAMERA_AUTO_EXPOSURE': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('auto_exposure', '1')),
        'CAMERA_EXPOSURE_TIME': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('exposure_time', '80')),
        'CAMERA_GAIN': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('gain', '20')),
        'CAMERA_WB_AUTO': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('white_balance_auto', '0')),
        'CAMERA_WB_TEMP': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('white_balance_temp', '5000')),
        'CAMERA_FOCUS_AUTO': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('focus_auto', '0')),
        'CAMERA_FOCUS': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('focus_absolute', '200')),
        'CAMERA_BACKLIGHT': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('backlight_comp', '0')),
        'CAMERA_POWERLINE_FREQ': str(current_app.config['CAMERA_CONFIG'].get('control_params', {}).get('power_line_freq', '1')),

        # 学校配置
        'CCODE': str(current_app.config.get('CCODE', '01')),

        # 其他配置
        'ROBOT_IP': str(current_app.config['ROBOT_IP']),
        'ROBOT_PORT': str(current_app.config['ROBOT_PORT']),
        'OBS_WS_URL': str(current_app.config['OBS_WS_URL']),
        'OBS_PASSWORD': str(current_app.config['OBS_PASSWORD']),
        'OBS_FOCUS_TIME': str(float(current_app.config.get('OBS_FOCUS_TIME', 1.0))),
        'FTP_MOCK_MODE': str(current_app.config.get('FTP_MOCK_MODE', 'false')).lower(),
        'FTP_HOST': str(current_app.config.get('FTP_HOST', '')),
        'FTP_PORT': int(current_app.config.get('FTP_PORT', '')),
        'FTP_USER': str(current_app.config.get('FTP_USER', '')),
        'FTP_PASS': str(current_app.config.get('FTP_PASS', '')),
        'LIFT_PORT': str(current_app.config.get('LIFT_PORT', '')),
        'LIFT_WAIT_TIME': int(current_app.config.get('LIFT_WAIT_TIME', '15')),
        'LIFT_HEIGHT': str(current_app.config.get('LIFT_HEIGHT', 'L2')),
    }
    
    # 如果.env文件不存在，创建一个新的
    if not os.path.exists(env_path):
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            current_app.logger.info(f"Created new .env file at {env_path}")
        except Exception as e:
            current_app.logger.error(f"Failed to create .env file: {str(e)}")
    else:
        # 如果文件存在，读取现有的值
        load_dotenv(env_path)
        for key in env_vars.keys():
            if os.environ.get(key):
                if key == 'CAMERA_URLS':
                    # 将逗号分隔的URLs转换为换行分隔
                    env_vars[key] = os.environ.get(key).replace(',', '\n')
                else:
                    env_vars[key] = os.environ.get(key)
    
    return render_template('settings.html', env=env_vars)

@bp.route('/api/settings', methods=['POST'])
@login_required
def update_settings():
    """更新设置"""
    try:
        data = request.get_json()
        env_path = os.path.join(current_app.config['BASEDIR'], '.env')
        
        # 验证数据
        required_fields = [
            # 基础配置
            'CAMERA_WIDTH', 'CAMERA_HEIGHT', 'CAMERA_FPS', 
            'CAMERA_JPEG_QUALITY', 'CAMERA_BUFFER_SIZE', 'ROBOT_IP', 
            'ROBOT_PORT', 'OBS_WS_URL', 'OBS_PASSWORD', 'LIFT_PORT',
            'PHOTO_MODE',
            # 学校配置
            'CCODE',
            # 相机控制参数
            'CAMERA_BRIGHTNESS', 'CAMERA_CONTRAST', 'CAMERA_SATURATION',
            'CAMERA_SHARPNESS', 'CAMERA_GAMMA', 'CAMERA_AUTO_EXPOSURE',
            'CAMERA_EXPOSURE_TIME', 'CAMERA_GAIN', 'CAMERA_WB_AUTO',
            'CAMERA_WB_TEMP', 'CAMERA_FOCUS_AUTO', 'CAMERA_FOCUS',
            'CAMERA_BACKLIGHT', 'CAMERA_POWERLINE_FREQ'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # 验证校区代码必须是两位数字
        if 'CCODE' in data:
            ccode_value = str(data['CCODE']).strip()
            if not re.match(r'^\d{2}$', ccode_value):
                raise ValueError("校区代码必须是两位数字，例如：01、02、03 等")
        
        # 验证数值范围
        validations = {
            'CAMERA_JPEG_QUALITY': (1, 100),
            'CAMERA_BUFFER_SIZE': (1, 100),
            'CAMERA_BRIGHTNESS': (0, 255),
            'CAMERA_CONTRAST': (0, 255),
            'CAMERA_SATURATION': (0, 255),
            'CAMERA_SHARPNESS': (0, 100),
            'CAMERA_GAMMA': (0, 500),
            'CAMERA_AUTO_EXPOSURE': (0, 1),
            'CAMERA_WB_AUTO': (0, 1),
            'CAMERA_FOCUS_AUTO': (0, 1),
            'CAMERA_BACKLIGHT': (0, 1),
            'CAMERA_POWERLINE_FREQ': (1, 2),
            'PHOTO_MODE': (0, 2)  # 添加 PHOTO_MODE 的验证范围
        }
        
        for field, (min_val, max_val) in validations.items():
            if field in data:
                value = int(data[field])
                if not (min_val <= value <= max_val):
                    raise ValueError(f"{field} must be between {min_val} and {max_val}")
        
        # 确保.env文件目录存在
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        
        # 更新.env文件
        for key, value in data.items():
            # 确保布尔值被正确处理
            if key in ['FTP_MOCK_MODE']:
                value = str(value).lower()  # 确保是小写的 'true' 或 'false'
            set_key(env_path, key, str(value))
        
        # 重新加载环境变量以立即生效
        load_dotenv(env_path, override=True)
        
        # # 更新 __init__.py 时间戳以触发 Flask 重载
        # if update_init_timestamp():
        #     logger.info("Settings and timestamp updated successfully")
        #     return jsonify({
        #         'status': 'OK', 
        #         'message': '设置已保存，系统正在重新加载...',
        #         'reload': True
        #     })
        # else:
        #     logger.warning("Settings saved but reload trigger failed")
        #     return jsonify({
        #         'status': 'OK', 
        #         'message': '设置已保存，但自动重载失败，请手动重启应用',
        #         'reload': False
        #     })

        return jsonify({
            "status": "OK",
            "message": "Settings updated successfully"
        }), 200

    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

@bp.route('/api/robot/recharge', methods=['POST'])
def robot_recharge():
    """机器人充电API"""
    try:
        robot_control = current_app.robot_control
        
        # 1. 查询MarkerConfig表中所有以CD开头的点位名称
        cd_markers = MarkerConfig.query.filter(
            MarkerConfig.mid_short.like('CD%')
        ).all()
        
        if not cd_markers:
            # 如果没有找到CD开头的点位，提示用户同步机器人点位
            return jsonify({
                "status": "ERROR",
                "message": "未找到充电点位，请先同步机器人点位配置",
                "results": None
            }), 400
        
        # 2. 使用第一个CD点位作为move_target
        # 按mid_short排序，确保一致性
        cd_markers.sort(key=lambda m: m.mid_short)
        target_marker = cd_markers[0].mid_short
        
        # 3. 先检查当前是否已在目标充电点
        status = robot_control.get_status()
        if status.get('results', {}).get('move_target') == target_marker and \
           status.get('results', {}).get('move_status') == 'succeeded':
            return jsonify({
                "status": "OK",
                "message": f"Already at charging station ({target_marker})",
                "results": status.get('results', {})
            })
        
        # 4. 如果不在充电点，则发送充电命令
        # 修改recharge方法以接受参数，或者直接调用send_command
        result = robot_control.send_command(f"/api/move?marker={target_marker}")
        
        return jsonify({
            "status": result.get("status", "ERROR"),
            "message": result.get("error_message", ""),
            "results": result.get("results", {})
        })
    except Exception as e:
        logger.error(f"Error in robot_recharge: {str(e)}")
        return jsonify({
            "status": "ERROR",
            "message": str(e),
            "results": None
        }), 500

@bp.route('/api/robot/status')
def robot_status():
    """获取机器人当前状态API"""
    robot_control = current_app.robot_control
    status = robot_control.get_status()
    
    results = status.get("results", {})
    response = {
        "move_target": results.get("move_target", ""),
        "move_status": results.get("move_status", ""),
        "running_status": results.get("running_status", ""),
        "charge_state": results.get("charge_state", False),
        "estop_state": results.get("estop_state", False),
        "power_percent": results.get("power_percent", 0)
    }
    
    return jsonify(response)


@bp.route('/api/move/cancel', methods=['POST'])
def move_cancel():
    """取消机器人当前移动任务API"""
    try:
        robot_control = current_app.robot_control
        result = robot_control.cancel_move()
        
        if result.get("status") == "OK":
            return jsonify({
                "status": "OK",
                "message": "Move cancelled successfully"
            })
        else:
            return jsonify({
                "status": "ERROR",
                "message": result.get("error_message", "Failed to cancel move")
            }), 500
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500
    


def update_init_timestamp():
    """更新 __init__.py 的时间戳注释以触发 Flask 重载"""
    try:
        init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
        
        with open(init_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新或添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp_line = f"# Last config update: {timestamp}\n"
        
        if lines and lines[0].startswith('# Last config update:'):
            lines[0] = timestamp_line
        else:
            lines.insert(0, timestamp_line)
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(f"Updated __init__.py timestamp to trigger reload: {timestamp}")
        return True
    except Exception as e:
        logger.error(f"Failed to update __init__.py timestamp: {str(e)}")
        return False

import psutil
import subprocess

def get_obs_executable():
    """获取OBS可执行文件路径"""
    import platform
    system = platform.system().lower()
    
    if system == 'windows':
        # Windows路径
        default_path = r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'
    else:
        # Linux路径
        default_path = '/usr/bin/obs'
    
    return os.environ.get('OBS_PATH', default_path)

def check_obs_process():
    """检查OBS进程状态"""
    import platform
    system = platform.system().lower()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'environ']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            
            # 根据系统检查进程名
            if system == 'windows' and proc_name in ['obs.exe', 'obs64.exe']:
                is_obs = True
            elif system != 'windows' and proc_name in ['obs', 'obs-studio']:
                is_obs = True
            else:
                is_obs = False
                
            if is_obs:
                cmdline = proc.info['cmdline'] or []
                env = proc.info['environ'] or {}
                # 检查是否为后台模式
                is_headless = (
                    any(flag in cmdline for flag in [
                        '--minimize-to-tray', 
                        '--startstreaming', 
                        '--startvirtualcam', 
                        '--headless',
                        '--disable-gpu'
                    ]) or
                    env.get('OBS_USE_HEADLESS') == '1' or
                    env.get('QT_QPA_PLATFORM') == 'offscreen'
                )
                return {
                    'running': True,
                    'headless': is_headless,
                    'pid': proc.pid,
                    'cmdline': cmdline,
                    'environ': env  # 添加环境变量信息用于调试
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    return {'running': False, 'headless': False, 'pid': None}

@bp.route('/api/obs/status')
def obs_status():
    """获取OBS运行状态"""
    try:
        status = check_obs_process()
        return jsonify(status)
    except Exception as e:
        logger.error(f"检查OBS状态时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/obs/start', methods=['POST'])
def start_obs():
    """启动OBS"""
    try:
        data = request.get_json()
        headless = data.get('headless', False)
        
        # 检查OBS是否已经在运行
        status = check_obs_process()
        if status['running']:
            return jsonify({'error': 'OBS已经在运行中'}), 400
            
        # 获取OBS可执行文件路径
        obs_path = get_obs_executable()
        if not os.path.exists(obs_path):
            return jsonify({'error': f'OBS可执行文件未找到: {obs_path}'}), 404
            
        # 准备命令行参数
        cmd = [obs_path]
        if headless:
            # 后台模式启动
            if platform.system().lower() == 'windows':
                cmd.extend([
                    '--startvirtualcam',
                    '--minimize-to-tray',
                    '--headless',
                    '--disable-shutdown-check',
                    '--disable-updater',
                    '--disable-gpu'
                ])
            else:
                # Linux下的后台启动参数
                cmd.extend([
                    '--startvirtualcam',
                    '--headless',
                    '--disable-shutdown-check',
                    '--disable-updater',
                    '--disable-gpu'
                ])
                
            # 确保不会启动GUI
            os.environ['OBS_USE_HEADLESS'] = '1'
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # 强制使用offscreen渲染
            os.environ['DISABLE_QT_COMPAT'] = '1'  # 禁用Qt兼容模式
                
        try:
            # 根据系统使用不同的启动方式
            if platform.system().lower() == 'windows':
                # Windows下的启动方式
                startupinfo = None
                if headless:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    cmd,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if headless else 0
                )
            else:
                # Linux下的启动方式
                env = os.environ.copy()
                if headless:
                    # 确保有显示服务器
                    if 'DISPLAY' not in env:
                        env['DISPLAY'] = ':0'
                    process = subprocess.Popen(
                        cmd,
                        env=env,
                        start_new_session=True,
                        stdout=subprocess.PIPE if headless else None,
                        stderr=subprocess.PIPE if headless else None
                    )
                else:
                    process = subprocess.Popen(cmd, env=env)
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"启动OBS失败: {str(e)}")
            return jsonify({'error': f'启动失败: {str(e)}'}), 500
            
        # 等待进程启动
        time.sleep(3)
        status = check_obs_process()
        if status['running']:
            return jsonify({'success': True, 'message': '启动成功'})
        else:
            return jsonify({'error': '启动失败'}), 500
            
    except Exception as e:
        logger.error(f"启动OBS时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/obs/stop', methods=['POST'])
def stop_obs():
    """停止OBS并确保完全清理"""
    try:
        status = check_obs_process()
        if not status['running']:
            return jsonify({'success': True, 'message': 'OBS未在运行'})
            
        # 获取OBS进程
        pid = status['pid']
        if pid:
            try:
                process = psutil.Process(pid)
                # 终止所有子进程
                for child in process.children(recursive=True):
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        continue
                
                # 终止主进程
                process.terminate()
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    process.kill()
                
                # 额外检查确保进程已终止
                time.sleep(1)
                if not psutil.pid_exists(pid):
                    return jsonify({'success': True, 'message': 'OBS已完全停止'})
                else:
                    return jsonify({'error': '未能完全停止OBS'}), 500
                    
            except psutil.NoSuchProcess:
                return jsonify({'success': True, 'message': 'OBS进程已不存在'})
        else:
            return jsonify({'error': '无法获取OBS进程ID'}), 500
            
    except Exception as e:
        logger.error(f"停止OBS时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500


def move_lift_to_configured_height(lift_height):
    """Move the lift to the specified height position (L2/L3)"""
    try:
        if current_app.lift:
            if lift_height == 'L3':
                current_app.lift.move_to_position_three()
                logger.info("Moving lift to position three (L3)")
            else:  # Default to L2
                current_app.lift.move_to_position_two()
                logger.info("Moving lift to position two (L2)")
            return True
        return False
    except Exception as e:
        logger.error(f"Error moving lift: {str(e)}")
        return False


@bp.route('/ipcams')
@login_required
def ipcams():
    """网络摄像头仪表盘页面，支持多行和逗号分隔的 CAMERA_URLS"""
    cameras = []
    urls_str = os.environ.get('CAMERA_URLS', '')
    
    for line in urls_str.splitlines():
        url = line.strip()
        if not url:
            continue
            
        # Extract camera name from RTSP URL
        # Handle both formats:
        # - rtsp://admin:boku2025@192.168.10.64:554/Streaming/Channels/101 (with password)
        # - rtsp://admin@192.168.10.21:554/user=admin&password=&channel=1&stream=0.sdp? (without password)
        try:
            # Remove rtsp:// prefix
            if url.startswith('rtsp://'):
                url_without_protocol = url[7:]
                
                # Extract host/IP part
                if '@' in url_without_protocol:
                    # URL with authentication: user:pass@host
                    host_part = url_without_protocol.split('@', 1)[1]
                else:
                    # URL without authentication
                    host_part = url_without_protocol
                
                # Extract host/IP (remove port and path)
                host = host_part.split(':')[0].split('/')[0]
                
                cameras.append({
                    'name': host,
                    'url': url
                })
            else:
                # Fallback for non-RTSP URLs
                cameras.append({
                    'name': f'Camera_{len(cameras)+1}',
                    'url': url
                })
                
        except Exception as e:
            # If parsing fails, use a generic name
            cameras.append({
                'name': f'Camera_{len(cameras)+1}',
                'url': url
            })

    return render_template('ipcams.html', cameras=cameras)


# ----------- 优化：全局复用RTSP连接，降低帧率 -----------
import threading
import queue

# 全局摄像头流管理
camera_streams = {}
camera_queues = {}
camera_threads = {}
FRAME_QUEUE_SIZE = 2
TARGET_FPS = 5  # 目标帧率，可根据需要调整

def camera_stream_worker(cam_id, rtsp_url):
    import cv2, time
    cap = cv2.VideoCapture(rtsp_url)
    q = camera_queues[cam_id]
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
        # 降帧
        time.sleep(1.0 / TARGET_FPS)
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            if q.full():
                try: q.get_nowait()
                except: pass
            q.put(buffer.tobytes())



@bp.route('/video_feed/<int:cam_id>')
def video_feed(cam_id):
    cameras = []
    urls_str = os.environ.get('CAMERA_URLS', '')
    for line in urls_str.splitlines():
        cameras.append(line.strip())

    if cam_id < 1 or cam_id > len(cameras):
        return "Invalid camera id", 404

    rtsp_url = cameras[cam_id - 1]

    print(f"RTSP URL: {rtsp_url}")
    # 初始化队列和线程
    if cam_id not in camera_queues or camera_queues[cam_id] is None:
        camera_queues[cam_id] = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
    if cam_id not in camera_threads or camera_threads[cam_id] is None or not camera_threads[cam_id].is_alive():
        t = threading.Thread(target=camera_stream_worker, args=(cam_id, rtsp_url), daemon=True)
        camera_threads[cam_id] = t
        t.start()

    def generate():
        placeholder_path = os.path.join(current_app.root_path, 'static', 'res', 'placeholder.png')
        while True:
            try:
                # 检查 camera_queues[cam_id] 是否为 None
                if cam_id not in camera_queues or camera_queues[cam_id] is None:
                    logger.warning(f"Camera queue for cam_id {cam_id} is None. Stopping video feed.")
                    break  # 优雅地退出生成器

                # 从队列中获取帧
                frame = camera_queues[cam_id].get(timeout=2)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except queue.Empty:
                # 如果队列为空，返回占位图
                logger.warning(f"Frame queue for cam_id {cam_id} is empty. Returning placeholder image.")
                with open(placeholder_path, 'rb') as f:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n')
            except Exception as e:
                # 捕获其他异常并记录日志
                logger.error(f"Error in video feed generator for cam_id {cam_id}: {str(e)}")
                with open(placeholder_path, 'rb') as f:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n')
                break  # 遇到异常时退出生成器

    return Response(stream_with_context(generate()), mimetype='multipart/x-mixed-replace; boundary=frame')


# @bp.route('/release_all_cameras', methods=['POST'])
# def release_all_cameras():
#     """释放所有摄像头资源"""
#     for cam_id in list(camera_threads.keys()):
#         # 停止线程
#         camera_threads[cam_id] = None
#         # 清空队列
#         if cam_id in camera_queues:
#             camera_queues[cam_id] = None
#         # 释放摄像头连接
#         if cam_id in camera_streams:
#             camera_streams[cam_id].release()
#             camera_streams.pop(cam_id, None)
#     return jsonify({'status': 'success', 'message': 'All camera resources released'})


camera_active = True  # 全局标志位

@bp.route('/release_all_cameras', methods=['POST'])
def release_all_cameras():
    """释放所有摄像头资源"""
    global camera_active
    camera_active = False  # 通知生成器停止工作
    try:
        for cam_id in list(camera_threads.keys()):
            # 停止线程
            camera_threads[cam_id] = None
            # 清空队列
            if cam_id in camera_queues:
                camera_queues[cam_id] = None
            # 释放摄像头连接
            if cam_id in camera_streams:
                camera_streams[cam_id].release()
                camera_streams.pop(cam_id, None)
        return jsonify({'status': 'success', 'message': 'All camera resources released'})
    except Exception as e:
        logger.error(f"Error releasing camera resources: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Failed to release camera resources: {str(e)}'}), 500




@bp.route('/crontab')
@login_required
def crontab():
    return render_template('crontab.html')


@bp.route('/api/crontab/list', methods=['GET'])
def list_crontab():
    """List all crontab entries."""
    try:
        result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 400
        return jsonify({"crontab": result.stdout.strip().split('\n')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/api/crontab/save', methods=['POST'])
def save_crontab():
    """Save the updated crontab content."""
    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' in request body"}), 400

    print(f"Received crontab content: {data['content']}")
    try:
        # Write the new crontab content
        result = subprocess.run(['crontab', '-'], input=data['content'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 400
        return jsonify({"message": "Crontab saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
