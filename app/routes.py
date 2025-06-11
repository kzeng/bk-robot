from flask import render_template, jsonify, request, Blueprint, current_app, redirect, url_for, send_from_directory, flash, session, flash, session
import hashlib
from functools import wraps
import json
from app.models import Task, TaskLog
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
from .lift_control import Lift
from dotenv import load_dotenv, set_key
from loguru import logger


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
            "title": "5.点位功能接口",
            "url": "#",
            "cmd": "/api/markers/insert"
        },
        {
            "title": "6.机器人直接控制指令",
            "url": "#",
            "cmd": "/api/joy_control"
        },
        {
            "title": "7.机器人急停控制指令",
            "url": "#",
            "cmd": "/api/estop"
        },
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
        {
            "title": "10.机器人主动通知",
            "url": "#",
            "cmd": "/api/xxxxxxxxxxx"
        },
        {
            "title": "11.设置参数",
            "url": "#",
            "cmd": "/api/set_params"
        },
        {
            "title": "12.获取参数",
            "url": "#",
            "cmd": "/api/get_params"
        },
        {
            "title": "13.无线网络接口",
            "url": "#",
            "cmd": "/api/wifi/list"
        },
        {
            "title": "14.地图接口",
            "url": "#",
            "cmd": "/api/map/list"
        },
        {
            "title": "15.关机重启接口",
            "url": "#",
            "cmd": "/api/shutdown"
        },
        {
            "title": "16.软件更新接口",
            "url": "#",
            "cmd": "/api/software/get_version"
        },
        {
            "title": "17.设置灯带接口",
            "url": "#",
            "cmd": "/api/LED/set_luminance"
        },
        {
            "title": "18.自诊断接口",
            "url": "#",
            "cmd": "/api/diagnosis/get_result"
        },
        {
            "title": "19.获取电源状态接口",
            "url": "#",
            "cmd": "/api/get_power_status"
        },
        {
            "title": "20.获取机器人全局路径接口",
            "url": "#",
            "cmd": "/api/get_planned_path"
        },
        {
            "title": "21.获取电梯状态接口",
            "url": "#",
            "cmd": "/api/lift_status"
        },
        {
            "title": "22.获取两点间路径接口",
            "url": "#",
            "cmd": "/api/make_plan"
        },
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

@bp.route('/photos')
@login_required
def photos_page():
    """照片管理页面"""
    return render_template('photos.html')

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
    
    camera_control = current_app.camera_control
    
    try:
        # Only connect if not already connected
        if hasattr(camera_control, 'connected') and not camera_control.connected:
            result = camera_control.connect()
            if result["status"] != "OK":
                return jsonify(result), 500
                
        # Take screenshots
        result = camera_control.take_screenshot_all_cameras(position_info=position_info)
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
    tasks = Task.query.order_by(Task.task_id.desc()).all()
    return jsonify([{
        'task_id': task.task_id,
        'marker': task.marker,
        'action': task.action,
        'create_at': task.create_at.strftime("%Y-%m-%d %H:%M:%S") if task.create_at else None,
        'update_at': task.update_at.strftime("%Y-%m-%d %H:%M:%S") if task.update_at else None,
        'description': task.description
    } for task in tasks])



@bp.route('/api/tasks', methods=['POST'])
@bp.route('/tasks', methods=['POST'])
def create_task():
    """创建新盘点任务"""
    try:
        # Log request headers and raw data
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Content-Type: {request.content_type}")
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
    task = Task.query.get_or_404(task_id)
    # 获取最新的任务日志
    task_log = TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.start_time.desc()).first()
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
    
    对于拍照任务(0)：
    - 原始行为：通过单个API调用移动机器人到所有标记点，监控状态并在每个标记点拍照
    - 新行为：将标记点列表拆分为连续的两点组合（例如[m1,m2,m3,m4] -> [m1,m2], [m2,m3], [m3,m4]）
                  顺序执行每个移动操作，在每次移动结束后拍照
        - 优势：简化了机器人状态监控逻辑，因为只需要关注单次移动完成信号
        
    Args:
        task_id (int): 要执行的任务ID
            
    Returns:
        JSON响应包含:
        - status: 'OK' 或 'ERROR'
        - message: 操作结果描述
        - task_log_id: 任务日志ID用于跟踪执行过程
    """
    task = Task.query.get_or_404(task_id)
    
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

def async_run_task(app, task_id):
    """在后台线程中执行任务"""
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return
            
        marker_list = task.marker.split(',') if task.marker else []
        marker_list = [marker.strip() for marker in marker_list if marker.strip()]
        if not marker_list:
            # 获取最新的任务日志并更新状态
            task_log = TaskLog.query.filter_by(task_id=task_id)\
                                  .order_by(TaskLog.start_time.desc())\
                                  .first()
            if task_log:
                task_log.status = 4  # 任务失败
                task_log.end_time = datetime.now()
                db.session.commit()
            return
            
        status = 1  # 1 = in progress
        file_paths = []
        task_log = TaskLog.query.filter_by(task_id=task_id)\
                               .order_by(TaskLog.start_time.desc())\
                               .first()
        
        try:
            if task.action == 0:  # 拍照
                subtasks = [(marker_list[i], marker_list[i+1]) for i in range(len(marker_list)-1)]
                completed_markers = set()
                for start_marker, end_marker in subtasks:
                    app.logger.info(f"Starting movement from {start_marker} to {end_marker}")
                    move_result = app.robot_control.send_command(f"/api/move?marker={start_marker},{end_marker}")

                    # HERE: Check if the move_result is vali. IMPORTANT!!!!!!!!!!!!! KZENG
                    if move_result.get('status') != 'OK':
                        raise Exception(f"Failed to start movement: {move_result.get('message')}")
                    while True:
                        robot_status = app.robot_control.send_command("/api/robot_status")
                        if robot_status.get('status') != 'OK':
                            raise Exception("Failed to get robot status")
                        results = robot_status.get('results', {})
                        move_status = results.get('move_status')
                        if move_status == 'succeeded':
                            logger.info(f"Robot reached marker {end_marker}, taking photos")
                            photo_result = app.obs_control.take_screenshot_all_cameras(position_info=end_marker)
                            if photo_result.get('status') == 'OK':
                                new_files = photo_result.get('file_paths', [])
                                if new_files:
                                    file_paths.extend(new_files)
                                    logger.info(f"Saved {len(new_files)} photos at {end_marker}")
                                else:
                                    status = 3
                                    logger.warning(f"No photos saved at {end_marker}")
                            else:
                                status = 3
                                logger.warning(f"Photo failed at {end_marker}: {photo_result.get('message')}")
                            completed_markers.add(end_marker)
                            break
                        elif move_status in ['failed', 'canceled']:
                            status = 3
                            logger.warning(f"Movement to {end_marker} {move_status}")
                            break
                        time.sleep(1)
            elif task.action == 1:  # 录像
                markers = ','.join(marker_list)
                move_result = app.robot_control.send_command(f"/api/move?marker={markers}")
                if move_result.get('status') != 'OK':
                    raise Exception(f"Failed to start movement: {move_result.get('message')}")
                logger.info("Started movement through markers for recording task")
                recording_started = False
                last_marker = marker_list[-1]
                while True:
                    robot_status = app.robot_control.send_command("/api/robot_status")
                    if robot_status.get('status') != 'OK':
                        raise Exception("Failed to get robot status")
                    results = robot_status.get('results', {})
                    current_target = results.get('move_target')
                    move_status = results.get('move_status')
                    if not recording_started and move_status == 'succeeded':
                        logger.info("Robot reached first marker, starting recording")
                        start_result = app.obs_control.start_recording()
                        if start_result.get('status') != 'OK':
                            status = 3
                            logger.warning(f"Start recording failed: {start_result.get('message')}")
                        recording_started = True
                    if (current_target == last_marker and move_status == 'succeeded') or \
                       move_status in ['failed', 'canceled']:
                        if recording_started:
                            logger.info("Stopping recording")
                            stop_result = app.obs_control.stop_recording()
                            if stop_result.get('status') != 'OK':
                                status = 3
                                logger.warning(f"Stop recording failed: {stop_result.get('message')}")
                            else:
                                file_paths.extend(stop_result.get('file_paths', []))
                        break
                    time.sleep(1)
            elif task.action == 99:  # 仅是移动
                subtasks = [(marker_list[i], marker_list[i+1]) for i in range(len(marker_list)-1)]
                for start_marker, end_marker in subtasks:
                    logger.info(f"Moving from {start_marker} to {end_marker} (move only, no photo/video)")
                    move_result = app.robot_control.send_command(f"/api/move?marker={start_marker},{end_marker}")
                    if move_result.get('status') != 'OK':
                        raise Exception(f"Failed to start movement: {move_result.get('message')}")
                    while True:
                        robot_status = app.robot_control.send_command("/api/robot_status")
                        if robot_status.get('status') != 'OK':
                            raise Exception("Failed to get robot status")
                        results = robot_status.get('results', {})
                        move_status = results.get('move_status')
                        if move_status == 'succeeded':
                            logger.info(f"Robot reached marker {end_marker}")
                            break
                        elif move_status in ['failed', 'canceled']:
                            status = 3
                            logger.warning(f"Movement to {end_marker} {move_status}")
                            break
                        time.sleep(1)
            else:
                status = 4
                raise Exception(f"Unknown action type: {task.action}")
            if status == 1:
                status = 2
        except Exception as e:
            status = 4
            logger.error(f"Error executing task {task_id}: {str(e)}")
            if task.action == 1 and 'recording_started' in locals() and recording_started:
                try:
                    stop_result = app.obs_control.stop_recording()
                    if stop_result.get('status') == 'OK':
                        file_paths.extend(stop_result.get('file_paths', []))
                except Exception as stop_error:
                    logger.error(f"Error stopping recording after failure: {stop_error}")
        finally:
            try:
                if task_log:
                    task_log.status = status
                    task_log.end_time = datetime.now()
                    task_log.file_count = len(file_paths)
                    task_log.file_paths = json.dumps(file_paths)
                    db.session.commit()
                    logger.info(f"Task log updated - Status: {status}, Files: {len(file_paths)}")
            except Exception as e:
                logger.error(f"Failed to update task log: {str(e)}")

# @bp.route('/api/tasks/<int:task_id>/run', methods=['POST'])
# def run_task(task_id):
#     """启动盘点任务执行"""
#     task = Task.query.get_or_404(task_id)
    
#     # 创建初始任务日志
#     task_log = TaskLog(
#         task_id=task_id,
#         marker=task.marker,
#         action=task.action,
#         start_time=datetime.now(),
#         status=1,  # 1 = in progress
#         file_count=0,
#         file_paths='[]'
#     )
#     db.session.add(task_log)
#     db.session.commit()
    
#     # 启动后台线程执行任务
#     app = current_app._get_current_object()  # 获取真实的app对象
#     thread = Thread(target=async_run_task, args=(app, task_id))
#     thread.daemon = True  # 设置为守护线程
#     thread.start()
    
#     return jsonify({
#         'status': 'OK',
#         'message': 'Task started successfully',
#         'task_log_id': task_log.log_id
#     })

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
    return jsonify({
        'log_id': log.log_id,
        'task_id': log.task_id,
        'marker': log.marker,
        'action': log.action,
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
    baudrate = 9600
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


# Photo management API routes ##########################################################################
@bp.route('/api/photos/directories', methods=['GET'])
def get_photo_directories():
    """获取所有图片目录"""
    try:
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        
        if not os.path.exists(screenshots_dir):
            return jsonify({
                'directories': [],
                'count': 0
            })
        
        # 获取所有子目录
        all_items = os.listdir(screenshots_dir)
        directories = [d for d in all_items 
                     if os.path.isdir(os.path.join(screenshots_dir, d))]
        
        # 添加调试输出：打印找到的目录
        logger.info(f"Found directories: {directories}")
        
        # 按目录名称排序（通常是日期格式，如YYYYMMDD）
        directories.sort(reverse=True)
        
        return jsonify({
            'directories': directories,
            'count': len(directories)
        })
    except Exception as e:
        logger.error(f"Error getting photo directories: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get directories: {str(e)}'
        }), 500


@bp.route('/api/photos/images', methods=['GET'])
def get_images_in_directory():
    """获取指定目录下的图片列表"""
    try:
        directory = request.args.get('directory', '')
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        
        # 添加调试日志：打印基础目录和请求的目录
        logger.info(f"Getting images - Base directory: {screenshots_dir}")
        logger.info(f"Getting images - Requested directory: {directory}")
        
        # 如果没有指定目录，则返回所有图片
        if not directory:
            images = []
            for root, dirs, files in os.walk(screenshots_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        rel_path = os.path.relpath(root, screenshots_dir)
                        full_path = os.path.join(root, file)
                        
                        # 添加调试日志：找到的文件路径
                        logger.info(f"Found file: {full_path}")
                        
                        # 获取相对路径用于构造URL
                        if rel_path == '.':
                            thumbnail_url = url_for('static', filename=f'screenshots/{file}')
                            full_url = url_for('static', filename=f'screenshots/{file}')
                        else:
                            thumbnail_url = url_for('static', filename=f'screenshots/{rel_path}/{file}')
                            full_url = url_for('static', filename=f'screenshots/{rel_path}/{file}')
                        
                        images.append({
                            'filename': file,
                            'directory': rel_path,
                            'fullUrl': full_url,
                            'thumbnailUrl': thumbnail_url,
                            'size': os.path.getsize(full_path)
                        })
            # 按时间倒序排列（最新的在前）
            images.sort(key=lambda x: -os.path.getmtime(os.path.join(screenshots_dir, x['directory'], x['filename'])))
            return jsonify({
                'images': images,
                'count': len(images),
                'all_images': True
            })
        
        # 添加调试日志：检查目录是否存在
        dir_path = os.path.join(screenshots_dir, directory)
        logger.info(f"Checking directory existence: {dir_path}")
        if not os.path.exists(dir_path):
            logger.info(f"Directory does not exist: {dir_path}")
            return jsonify({
                'images': [],
                'count': 0,
                'directory': directory
            })
        
        # 添加调试日志：列出目录中的所有内容
        all_items = os.listdir(dir_path)
        logger.info(f"All items in directory {dir_path}: {all_items}")
        
        # 获取指定目录下的图片
        images = []
        for file in os.listdir(dir_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                full_path = os.path.join(dir_path, file)
                
                # 确保文件确实存在
                if not os.path.exists(full_path):
                    logger.warning(f"File does not exist: {full_path}")
                    continue
                    
                # 添加调试日志：找到的文件路径
                logger.info(f"Found file in directory: {full_path}")
                
                # 构造正确的URL，修复Windows下反斜杠问题
                relative_path = os.path.join('screenshots', directory, file).replace('\\', '/')
                images.append({
                    'filename': file,
                    'directory': directory,
                    'fullUrl': url_for('static', filename=relative_path),
                    'thumbnailUrl': url_for('static', filename=relative_path),
                    'size': os.path.getsize(full_path),
                    'timestamp': os.path.getmtime(full_path)  # 添加时间戳用于排序
                })
        
        # 按时间倒序排列（最新的在前）
        images.sort(key=lambda x: -x['timestamp'])
        
        # 在返回数据前过滤，只保留与当前目录匹配的图片
        logger.info(f"Filtering images for directory: {directory}")
        filtered_images = [img for img in images if img['directory'] == directory]
        
        # 在返回数据前添加验证
        for image in filtered_images:
            if 'thumbnailUrl' not in image or 'fullUrl' not in image:
                logger.warning(f"Image data missing URL fields: {image}")
        
        return jsonify({
            'images': filtered_images,
            'count': len(filtered_images),
            'directory': directory
        })
    except Exception as e:
        logger.error(f"Error getting images in directory: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get images: {str(e)}'
        }), 500


@bp.route('/api/photos/upload', methods=['POST'])
def upload_directory():
    """上传指定目录下的所有图片到FTP服务器"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': 'No directory specified'
            }), 400
        
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'Directory not found: {directory}'
            }), 404

        config = current_app.config
        uploaded_files = []
        
        if config['FTP_MOCK_MODE']:
            # Mock mode - just simulate upload
            logger.info(f"Mock FTP upload from directory: {directory}")
            for file in os.listdir(dir_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    uploaded_files.append(file)
        else:
            # Real FTP upload
            try:
                with FTP() as ftp:
                    # Connect to FTP server
                    ftp.connect(config['FTP_HOST'], config['FTP_PORT'])
                    ftp.login(config['FTP_USER'], config['FTP_PASS'])
                    logger.info(f"Connected to FTP server: {config['FTP_HOST']}")

                    # Upload each file
                    for file in os.listdir(dir_path):
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            file_path = os.path.join(dir_path, file)
                            try:
                                with open(file_path, 'rb') as f:
                                    ftp.storbinary(f'STOR {file}', f)
                                uploaded_files.append(file)
                                logger.info(f"Uploaded {file} to FTP server")
                            except Exception as file_error:
                                logger.error(f"Error uploading {file}: {str(file_error)}")
                                continue
            except ftplib.all_errors as ftp_error:
                logger.error(f"FTP connection error: {str(ftp_error)}")
                return jsonify({
                    'status': 'ERROR',
                    'message': f'FTP connection failed: {str(ftp_error)}'
                }), 500
        
        return jsonify({
            'status': 'OK',
            'message': f'Successfully uploaded {len(uploaded_files)} files from {directory}',
            'directory': directory,
            'uploaded_files': uploaded_files
        })
    except Exception as e:
        logger.error(f"Error uploading directory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'ERROR',
            'message': f'Upload failed: {str(e)}'
        }), 500


@bp.route('/api/photos/delete_directory', methods=['POST'])
def delete_directory():
    """删除指定目录及其所有内容"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': 'No directory specified'
            }), 400
        

        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'Directory not found: {directory}'
            }), 404
        
        # 删除目录及其内容
        import shutil
        shutil.rmtree(dir_path)
        
        return jsonify({
            'status': 'OK',
            'message': f'Directory {directory} and its contents have been deleted',
            'directory': directory
        })
    except Exception as e:
        logger.error(f"Error deleting directory: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Delete operation failed: {str(e)}'
        }), 500


@bp.route('/api/photos/delete_image', methods=['POST'])
def delete_image():
    """删除指定目录下的单个图片文件"""
    logger.info("Received request to delete image.......")
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        filename = data.get('filename', '')
        
        logger.info(f"Directory: {directory}, Filename: {filename}")


        if not directory or not filename:
            return jsonify({
                'status': 'ERROR',
                'message': 'Directory or filename missing'
            }), 400
        
        screenshots_dir = os.path.join(current_app.root_path, 'static', 'screenshots')
        file_path = os.path.join(screenshots_dir, directory, filename)
        
        # 修复路径问题：使用项目根目录下的static目录
        # 修正方法：移除app目录层级
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        file_path = os.path.normpath(os.path.join(screenshots_dir, directory, filename))
        
        logger.info(f"Full file path: {file_path}")
        logger.info(f"File exists: {os.path.exists(file_path)}")

        
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'File not found: {filename} in directory {directory}'
            }), 404
        
        # 删除文件
        logger.info(f"Deleting file: {file_path}")
        os.remove(file_path)
        
        return jsonify({
            'status': 'OK',
            'message': f'File {filename} has been deleted from directory {directory}',
            'directory': directory,
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Delete operation failed: {str(e)}'
        }), 500


@bp.route('/api/photos/clear_all', methods=['POST'])
def clear_all_photos():
    """清空所有图片和目录"""
    try:
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        
        # 如果目录不存在，直接返回成功
        if not os.path.exists(screenshots_dir):
            return jsonify({
                'status': 'OK',
                'message': 'Screenshots directory does not exist, nothing to clear'
            })
        
        # 遍历目录中的所有文件和子目录
        for item in os.listdir(screenshots_dir):
            item_path = os.path.join(screenshots_dir, item)
            
            # 如果是文件，则直接删除
            if os.path.isfile(item_path):
                os.remove(item_path)
            # 如果是目录，则递归删除
            elif os.path.isdir(item_path):
                import shutil
                shutil.rmtree(item_path)
        
        return jsonify({
            'status': 'OK',
            'message': 'All photos and directories have been cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing all photos: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Clear operation failed: {str(e)}'
        }), 500

@bp.route('/static/screenshots/<path:filename>')
def serve_screenshots(filename):
    """Serve screenshots files"""
    screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
    return send_from_directory(screenshots_dir, filename)

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
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin':
            hashed_password = hashlib.sha1(password.encode()).hexdigest()
            if hashed_password == current_app.config['ADMIN_PASSWORD']:
                session['authenticated'] = True
                return redirect(url_for('main.index'))
        
        flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('authenticated', None)
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
        
        # 其他配置
        'ROBOT_IP': str(current_app.config['ROBOT_IP']),
        'ROBOT_PORT': str(current_app.config['ROBOT_PORT']),
        'OBS_WS_URL': str(current_app.config['OBS_WS_URL']),
        'OBS_PASSWORD': str(current_app.config['OBS_PASSWORD']),
        'USE_OPENCV': str(current_app.config['USE_OPENCV']).lower(),
        'ROBOT_MOCK_MODE': str(current_app.config['ROBOT_MOCK_MODE']).lower(),
        'FTP_MOCK_MODE': str(current_app.config.get('FTP_MOCK_MODE', 'false')).lower(),
        'FTP_HOST': str(current_app.config.get('FTP_HOST', '')),
        'FTP_PORT': str(current_app.config.get('FTP_PORT', '')),
        'FTP_USER': str(current_app.config.get('FTP_USER', '')),
        'FTP_PASS': str(current_app.config.get('FTP_PASS', '')),
        'LIFT_PORT': str(current_app.config.get('LIFT_PORT', '')),
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
            # 确保布尔值被正确处理
            if key in ['ROBOT_MOCK_MODE', 'USE_OPENCV', 'FTP_MOCK_MODE']:
                value = str(value).lower()  # 确保是小写的 'true' 或 'false'
            set_key(env_path, key, str(value))
        
        # 重新加载环境变量以立即生效
        load_dotenv(env_path, override=True)
        
        # 尝试更新相机参数
        if current_app.camera_control and hasattr(current_app.camera_control, 'update_camera_params'):
            camera_params = {k.lower().replace('camera_', ''): v for k, v in data.items() 
                           if k.startswith('CAMERA_') and k not in ['CAMERA_WIDTH', 'CAMERA_HEIGHT', 
                                                                   'CAMERA_FPS', 'CAMERA_BUFFER_SIZE']}
            # 获取第一个摄像头id
            camera_ids = list(getattr(current_app.camera_control, 'camera_controls', {}).keys())
            if camera_ids:
                camera_id = camera_ids[0]
                current_app.camera_control.update_camera_params(camera_id, camera_params)
        
        logger.info("Settings updated successfully")
        return jsonify({'status': 'OK', 'message': '设置已保存'})
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500
