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

@bp.route('/photos')
@login_required
def photos_page():
    """照片管理页面"""
    return render_template('photos.html')

@bp.route('/marker-config')
@login_required
def marker_config_page():
    """标记点位配置页面"""
    return render_template('marker_config.html')
    return render_template('marker_config.html')

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
        result = camera_control.take_photo_all_cameras(position_info=position_info)
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
            # move lift to configured height position before starting the task
            if app.lift:
                logger.info("Moving lift to configured height position...")
                if not move_lift_to_configured_height():
                    raise Exception("Failed to move lift to configured height")
                time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))  # wait for lift to reach position
            else:
                logger.error("Lift control not initialized, please check")
                raise Exception("Lift control not initialized, please check")


            if task.action == 0:  # 拍照
                logger.info("Starting movement through markers for photo task ......")
                current_marker_index = 0
                while current_marker_index < len(marker_list):
                    target_marker = marker_list[current_marker_index]
                    logger.info(f"Moving to target marker: {target_marker} (sequence {current_marker_index+1}/{len(marker_list)})")

                    # Check if next marker is CD and lift needs to be lowered
                    if current_marker_index == len(marker_list) - 2:  # Second last marker (before CD)
                        logger.info("Next marker is CD, moving lift to position one...")
                        app.lift.move_to_position_one()
                        # time.sleep(current_app.config.get('LIFT_WAIT_TIME', 0))


                    # Try moving up to 3 times
                    max_retries = 3
                    retry_count = 0
                    move_success = False
                    
                    while retry_count < max_retries and not move_success:
                        move_result = app.robot_control.send_command(f"/api/move?marker={target_marker}")
                        
                        if not move_result:
                            logger.error(f"Failed to get response when moving to {target_marker} (attempt {retry_count + 1})")
                            retry_count += 1
                            time.sleep(1)
                            continue
                            
                        logger.info(f"Movement result: {move_result}")

                        # Wait for the robot to finish moving, monitoring the status
                        move_complete = False
                        status_checks = 0
                        max_status_checks = 30  # 30 second timeout
                        
                        while not move_complete and status_checks < max_status_checks:
                            robot_status = app.robot_control.send_command("/api/robot_status")
                            
                            if not robot_status:
                                logger.warning(f"Failed to get robot status (check {status_checks + 1})")
                                status_checks += 1
                                time.sleep(1)
                                continue
                                
                            logger.debug(f"Robot status: {robot_status}")
                            
                            if robot_status.get('status') == 'OK':
                                results = robot_status.get('results', {})
                                actual_marker = results.get('move_target')
                                move_status = results.get('move_status')
                                
                                if move_status == 'succeeded' and actual_marker == target_marker:
                                    logger.info(f"Robot successfully reached marker {target_marker}")

                                    # take photos at the target marker
                                    logger.info(f"Taking photos at marker {target_marker}")
                                    time.sleep(1)  # Give some time for the robot to stabilize at the marker
                                    
                                    photo_result = app.camera_control.take_photo_all_cameras(position_info=target_marker)
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
                                    move_complete = True
                                    current_marker_index += 1  # Only advance to next marker after confirmed success
                                elif move_status in ['failed', 'canceled']:
                                    raise Exception(f"Movement {move_status} at {target_marker}")
                            else:
                                status_checks += 1
                                time.sleep(1)
                                
                        if not move_complete:
                            logger.warning(f"Movement to {target_marker} not completed (attempt {retry_count + 1})")
                            retry_count += 1
                            
                    if not move_success:
                        raise Exception(f"Failed to move to {target_marker} after {max_retries} attempts")

            elif task.action == 1:  # 录像
                pass
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
                        
                        if not move_result:
                            logger.error(f"Failed to get response when moving to {target_marker} (attempt {retry_count + 1})")
                            retry_count += 1
                            time.sleep(1)
                            continue
                            
                        logger.info(f"Movement result: {move_result}")

                        # Wait for the robot to finish moving, monitoring the status
                        move_complete = False
                        status_checks = 0
                        max_status_checks = 30  # 30 second timeout
                        
                        while not move_complete and status_checks < max_status_checks:
                            robot_status = app.robot_control.send_command("/api/robot_status")
                            
                            if not robot_status:
                                logger.warning(f"Failed to get robot status (check {status_checks + 1})")
                                status_checks += 1
                                time.sleep(1)
                                continue
                                
                            logger.debug(f"Robot status: {robot_status}")
                            
                            if robot_status.get('status') == 'OK':
                                results = robot_status.get('results', {})
                                actual_marker = results.get('move_target')
                                move_status = results.get('move_status')
                                
                                if move_status == 'succeeded' and actual_marker == target_marker:
                                    logger.info(f"Robot successfully reached marker {target_marker}")
                                    move_success = True
                                    move_complete = True
                                    current_marker_index += 1  # Only advance to next marker after confirmed success
                                elif move_status in ['failed', 'canceled']:
                                    raise Exception(f"Movement {move_status} at {target_marker}")
                            else:
                                status_checks += 1
                                time.sleep(1)
                                
                        if not move_complete:
                            logger.warning(f"Movement to {target_marker} not completed (attempt {retry_count + 1})")
                            retry_count += 1
                            
                    if not move_success:
                        raise Exception(f"Failed to move to {target_marker} after {max_retries} attempts")
            else:
                status = 4
                raise Exception(f"Unknown action type: {task.action}")
            
            if status == 1:
                status = 2
        except Exception as e:
            status = 4
            logger.error(f"Error executing task {task_id}: {str(e)}")
            # 确保在任何错误情况下升降柱都能回到安全位置
            try:
                if app.lift:
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
            if task_log:
                # task_log.status = status
                task_log.status = TASK_STATUS_COMPLETED  #2 force to completed
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
    """获取指定目录下的图片列表，支持分页和缩略图"""
    try:
        directory = request.args.get('directory', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 8))
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        thumbnails_dir = os.path.join(screenshots_dir, 'thumbnails')
        
        # 检查目录是否存在
        dir_path = os.path.join(screenshots_dir, directory) if directory else screenshots_dir
        if not os.path.exists(dir_path):
            logger.info(f"Directory does not exist: {dir_path}")
            return jsonify({
                'images': [],
                'count': 0,
                'directory': directory,
                'page': page,
                'page_size': page_size
            })

        images = []
        processed_files = set()  # 用于跟踪已处理的文件，避免重复
        
        # 递归遍历目录及其子目录
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    full_path = os.path.join(root, file)
                    
                    # 验证文件是否真实存在且未被处理过
                    if not os.path.isfile(full_path) or full_path in processed_files:
                        continue
                        
                    processed_files.add(full_path)
                    
                    try:
                        # 获取文件状态信息
                        file_stat = os.stat(full_path)
                        
                        # 计算相对路径
                        rel_path = os.path.relpath(full_path, screenshots_dir)
                        rel_dir = os.path.relpath(root, screenshots_dir)
                        
                        # 确保路径分隔符统一使用正斜杠
                        web_path = rel_path.replace(os.sep, '/')
                        
                        # 构建URL
                        thumb_path = os.path.join(thumbnails_dir, rel_dir, file)
                        if os.path.exists(thumb_path):
                            thumbnail_url = url_for('static', filename=f'screenshots/thumbnails/{web_path}')
                        else:
                            thumbnail_url = url_for('static', filename=f'screenshots/{web_path}')
                            
                        images.append({
                            'filename': file,
                            'directory': rel_dir,
                            'fullUrl': url_for('static', filename=f'screenshots/{web_path}'),
                            'thumbnailUrl': thumbnail_url,
                            'size': file_stat.st_size,
                            'timestamp': file_stat.st_mtime,
                            'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except (OSError, ValueError) as e:
                        logger.error(f"Error processing file {full_path}: {str(e)}")
                        continue

        # 按时间戳排序
        images.sort(key=lambda x: -x['timestamp'])
        
        # 分页处理
        total = len(images)
        start = (page - 1) * page_size
        end = start + page_size
        paged_images = images[start:end]

        return jsonify({
            'images': paged_images,
            'count': total,
            'directory': directory,
            'page': page,
            'page_size': page_size,
            'all_images': not directory  # 标记是否是获取所有图片
        })

    except Exception as e:
        logger.error(f"Error getting images in directory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get images: {str(e)}'
        }), 500


@bp.route('/api/photos/upload', methods=['POST'])
def upload_directory():
    """上传指定目录及其子目录下的所有图片到FTP服务器(保留目录结构)"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': '未指定目录'
            }), 400
        
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'目录不存在: {directory}'
            }), 404

        config = current_app.config
        uploaded_files = []
        
        if config.get('FTP_MOCK_MODE', False):
            # Mock mode - just simulate upload
            logger.info(f"模拟FTP上传(保留目录结构): {directory}")
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # 计算相对路径，保持目录结构
                        rel_path = os.path.relpath(root, dir_path)
                        uploaded_files.append({
                            'file': file,
                            'directory': rel_path if rel_path != '.' else '',
                            'status': 'success',
                            'message': 'Simulated upload successful'
                        })
            logger.info(f"模拟上传完成，共处理 {len(uploaded_files)} 个文件")
        else:
            # Real FTP upload with directory structure
            ftp = None
            try:
                # Connect to FTP server
                ftp = FTP()
                ftp.connect(config['FTP_HOST'], config['FTP_PORT'])
                ftp.login(config['FTP_USER'], config['FTP_PASS'])
                logger.info(f"已连接FTP服务器: {config['FTP_HOST']}")

                # 设置FTP根目录
                remote_base = config.get('FTP_BASE_DIR', '/pic')
                try:
                    # 先尝试进入目录
                    ftp.cwd(remote_base)
                except Exception as e:
                    logger.info(f"FTP根目录 {remote_base} 不存在，尝试创建")
                    try:
                        # 创建目录
                        ftp.mkd(remote_base)
                        ftp.cwd(remote_base)
                        logger.info(f"成功创建并进入FTP根目录: {remote_base}")
                    except Exception as mkdir_error:
                        logger.error(f"无法创建FTP根目录 {remote_base}: {str(mkdir_error)}")
                        return jsonify({
                            'status': 'ERROR',
                            'message': f'无法创建FTP根目录: {str(mkdir_error)}',
                            'uploaded_files': []
                        }), 500
                
                # 递归上传文件，保持目录结构
                for root, _, files in os.walk(dir_path):
                    # 计算相对路径
                    rel_path = os.path.relpath(root, dir_path)
                    if rel_path != '.':
                        # 在FTP服务器上创建子目录
                        current_remote_path = remote_base
                        for subdir in rel_path.split(os.sep):
                            try:
                                # 先尝试进入目录
                                ftp.cwd(subdir)
                                current_remote_path = os.path.join(current_remote_path, subdir)
                            except:
                                try:
                                    # 如果目录不存在则创建
                                    ftp.mkd(subdir)
                                    ftp.cwd(subdir)
                                    current_remote_path = os.path.join(current_remote_path, subdir)
                                except Exception as e:
                                    logger.error(f"创建FTP目录失败 {subdir}: {str(e)}")
                                    # 返回根目录继续尝试
                                    ftp.cwd(remote_base)
                                    continue
                        
                        # 上传当前目录下的所有图片
                        for file in files:
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                local_file = os.path.join(root, file)
                                try:
                                    with open(local_file, 'rb') as fp:
                                        ftp.storbinary(f'STOR {file}', fp)
                                    uploaded_files.append({
                                        'file': file,
                                        'directory': rel_path if rel_path != '.' else '',
                                        'status': 'success',
                                        'message': 'Upload successful'
                                    })
                                    logger.info(f"成功上传: {local_file}")
                                except Exception as e:
                                    error_msg = f"上传失败: {str(e)}"
                                    logger.error(f"{error_msg} - {local_file}")
                                    uploaded_files.append({
                                        'file': file,
                                        'directory': rel_path if rel_path != '.' else '',
                                        'status': 'failed',
                                        'error': error_msg
                                    })
                        
                        # 返回上级目录，为下一个子目录做准备
                        if rel_path != '.':
                            for _ in rel_path.split(os.sep):
                                ftp.cwd('..')
                    
            except Exception as ftp_error:
                logger.error(f"FTP connection error: {str(ftp_error)}")
                return jsonify({
                    'status': 'ERROR',
                    'message': f'FTP连接失败: {str(ftp_error)}',
                    'uploaded_files': uploaded_files
                }), 500
        
        return jsonify({
            'status': 'OK',
            'message': f'成功上传 {len(uploaded_files)} 个文件到 {directory}',
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
    logger.info("Received request to delete image")
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'ERROR',
                'message': 'No JSON data received'
            }), 400

        directory = data.get('directory', '')  # 允许空目录，表示根目录
        filename = data.get('filename')
        
        logger.info(f"Deleting image - Directory: {directory}, Filename: {filename}")

        if not filename:  # 只检查文件名是否存在
            return jsonify({
                'status': 'ERROR',
                'message': 'Filename is required'
            }), 400
        
        # 获取截图根目录，使用绝对路径
        # screenshots_dir = os.path.normpath('/home/bk/BOKU-SERVICE-HOME/bk-robot/static/screenshots')
        # logger.info(f"Screenshots base directory (absolute path): {screenshots_dir}")
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        screenshots_dir = os.path.normpath(screenshots_dir)
        logger.info(f"Screenshots base directory: {screenshots_dir}")


        # 优先检查日期子目录（如果文件名包含日期）
        file_path = None
        year_month_day = None
        
        # 尝试从文件名提取日期 (格式: YYYYMMDD)
        if 'Unknown-' in filename:
            year_month_day = filename.split('-')[2][:8]  # Extract from Unknown-CameraX-YYYYMMDD_HHMMSS
        else:
            try:
                # Handle both formats:
                # 1. CameraX-YYYYMMDD_HHMMSS.png
                # 2. M1-s2-c2-YYYYMMDD_HHMMSS.png
                if '-' in filename and '_' in filename:
                    # Split on underscore first to get the date part
                    date_part = filename.split('_')[0]
                    # Then get the last segment which contains the date
                    year_month_day = date_part.split('-')[-1][:8]
                else:
                    year_month_day = filename.split('_')[1][:8]  # Fallback to original format
            except IndexError:
                pass
        
        logger.info(f"Extracted date from filename: {year_month_day}")

        # 确保screenshots目录存在
        if not os.path.exists(screenshots_dir):
            logger.error(f"Screenshots directory does not exist: {screenshots_dir}")
            return jsonify({
                'status': 'ERROR',
                'message': f'Screenshots directory not found'
            }), 404
        
        # 如果找到日期且目录未指定，优先检查日期子目录
        if year_month_day and year_month_day.isdigit() and not directory:
            dated_dir = os.path.join(screenshots_dir, year_month_day)
            logger.info(f"Checking dated directory: {dated_dir}")
            if os.path.exists(dated_dir):
                dated_path = os.path.normpath(os.path.join(dated_dir, filename))
                logger.info(f"Checking file path: {dated_path}")
                if os.path.exists(dated_path):
                    file_path = dated_path
                    logger.info(f"Found file in dated directory: {file_path}")
                else:
                    # Also check root directory as fallback
                    root_path = os.path.normpath(os.path.join(screenshots_dir, filename))
                    if os.path.exists(root_path):
                        file_path = root_path
                        logger.info(f"Found file in root directory: {file_path}")
                    else:
                        logger.warning(f"File not found at path: {dated_path} or {root_path}")
            else:
                # Check root directory if dated directory doesn't exist
                root_path = os.path.normpath(os.path.join(screenshots_dir, filename))
                if os.path.exists(root_path):
                    file_path = root_path
                    logger.info(f"Found file in root directory: {root_path}")
                else:
                    logger.warning(f"Dated directory not found: {dated_dir} and file not in root")
        
        # 如果仍未找到文件路径，尝试其他位置
        if not file_path:
            if directory:
                file_path = os.path.normpath(os.path.join(screenshots_dir, directory, filename))
            else:
                file_path = os.path.normpath(os.path.join(screenshots_dir, filename))
        
        logger.info(f"Trying to delete file: {file_path}")
        logger.info(f"Full absolute path: {os.path.abspath(file_path)}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {os.path.abspath(file_path)}")
            return jsonify({
                'status': 'ERROR',
                'message': f'File not found: {filename} in directory {directory}',
                'full_path': os.path.abspath(file_path)
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
        
        # 先检查当前是否已在充电点
        status = robot_control.get_status()
        if status.get('results', {}).get('move_target') == 'CD' and \
           status.get('results', {}).get('move_status') == 'succeeded':
            return jsonify({
                "status": "OK",
                "message": "Already at charging station",
                "results": status.get('results', {})
            })
        
        # 如果不在充电点，则发送充电命令
        result = robot_control.recharge()
        
        return jsonify({
            "status": result.get("status", "ERROR"),
            "message": result.get("error_message", ""),
            "results": result.get("task_id", "")
        })
    except Exception as e:
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


@bp.route('/api/marker-config', methods=['GET', 'POST'])
@login_required
def api_marker_configs():
    """标记点位配置API"""
    if request.method == 'GET':
        search = request.args.get('search', '')
        query = MarkerConfig.query
        if search:
            query = query.filter(
                (MarkerConfig.mid.ilike(f'%{search}%')) |
                (MarkerConfig.mid_short.ilike(f'%{search}%'))
            )
        configs = query.all()
        return jsonify([{
            'id': c.id,
            'mid': c.mid,
            'mid_short': c.mid_short,
            'x': c.x,
            'y': c.y,
            'w': c.w,
            'h': c.h
        } for c in configs])
    
    data = request.json
    config = MarkerConfig(
        mid=data['mid'],
        mid_short=data['mid_short'],
        x=data['x'],
        y=data['y'],
        w=data['w'],
        h=data['h']
    )
    try:
        db.session.add(config)
        db.session.commit()
        return jsonify({
            'id': config.id,
            'message': 'Created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/api/marker-config/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def api_marker_config(id):
    """单个标记点位配置API"""
    config = MarkerConfig.query.get_or_404(id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(config)
            db.session.commit()
            return jsonify({'message': 'Deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    data = request.json
    try:
        config.mid = data['mid']
        config.mid_short = data['mid_short']
        config.x = data['x']
        config.y = data['y']
        config.w = data['w']
        config.h = data['h']
        db.session.commit()
        return jsonify({
            'id': config.id,
            'message': 'Updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/api/marker-config/clear', methods=['POST'])
@login_required
def clear_marker_configs():
    """清空所有点位配置"""
    try:
        num_deleted = db.session.query(MarkerConfig).delete()
        db.session.commit()
        return jsonify({
            'status': 'OK',
            'message': f'成功删除 {num_deleted} 个点位配置'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'message': f'清空点位失败: {str(e)}'
        }), 500

@bp.route('/api/marker-config/sync', methods=['POST'])
@login_required
def sync_marker_configs():
    """同步机器人点位配置"""
    try:
        # Check if we should use mock data
        # if current_app.config.get('MOCK_MARKER_DATA'):
        if False:
            result = {
                'type': 'response',
                'command': '/api/markers/query_list',
                'status': 'OK',
                'error_message': '',
                'results': {
                    'meeting_room1': {
                        'marker_name': '01020301041',
                        'pose': {'position': {'x': -8.58, 'y': 6.36}}
                    },
                    'meeting_room2': {
                        'marker_name': '01020301042', 
                        'pose': {'position': {'x': -8.58, 'y': 6.36}}
                    }
                }
            }
        else:
            # Call robot API to get marker list
            robot_control = current_app.robot_control
            result = robot_control.send_command("/api/markers/query_list")
        
        if result.get('status') != 'OK':
            return jsonify({
                'status': 'ERROR',
                'error_type': result.get('error_type', 'unknown_error'),
                'message': f'获取机器人点位失败: {result.get("error_message", "未知错误")}'
            }), 500

        # 清空现有点位
        db.session.query(MarkerConfig).delete()
        
               
        # 解析并添加新点位
        markers = result.get('results', {})
        count = 0
        for location_name, info in markers.items():
            marker_name = info.get('marker_name')
            if marker_name:
                # 创建简写名称（M1, M2, ...）
                if marker_name != 'CD':
                    count += 1
                    mid_short = f'M{count}'
                else:
                    mid_short = 'CD'
                    
                config = MarkerConfig(
                    mid=marker_name,
                    mid_short=mid_short,
                    x=0,
                    y=0,
                    w=0,
                    h=0
                )
                db.session.add(config)
        
        db.session.commit()
        return jsonify({
            'status': 'OK',
            'message': f'成功同步 {count+1} 个点位',
            'results': {
                'count': count+1,
                'markers': list(markers.keys())
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'error_type': 'database_error',
            'message': f'同步点位失败: {str(e)}',
            'details': 'Failed to update database with marker data'
        }), 500

def move_lift_to_configured_height():
    """Move the lift to the configured height position"""
    try:
        lift_height = os.getenv('LIFT_HEIGHT', 'L2')  # Default to L2 if not set
        
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

@bp.route('/api/photos/crop', methods=['POST'])
def crop_images():
    try:
        logger.info("开始处理裁剪请求")
        data = request.get_json()
        directory = data.get('directory')
        if not directory:
            logger.warning("目录参数为空")
            return jsonify({
                'success': False,
                'message': '目录参数不能为空',
                'processed_files': []
            })

        # 确保目录存在
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        logger.info(f"检查目录路径: {dir_path}")
        
        if not os.path.exists(dir_path):
            logger.error(f"目录不存在: {dir_path}")
            return jsonify({
                'success': False,
                'message': f'目录 {directory} 不存在，完整路径: {dir_path}',
                'processed_files': []
            })

        processed_files = []
        
        # 遍历目录中的所有图片文件
        for filename in os.listdir(dir_path):
            if not filename.endswith(('.png', '.jpg', '.jpeg')) or 'Unknown' in filename:
                continue

            # 解析文件名获取marker ID
            try:
                marker_id = filename.split('-')[0]  # 获取第一个划线前的部分作为marker ID
                
                # 查询marker_config表获取裁剪参数
                marker_config = MarkerConfig.query.filter_by(mid=marker_id).first()
                
                if not marker_config:
                    processed_files.append({
                        'file': filename,
                        'status': 'failed',
                        'error': f'找不到对应的marker配置: {marker_id}'
                    })
                    continue

                # 图片完整路径
                img_path = os.path.join(dir_path, filename)
                
                try:
                    from PIL import Image
                    logger.info(f"开始处理图片: {img_path}")
                    img = Image.open(img_path)

                    # 如果x,y,w,h都为0，则跳过裁剪但仍然保存新文件
                    if marker_config.x == 0 and marker_config.y == 0 and \
                       marker_config.w == 0 and marker_config.h == 0:
                        logger.info(f"配置参数全为0，跳过裁剪: {marker_id}")
                        new_img = img
                    else:
                        # 执行裁剪
                        logger.info(f"裁剪参数: x={marker_config.x}, y={marker_config.y}, w={marker_config.w}, h={marker_config.h}")
                        new_img = img.crop((
                            marker_config.x,  # 左
                            marker_config.y,  # 上
                            marker_config.x + marker_config.w,  # 右
                            marker_config.y + marker_config.h   # 下
                        ))

                    # 生成新的文件名
                    base_name = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    new_filename = f"{base_name}-crop{ext}"
                    new_path = os.path.join(dir_path, new_filename)

                    # 保存新图片
                    logger.info(f"保存裁剪后的图片: {new_path}")
                    new_img.save(new_path)
                    logger.info(f"成功保存裁剪后的图片: {new_path}")

                    # 准备处理结果
                    result = {
                        'file': filename,
                        'status': 'success',
                        'new_file': new_filename
                    }

                    # 如果是裁剪后的文件，进行分类移动
                    if new_filename.endswith('-crop.png'):
                        try:
                            # 解析文件名各部分
                            parts = base_name.split('-')  # 不包含-crop.png部分
                            if len(parts) >= 4:
                                first_part = parts[0]  # 例如：01020301041
                                second_part = parts[1]  # 例如：s1
                                time_part = parts[3]    # 例如：1751422638
                                
                                # 构建 FOLDER1：01 + 前10位 + 第二个字段第2个字符补0
                                if len(first_part) >= 10 and len(second_part) >= 2:
                                    prefix_10 = first_part[:10]  # 取前10位
                                    second_char = second_part[1]  # 取第二个字符
                                    folder1 = f"01{prefix_10}{second_char.zfill(2)}"  # 补0确保两位
                                    
                                    # 构建文件名：第一个字段的最后一位
                                    if len(first_part) > 0:
                                        new_filename_final = f"{first_part[-1]}.png"
                                        
                                        # 构建新的目录结构：pic/[FOLDER1]/book/[TIME]/[FILENAME].png
                                        new_dir = os.path.join(screenshots_dir, 'pic', folder1, 'book', time_part)
                                        new_file_path = os.path.join(new_dir, new_filename_final)
                                        
                                        # 创建目录（如果不存在）
                                        os.makedirs(new_dir, exist_ok=True)
                                        
                                        # 移动文件
                                        logger.info(f"移动文件到新位置: {new_file_path}")
                                        shutil.move(new_path, new_file_path)
                                        logger.info(f"成功移动文件到: {new_file_path}")
                                        
                                        # 更新处理状态
                                        result['moved_to'] = os.path.relpath(new_file_path, screenshots_dir)
                        except Exception as e:
                            logger.error(f"移动文件时出错: {str(e)}", exc_info=True)
                            result['move_error'] = str(e)
                    
                    processed_files.append(result)
                except Exception as e:
                    logger.error(f"处理图片时出错: {str(e)}", exc_info=True)
                    processed_files.append({
                        'file': filename,
                        'status': 'failed',
                        'error': str(e)
                    })

            except Exception as e:
                processed_files.append({
                    'file': filename,
                    'status': 'failed',
                    'error': str(e)
                })

        # 统计处理结果
        success_count = len([f for f in processed_files if f['status'] == 'success'])
        fail_count = len([f for f in processed_files if f['status'] == 'failed'])

        logger.info(f"裁剪处理完成: {success_count} 成功, {fail_count} 失败")
        return jsonify({
            'success': True,
            'message': f'处理完成: {success_count} 成功, {fail_count} 失败',
            'processed_files': processed_files
        })

    except Exception as e:
        logger.error(f"裁剪过程发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'处理过程中发生错误: {str(e)}',
            'processed_files': []
        }), 500  # 添加500状态码表示服务器错误

@bp.route('/ipcams')
@login_required
def ipcams():
    """网络摄像头仪表盘页面，支持多行和逗号分隔的 CAMERA_URLS"""
    # 获取摄像头URL配置
    # camera_urls_raw = current_app.config.get('CAMERA_URLS', '')
    cameras = []
    urls_str = os.environ.get('CAMERA_URLS', '')
    # First split by newlines, then split each line by commas
    camera_urls = []
    for line in urls_str.splitlines():
        # camera_urls.extend([url.strip() for url in line.split(',') if url.strip()])
        print(line)
        # rtsp://admin@192.168.10.21:554/user=admin&password=&channel=1&stream=0.sdp?
        cameras.append({
            'name': f'{ line.split("@")[1].split(":")[0] }',
            'url': line
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