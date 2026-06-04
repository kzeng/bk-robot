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
import subprocess
from dotenv import load_dotenv, set_key
from loguru import logger
import os
from flask import stream_with_context, Response
import cv2
import re
import requests

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


def _status_after_cleanup_failure(status):
    if status == TASK_STATUS_INPROGRESS:
        return TASK_STATUS_COMPLETED
    return status


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


def super_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config['NEED_AUTH'] and session.get('role') != 'super_user':
            return jsonify({'status': 'ERROR', 'message': '需要超级用户权限'}), 403
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
            "title": "4.设备信息",
            "url": "#",
            "cmd": "/api/core/system/v1/robot/info"
        },
        {
            "title": "5.设备健康状态",
            "url": "#",
            "cmd": "/api/core/system/v1/robot/health"
        },
        {
            "title": "6.机器人能力列表",
            "url": "#",
            "cmd": "/api/core/system/v1/capabilities"
        },
        {
            "title": "7.电源状态",
            "url": "#",
            "cmd": "/api/core/system/v1/power/status"
        },
        {
            "title": "8.电池包状态",
            "url": "#",
            "cmd": "/api/core/system/v1/battery/pack"
        },
        {
            "title": "9.支持的Action",
            "url": "#",
            "cmd": "/api/core/motion/v1/action-factories"
        },
        {
            "title": "10.当前速度",
            "url": "#",
            "cmd": "/api/core/motion/v1/speed"
        },
        {
            "title": "11.支持的运动策略",
            "url": "#",
            "cmd": "/api/core/motion/v1/strategies"
        },
        {
            "title": "12.剩余路径",
            "url": "#",
            "cmd": "/api/core/motion/v1/path"
        },
        {
            "title": "13.剩余目标点",
            "url": "#",
            "cmd": "/api/core/motion/v1/milestones"
        },
        {
            "title": "14.剩余时间",
            "url": "#",
            "cmd": "/api/core/motion/v1/time"
        },
        {
            "title": "15.里程计位姿",
            "url": "#",
            "cmd": "/api/core/slam/v1/localization/odopose"
        },
        {
            "title": "16.定位质量",
            "url": "#",
            "cmd": "/api/core/slam/v1/localization/quality"
        },
        {
            "title": "17.IMU数据",
            "url": "#",
            "cmd": "/api/core/slam/v1/imu"
        },
        {
            "title": "18.所有楼层",
            "url": "#",
            "cmd": "/api/multi-floor/map/v1/floors"
        },
        {
            "title": "19.点位列表",
            "url": "#",
            "cmd": "/api/multi-floor/map/v1/pois"
        },
        {
            "title": "20.多楼层状态",
            "url": "#",
            "cmd": "/api/multi-floor/status"
        },
        {
            "title": "21.多楼层充电桩",
            "url": "#",
            "cmd": "/api/multi-floor/map/v1/homedocks"
        },
        {
            "title": "22.运行里程",
            "url": "#",
            "cmd": "/api/core/statistics/v1/odometry"
        },
        {
            "title": "23.运行时间",
            "url": "#",
            "cmd": "/api/core/statistics/v1/runtime"
        },
        {
            "title": "24.系统时间戳",
            "url": "#",
            "cmd": "/api/platform/v1/timestamp"
        }
    ]

@bp.route('/')
@login_required
def index():
    """调试界面主页"""
    return render_template('index.html', robot_all_apis_options=robot_all_apis_options)


@bp.route('/docs/<path:filename>')
def serve_docs(filename):
    static_docs_dir = os.path.join(current_app.root_path, 'static', 'docs')
    repo_docs_dir = os.path.join(current_app.config['ROOT_PATH'], 'docs')
    if os.path.exists(os.path.join(static_docs_dir, filename)):
        return send_from_directory(static_docs_dir, filename)
    return send_from_directory(repo_docs_dir, filename)


def _robot_base_swagger_path():
    return os.path.join(
        current_app.config['ROOT_PATH'],
        'docs',
        'robot-chassis',
        'Slamware-RESTful-API-swagger-conf.json'
    )


def _load_robot_base_swagger():
    with open(_robot_base_swagger_path(), 'r', encoding='utf-8') as f:
        return json.load(f)


def _path_template_matches(template, path):
    template_parts = [p for p in template.strip('/').split('/') if p]
    path_parts = [p for p in path.strip('/').split('/') if p]
    if len(template_parts) != len(path_parts):
        return False
    for template_part, path_part in zip(template_parts, path_parts):
        if template_part.startswith('{') and template_part.endswith('}'):
            if not path_part:
                return False
            continue
        if template_part != path_part:
            return False
    return True


def _find_swagger_operation(swagger, method, path):
    method = method.lower()
    for template, methods in (swagger.get('paths') or {}).items():
        if method not in methods:
            continue
        if template == path or _path_template_matches(template, path):
            return template, methods[method]
    return None, None


def _is_robot_base_write_operation(method, path):
    method = method.upper()
    return method != 'GET'


@bp.route('/robot-base-api')
@login_required
@super_user_required
def robot_base_api_page():
    """Slamtec base API test console."""
    return render_template('robot-base-api.html')


@bp.route('/api/robot-base/swagger', methods=['GET'])
@login_required
@super_user_required
def robot_base_swagger():
    """Return a compact operation list from the local Slamtec Swagger file."""
    try:
        swagger = _load_robot_base_swagger()
        operations = []
        for path, methods in sorted((swagger.get('paths') or {}).items()):
            for method, spec in methods.items():
                if method.lower() not in {'get', 'post', 'put', 'delete', 'patch'}:
                    continue
                parameters = []
                has_body = False
                for parameter in spec.get('parameters', []) or []:
                    location = parameter.get('in')
                    if location == 'body':
                        has_body = True
                    parameters.append({
                        'name': parameter.get('name'),
                        'in': location,
                        'required': bool(parameter.get('required')),
                        'description': parameter.get('description', ''),
                    })
                if spec.get('requestBody'):
                    has_body = True
                operations.append({
                    'method': method.upper(),
                    'path': path,
                    'summary': spec.get('summary') or '',
                    'description': spec.get('description') or '',
                    'operationId': spec.get('operationId') or '',
                    'tags': spec.get('tags') or ['Other'],
                    'parameters': parameters,
                    'hasBody': has_body,
                    'isWrite': _is_robot_base_write_operation(method.upper(), path),
                })
        return jsonify({
            'status': 'OK',
            'base_url': current_app.config.get('ROBOT_BASE_URL', ''),
            'operations': operations
        })
    except Exception as e:
        logger.error(f"Failed to load robot base swagger: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500


@bp.route('/api/robot-base/proxy', methods=['POST'])
@login_required
@super_user_required
def robot_base_proxy():
    """Execute a documented Slamtec API request against the configured base."""
    try:
        data = request.get_json() or {}
        method = str(data.get('method') or 'GET').upper()
        path = str(data.get('path') or '').strip()
        query = data.get('query') or {}
        body = data.get('body', None)
        confirmed = bool(data.get('confirmed'))

        if method not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
            raise ValueError('不支持的请求方法')
        if not path.startswith('/api/'):
            raise ValueError('路径必须以 /api/ 开头')

        swagger = _load_robot_base_swagger()
        template, operation = _find_swagger_operation(swagger, method, path)
        if not operation:
            raise ValueError('该接口不在本地思岚Swagger文档中，或方法不匹配')

        is_write = _is_robot_base_write_operation(method, template or path)
        if is_write and not confirmed:
            return jsonify({
                'status': 'CONFIRM_REQUIRED',
                'message': '该接口可能修改底座状态，请确认后再执行',
                'method': method,
                'path': path
            }), 409

        base_url = str(current_app.config.get('ROBOT_BASE_URL') or '').rstrip('/')
        timeout = float(current_app.config.get('ROBOT_API_TIMEOUT', 10))
        started = time.time()
        response = requests.request(
            method,
            f"{base_url}{path}",
            params=query or None,
            json=body if body not in ({}, '', None) else None,
            timeout=timeout
        )
        elapsed_ms = int((time.time() - started) * 1000)

        content_type = response.headers.get('Content-Type', '')
        if response.content and 'application/json' in content_type:
            response_body = response.json()
        elif response.text:
            response_body = response.text
        else:
            response_body = None

        return jsonify({
            'status': 'OK' if response.ok else 'ERROR',
            'method': method,
            'path': path,
            'template': template,
            'http_status': response.status_code,
            'elapsed_ms': elapsed_ms,
            'response': response_body,
            'headers': dict(response.headers),
        }), 200 if response.ok else 502
    except Exception as e:
        logger.error(f"Robot base proxy failed: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 400


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



@bp.route('/api/robot/estop', methods=['POST'])
def robot_estop():
    """Set or clear the robot emergency stop state."""
    data = request.get_json(silent=True) or {}
    enabled = bool(data.get('enabled'))

    try:
        robot_control = current_app.robot_control
        result = robot_control.set_emergency_stop(enabled) or {}
        return jsonify({
            "container": "opt-info",
            "timestamp": time.time(),
            "command": "enter_estop" if enabled else "exit_estop",
            "status": result.get("status", "ERROR"),
            "error_message": result.get("error_message", ""),
            "message": result.get("message", ""),
            "results": result.get("results", None)
        })
    except Exception as e:
        logger.error(f"Error in robot_estop: {str(e)}")
        return jsonify({
            "container": "opt-info",
            "timestamp": time.time(),
            "command": "enter_estop" if enabled else "exit_estop",
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



@bp.route('/api/camera/start_recording', methods=['POST'])
def start_recording():
    """开始录制API"""
    camera_control = current_app.camera_control
    data = request.get_json(silent=True) or {}
    
    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            connect_result = camera_control.connect()
            if connect_result["status"] != "OK":
                return jsonify(connect_result), 500
        
        # Start recording and return result
        result = camera_control.start_recording(
            camera_id=int(data.get('camera_id', 1)),
            task_id=data.get('task_id'),
            marker=data.get('marker')
        )
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

@bp.route('/api/camera/stop_recording', methods=['POST'])
def stop_recording():
    """停止录制API"""
    camera_control = current_app.camera_control
    data = request.get_json(silent=True) or {}

    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            connect_result = camera_control.connect()
            if connect_result["status"] != "OK":
                return jsonify(connect_result), 500
        
        # Stop recording and get result
        result = camera_control.stop_recording(
            camera_id=int(data.get('camera_id', 1)),
            task_id=data.get('task_id'),
            start_marker=data.get('start_marker'),
            start_timestamp=data.get('start_timestamp'),
            end_marker=data.get('end_marker')
        )
        logger.info(f"Stop recording result: {result}")
        
        if result["status"] != "OK":
            return jsonify(result), 500

        # Return success response
        file_path = ""
        if isinstance(result.get("file_paths"), list) and result["file_paths"]:
            # For OpenCV control that returns multiple file paths
            file_path = result["file_paths"][0]
        else:
            file_path = result.get("file_path", result.get("filepath", ""))
            
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



@bp.route('/api/camera/screenshot', methods=['POST'])
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
                'description': task.description
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
    thread = Thread(target=async_run_task, args=(current_app._get_current_object(), task.task_id, task_log.log_id))
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


def get_marker_config_by_short(marker_short):
    return MarkerConfig.query.filter_by(mid_short=marker_short).first()


def normalize_marker_short_list(marker_text):
    marker_list = marker_text.split(',') if marker_text else []
    return [marker.strip() for marker in marker_list if marker.strip()]


def prepare_task_marker_list(marker_text):
    """Return task marker shorts with a same-floor CD marker appended.

    Inventory tasks are not allowed to span floors. CD markers are selected from
    the task floor first, then by global name order as a fallback.
    """
    requested = normalize_marker_short_list(marker_text)
    non_cd = [m for m in requested if not m.upper().startswith('CD')]
    selected_cd = [m for m in requested if m.upper().startswith('CD')]

    configs = []
    for marker in non_cd:
        config = get_marker_config_by_short(marker)
        if not config:
            raise ValueError(f"Unknown marker: {marker}")
        configs.append(config)

    floor_keys = {(c.building or '', c.floor or '') for c in configs}
    if len(floor_keys) > 1:
        raise ValueError("Inventory tasks cannot span multiple floors")

    task_floor_key = next(iter(floor_keys), None)
    cd_query = MarkerConfig.query.filter(MarkerConfig.mid_short.ilike('CD%'))
    cd_configs = cd_query.all()

    cd_marker = None
    if selected_cd:
        cd_marker = selected_cd[0]
    elif task_floor_key:
        same_floor_cds = [
            c for c in cd_configs
            if (c.building or '', c.floor or '') == task_floor_key
        ]
        if same_floor_cds:
            same_floor_cds.sort(key=lambda c: c.mid_short)
            cd_marker = same_floor_cds[0].mid_short

    if not cd_marker and cd_configs:
        cd_configs.sort(key=lambda c: c.mid_short)
        cd_marker = cd_configs[0].mid_short

    if not cd_marker:
        cd_marker = 'CD'

    final_markers = [m for m in non_cd]
    final_markers.append(cd_marker)
    return final_markers


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
            robot_status = robot_control.get_status()
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


def wait_for_robot_move(robot_control, target_marker, max_duration=300, max_consecutive_failures=10, expected_task_id=None):
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

        if expected_task_id and hasattr(robot_control, 'get_action_status'):
            robot_status = robot_control.get_action_status(expected_task_id)
        else:
            robot_status = robot_control.get_status()

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
        actual_marker = results.get('move_target') or target_marker
        move_status = results.get('move_status')
        current_pose = results.get('current_pose')
        move_retry_times = results.get('move_retry_times')
        current_task_id = results.get('task_id')

        if expected_task_id and current_task_id and current_task_id != expected_task_id:
            logger.info(
                f"Ignoring stale move status for {target_marker}: "
                f"expected_task_id={expected_task_id}, current_task_id={current_task_id}, "
                f"move_status={move_status}"
            )
            time.sleep(0.5)
            continue

        if move_status == 'succeeded' and actual_marker == target_marker:
            logger.info(f"Robot successfully reached marker {target_marker}")
            return True
        elif move_status in ['failed', 'canceled']:
            raise Exception(f"Movement {move_status} at {target_marker}")

        if actual_marker == target_marker and move_status in ['running', 'moving', 'paused']:
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


def async_run_task(app, task_id, task_log_id=None):
    """在后台线程中执行任务"""
    with app.app_context():
        task_log = TaskLog.query.get(task_log_id) if task_log_id else None
        if task_log_id and not task_log:
            logger.error(f"Task log {task_log_id} not found for task {task_id}")

        task = Task.query.get(task_id)
        if not task:
            if task_log:
                task_log.status = TASK_STATUS_FAILED
                task_log.end_time = datetime.now()
                db.session.commit()
            try:
                task_exec_lock.release()
                logger.info("Task execution lock released because task was not found")
            except Exception:
                pass
            return
        
        timestamp = str(int(time.time()))
        marker_list = prepare_task_marker_list(task.marker)


        logger.info(f"Final marker list for task {task_id}: {marker_list}")

        if not task_log:
            task_log = TaskLog.query.filter_by(task_id=task_id)\
                                   .order_by(TaskLog.start_time.desc())\
                                   .first()

        inventory_marker_count = len([marker for marker in marker_list if marker != 'CD'])
        if task.action in (0, 1) and inventory_marker_count == 0:
            if task_log:
                task_log.status = TASK_STATUS_FAILED
                task_log.end_time = datetime.now()
                db.session.commit()
            logger.error(f"Task {task_id} has no inventory markers")
            try:
                task_exec_lock.release()
                logger.info("Task execution lock released because task has no inventory markers")
            except Exception:
                pass
            return
            
    
        status = TASK_STATUS_INPROGRESS  # 1 = in progress
        file_paths = []
        
        try:
            if task.action == 0:  # 拍照
                logger.info("Starting movement through markers for photo task ......")
                current_marker_index = 0
                while current_marker_index < len(marker_list):
                    target_marker = marker_list[current_marker_index]
                    logger.info(f"Moving to target marker: {target_marker} (sequence {current_marker_index+1}/{len(marker_list)})")

                    logger.info(f"Want to move target {target_marker}")

                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.move_to_marker(target_marker)
                        
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
                        move_task_id = (move_result.get('results') or {}).get('task_id')
                        move_complete = wait_for_robot_move(app.robot_control, target_marker, expected_task_id=move_task_id)

                        if move_complete:
                            logger.info(f"Robot successfully reached marker {target_marker}")

                            # if target_marker is CD, skip taking photos
                            if target_marker == "CD":
                                logger.info("Skipping photo taking at CD")
                            else:
                                # take photos at the target marker
                                logger.info(f"Taking photos at marker {target_marker}")
                                time.sleep(2)  # Give some time for the robot to stabilize at the marker

                                marker_config = get_marker_config_by_short(target_marker)
                                photo_position = marker_config.mid if marker_config else target_marker
                                photo_result = app.camera_control.take_photo_all_cameras(position_info=photo_position, timestamp=timestamp)
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
                            
                    if not move_success:
                        if target_marker == "CD":
                            status = _status_after_cleanup_failure(status)
                            logger.error(
                                f"Inventory work finished but failed to return to CD after {max_retries} attempts"
                            )
                            break
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

                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.move_to_marker(target_marker)
                        
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
                        move_task_id = (move_result.get('results') or {}).get('task_id')
                        move_complete = wait_for_robot_move(app.robot_control, target_marker, expected_task_id=move_task_id)

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
                        if target_marker == "CD":
                            status = _status_after_cleanup_failure(status)
                            logger.error(
                                f"Inventory video work finished but failed to return to CD after {max_retries} attempts"
                            )
                            break
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
                        move_result = app.robot_control.move_to_marker(target_marker)
                        
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
                        move_task_id = (move_result.get('results') or {}).get('task_id')
                        move_complete = wait_for_robot_move(app.robot_control, target_marker, expected_task_id=move_task_id)

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
                status = TASK_STATUS_FAILED
                raise Exception(f"Unknown action type: {task.action}")
            
            if status == TASK_STATUS_INPROGRESS:
                status = TASK_STATUS_COMPLETED
        except Exception as e:
            status = TASK_STATUS_FAILED
            logger.error(f"Error executing task {task_id}: {str(e)}")
            # 安全降柱：只在升降柱确实升起过的情况下执行
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
        'ROBOT_BASE_URL': str(current_app.config['ROBOT_BASE_URL']),
        'ROBOT_API_TIMEOUT': str(current_app.config['ROBOT_API_TIMEOUT']),
        'FTP_HOST': str(current_app.config.get('FTP_HOST', '')),
        'FTP_PORT': int(current_app.config.get('FTP_PORT', '')),
        'FTP_USER': str(current_app.config.get('FTP_USER', '')),
        'FTP_PASS': str(current_app.config.get('FTP_PASS', '')),
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
            'ROBOT_PORT', 'ROBOT_BASE_URL', 'ROBOT_API_TIMEOUT',
            'FTP_HOST', 'FTP_PORT', 'FTP_USER', 'FTP_PASS',
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

        robot_ip = str(data.get('ROBOT_IP', '')).strip()
        robot_port = int(data.get('ROBOT_PORT', 0))
        if not robot_ip:
            raise ValueError("机器人IP不能为空")
        if not (1 <= robot_port <= 65535):
            raise ValueError("机器人端口必须在 1 到 65535 之间")
        data['ROBOT_IP'] = robot_ip
        data['ROBOT_PORT'] = str(robot_port)
        data['ROBOT_BASE_URL'] = f"http://{robot_ip}:{robot_port}"

        if not str(data.get('ROBOT_BASE_URL', '')).startswith(('http://', 'https://')):
            raise ValueError("机器人REST地址必须以 http:// 或 https:// 开头")

        timeout_value = float(data.get('ROBOT_API_TIMEOUT', 0))
        ftp_port = int(data.get('FTP_PORT', 0))
        if not (1 <= timeout_value <= 120):
            raise ValueError("机器人接口超时必须在 1 到 120 秒之间")
        if not (1 <= ftp_port <= 65535):
            raise ValueError("FTP端口必须在 1 到 65535 之间")
        if not str(data.get('FTP_HOST', '')).strip():
            raise ValueError("FTP服务器不能为空")
        if not str(data.get('FTP_USER', '')).strip():
            raise ValueError("FTP用户名不能为空")
        
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
            'CAMERA_POWERLINE_FREQ': (1, 2)
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
            set_key(env_path, key, str(value))
        
        # 重新加载环境变量以立即生效
        load_dotenv(env_path, override=True)
        current_app.config['ROBOT_IP'] = data.get('ROBOT_IP', current_app.config['ROBOT_IP'])
        current_app.config['ROBOT_PORT'] = int(data.get('ROBOT_PORT', current_app.config['ROBOT_PORT']))
        current_app.config['ROBOT_BASE_URL'] = data.get('ROBOT_BASE_URL', current_app.config['ROBOT_BASE_URL'])
        current_app.config['ROBOT_API_TIMEOUT'] = float(data.get('ROBOT_API_TIMEOUT', current_app.config['ROBOT_API_TIMEOUT']))
        current_app.config['FTP_HOST'] = data.get('FTP_HOST', current_app.config['FTP_HOST'])
        current_app.config['FTP_PORT'] = int(data.get('FTP_PORT', current_app.config['FTP_PORT']))
        current_app.config['FTP_USER'] = data.get('FTP_USER', current_app.config['FTP_USER'])
        current_app.config['FTP_PASS'] = data.get('FTP_PASS', current_app.config['FTP_PASS'])
        if hasattr(current_app, 'robot_control'):
            current_app.robot_control.base_url = current_app.config['ROBOT_BASE_URL'].rstrip('/')
            current_app.robot_control.timeout = current_app.config['ROBOT_API_TIMEOUT']
        
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


@bp.route('/api/settings/ftp-test', methods=['POST'])
@login_required
def test_ftp_settings():
    """Test FTP connection using submitted settings without saving them."""
    ftp = None
    try:
        data = request.get_json(silent=True) or {}
        host = str(data.get('FTP_HOST', '')).strip()
        port = int(data.get('FTP_PORT', 21))
        username = str(data.get('FTP_USER', '')).strip()
        password = str(data.get('FTP_PASS', ''))

        if not host:
            raise ValueError("FTP服务器不能为空")
        if not (1 <= port <= 65535):
            raise ValueError("FTP端口必须在 1 到 65535 之间")
        if not username:
            raise ValueError("FTP用户名不能为空")

        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(username, password)
        current_dir = ftp.pwd()
        ftp.voidcmd("NOOP")

        return jsonify({
            "status": "OK",
            "message": f"FTP连接测试成功，当前目录: {current_dir}"
        })
    except Exception as e:
        logger.error(f"FTP connection test failed: {str(e)}")
        return jsonify({
            "status": "ERROR",
            "message": f"FTP连接测试失败: {str(e)}"
        }), 500
    finally:
        if ftp:
            try:
                ftp.quit()
            except Exception:
                ftp.close()


@bp.route('/api/robot/recharge', methods=['POST'])
def robot_recharge():
    """机器人充电API"""
    try:
        robot_control = current_app.robot_control
        status = robot_control.get_status()
        results = status.get('results', {}) if status else {}
        current_floor_key = (results.get('current_building') or '', results.get('current_floor') or '')

        cd_markers = MarkerConfig.query.filter(MarkerConfig.mid_short.ilike('CD%')).all()
        if not cd_markers:
            return jsonify({
                "status": "ERROR",
                "message": "未找到充电点位，请先同步机器人点位配置",
                "results": None
            }), 400

        same_floor_cds = [
            marker for marker in cd_markers
            if (marker.building or '', marker.floor or '') == current_floor_key
        ]
        candidates = same_floor_cds or cd_markers
        candidates.sort(key=lambda m: m.mid_short)
        target_marker = candidates[0].mid_short

        if results.get('move_target') == target_marker and results.get('move_status') == 'succeeded':
            return jsonify({
                "status": "OK",
                "message": f"Already at charging station ({target_marker})",
                "results": results
            })

        result = robot_control.move_to_marker(target_marker)
        
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
        "estop_state": results.get("estop_state"),
        "estop_state_source": results.get("estop_state_source", ""),
        "estop_state_error": results.get("estop_state_error", ""),
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
