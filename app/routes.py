from flask import render_template, jsonify, request, Blueprint, current_app, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from app.models import Task, TaskLog
from app import db
from datetime import datetime, timezone, timedelta
import asyncio
import os
from functools import wraps
import time


def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

bp = Blueprint('main', __name__)

robot_all_apis_options = [
        {
            "title": "1.机器人移动功能",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#1%E6%9C%BA%E5%99%A8%E4%BA%BA%E7%A7%BB%E5%8A%A8%E5%8A%9F%E8%83%BD",
            "cmd": "/api/move"
        },
        {
            "title": "2.移动取消功能",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#2%E7%A7%BB%E5%8A%A8%E5%8F%96%E6%B6%88%E5%8A%9F%E8%83%BD",
            "cmd": "/api/move/cancel"
        },
        {
            "title": "3.获取机器人当前全局状态",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#3%E8%8E%B7%E5%8F%96%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%BD%93%E5%89%8D%E5%85%A8%E5%B1%80%E7%8A%B6%E6%80%81",
            "cmd": "/api/robot_status"
        },
        {
            "title": "4.获取机器人信息接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#4%E8%8E%B7%E5%8F%96%E6%9C%BA%E5%99%A8%E4%BA%BA%E4%BF%A1%E6%81%AF%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/robot_info"
        },
        {
            "title": "5.点位功能接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#5%E7%82%B9%E4%BD%8D%E5%8A%9F%E8%83%BD%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/markers/insert"
        },
        {
            "title": "6.机器人直接控制指令",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#6%E6%9C%BA%E5%99%A8%E4%BA%BA%E7%9B%B4%E6%8E%A5%E6%8E%A7%E5%88%B6%E6%8C%87%E4%BB%A4",
            "cmd": "/api/joy_control"
        },
        {
            "title": "7.机器人急停控制指令",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#7%E6%9C%BA%E5%99%A8%E4%BA%BA%E6%80%A5%E5%81%9C%E6%8E%A7%E5%88%B6%E6%8C%87%E4%BB%A4",
            "cmd": "/api/estop"
        },
        {
            "title": "8.校正机器人当前位置",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#8%E6%A0%A1%E6%AD%A3%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%BD%93%E5%89%8D%E4%BD%8D%E7%BD%AE",
            "cmd": "/api/position_adjust"
        },
        {
            "title": "9.请求机器人实时数据",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#9%E8%AF%B7%E6%B1%82%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%AE%9E%E6%97%B6%E6%95%B0%E6%8D%AE",
            "cmd": "/api/request_data"
        },
        {
            "title": "10.机器人主动通知",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#10%E6%9C%BA%E5%99%A8%E4%BA%BA%E4%B8%BB%E5%8A%A8%E9%80%9A%E7%9F%A5",
            "cmd": "/api/xxxxxxxxxxx"
        },
        {
            "title": "11.设置参数",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#11%E8%AE%BE%E7%BD%AE%E5%8F%82%E6%95%B0",
            "cmd": "/api/set_params"
        },
        {
            "title": "12.获取参数",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#12%E8%8E%B7%E5%8F%96%E5%8F%82%E6%95%B0",
            "cmd": "/api/get_params"
        },
        {
            "title": "13.无线网络接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#13%E6%97%A0%E7%BA%BF%E7%BD%91%E7%BB%9C%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/wifi/list"
        },
        {
            "title": "14.地图接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#14%E5%9C%B0%E5%9B%BE%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/map/list"
        },
        {
            "title": "15.关机重启接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#15%E5%85%B3%E6%9C%BA%E9%87%8D%E5%90%AF%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/shutdown"
        },
        {
            "title": "16.软件更新接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#16%E8%BD%AF%E4%BB%B6%E6%9B%B4%E6%96%B0%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/software/get_version"
        },
        {
            "title": "17.设置灯带接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#17%E8%AE%BE%E7%BD%AE%E7%81%AF%E5%B8%A6%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/LED/set_luminance"
        },
        {
            "title": "18.自诊断接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#18%E8%87%AA%E8%AF%8A%E6%96%AD%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/diagnosis/get_result"
        },
        {
            "title": "19.获取电源状态接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#19%E8%8E%B7%E5%8F%96%E7%94%B5%E6%BA%90%E7%8A%B6%E6%80%81%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/get_power_status"
        },
        {
            "title": "20.获取机器人全局路径接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#20%E8%8E%B7%E5%8F%96%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%85%A8%E5%B1%80%E8%B7%AF%E5%BE%84%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/get_planned_path"
        },
        {
            "title": "21.获取电梯状态接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#21%E8%8E%B7%E5%8F%96%E7%94%B5%E6%A2%AF%E7%8A%B6%E6%80%81%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/lift_status"
        },
        {
            "title": "22.获取两点间路径接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#22%E8%8E%B7%E5%8F%96%E4%B8%A4%E7%82%B9%E9%97%B4%E8%B7%AF%E5%BE%84%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/make_plan"
        },
        {
            "title": "23.获取机器人当前位置接口",
            "url": "http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#23%E8%8E%B7%E5%8F%96%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%BD%93%E5%89%8D%E4%BD%8D%E7%BD%AE%E6%8E%A5%E5%8F%A3",
            "cmd": "/api/get_current_location"
        }
    ]

@bp.route('/')
def index():
    """调试界面主页"""
    return render_template('index.html', robot_all_apis_options=robot_all_apis_options)

@bp.route('/tasks')
def tasks_page():
    """盘点任务管理页面"""
    return render_template('task.html')

@bp.route('/task-logs')
def task_logs_page():
    """任务日志列表页面"""
    return render_template('task-logs.html')



@bp.route('/api/robot/cmd', methods=['POST'])
def robot_cmd():
    """发送机器人控制命令API"""
    data = request.get_json()
    print(f"Received operation command: {data}")

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
    obs_control = current_app.obs_control

    # Call connect synchronously
    connect_result = obs_control.connect()
    if connect_result["status"] != "OK":
        return jsonify(connect_result), 500

    # Call start_recording synchronously
    result = obs_control.start_recording()
    if result["status"] != "OK":
        return jsonify(result), 500

    # Optionally log or verify the recording has started
    current_app.logger.info("Recording started successfully.")

    return jsonify(result)

@bp.route('/api/obs/stop_recording', methods=['POST'])
def stop_recording():
    """停止录制API"""
    obs_control = current_app.obs_control

    try:
        # Ensure OBS connection
        connect_result = obs_control.connect()
        if connect_result["status"] != "OK":
            return jsonify(connect_result), 500
        
        # Stop recording and get result
        result = obs_control.stop_recording()
        current_app.logger.info(f"Stop recording result: {result}")
        
        if result["status"] != "OK":
            return jsonify(result), 500

        # Close the WebSocket connection
        obs_control.close()

        # Return success response
        return jsonify({
            "status": "OK",
            "message": "Recording stopped successfully",
            "file_path": result.get("outputPath", "")  # Use OBS provided path if available
        })

    except Exception as e:
        current_app.logger.error(f"Error stopping recording: {str(e)}")
        try:
            obs_control.close()
        except:
            pass
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
    
    obs_control = current_app.obs_control
    obs_control.connect()
    result = obs_control.take_screenshot_all_cameras(position_info=position_info)
    obs_control.close()
    return jsonify(result)


@bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    # Add database check
    from app.models import TaskLog
    try:
        log_count = TaskLog.query.count()
        return jsonify({
            "status": "OK",
            "message": "Service is running",
            "task_logs_count": log_count,
            "db_status": "Connected"
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e),
            "db_status": "Error"
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
        current_app.logger.info(f"Request headers: {dict(request.headers)}")
        current_app.logger.info(f"Content-Type: {request.content_type}")
        current_app.logger.info(f"Raw request data: {request.data}")
        
        try:
            data = request.get_json()
        except Exception as e:
            current_app.logger.error(f"Failed to parse JSON: {str(e)}")
            return jsonify({'status': 'ERROR', 'message': 'Invalid JSON format'}), 400
            
        current_app.logger.info(f"Creating new task with data: {data}")
        
        task = Task(
            marker=data.get('marker', ''),
            action=data.get('action', 0),
            description=data.get('description', ''),
            create_at=datetime.now(timezone(timedelta(hours=8)))  # Use Shanghai timezone
        )

        db.session.add(task)
        db.session.commit()
        
        current_app.logger.info(f"Successfully created task ID: {task.task_id}")
        return jsonify({
            'status': 'OK', 
            'task_id': task.task_id,
            'message': 'Task created successfully'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating task: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to create task: {str(e)}'
        }), 500

@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取单个盘点任务"""
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'task_id': task.task_id,
        'marker': task.marker,
        'action': task.action,
        'create_at': task.create_at.strftime("%Y-%m-%d %H:%M:%S") if task.create_at else None,
        'update_at': task.update_at.strftime("%Y-%m-%d %H:%M:%S") if task.update_at else None,
        'description': task.description
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
    """执行盘点任务"""
    task = Task.query.get_or_404(task_id)
    marker_list = task.marker.split(',') if task.marker else []
    if not marker_list:
        return jsonify({'status': 'ERROR', 'message': 'No markers provided'}), 400
    
    start_time = datetime.now()
    status = 1  # 1 = in progress
    file_paths = []
    
    # Create initial task log
    current_app.logger.info(f"Creating initial TaskLog for task {task_id}")
    task_log = TaskLog(
        task_id=task_id,
        marker=task.marker,
        action=task.action,
        start_time=start_time,
        end_time=datetime.now(),
        status=1,  # 1 = in progress
        file_count=0,
        file_paths='[]'
    )
    db.session.add(task_log)
    db.session.commit()
    current_app.logger.info(f"Initial TaskLog created with ID: {task_log.log_id}")
    
    try:
        if task.action == 0:  # Photo task
            # Send move command with all markers
            markers = ','.join(marker.strip() for marker in marker_list)
            move_result = current_app.robot_control.send_command(f"/api/move?marker={markers}")
            if move_result.get('status') != 'OK':
                raise Exception(f"Failed to start movement: {move_result.get('message')}")

            current_app.logger.info("Started movement through markers for photo task")
            completed_markers = set()
            
            # Monitor robot status until all markers are processed
            while len(completed_markers) < len(marker_list):
                robot_status = current_app.robot_control.send_command("/api/robot_status")
                if robot_status.get('status') != 'OK':
                    raise Exception("Failed to get robot status")

                results = robot_status.get('results', {})
                current_target = results.get('move_target')
                move_status = results.get('move_status')
                
                # Skip if no target or already processed
                if not current_target or current_target in completed_markers:
                    time.sleep(1)
                    continue
                
                # If succeeded at current target, take photo
                if move_status == 'succeeded':
                    current_app.logger.info(f"Robot reached marker {current_target}, taking photos")
                    
                    photo_result = current_app.obs_control.take_screenshot_all_cameras(
                        position_info=current_target
                    )
                    if photo_result.get('status') == 'OK':
                        new_files = photo_result.get('file_paths', [])
                        if new_files:
                            file_paths.extend(new_files)
                            current_app.logger.info(f"Saved {len(new_files)} photos for marker {current_target}")
                        else:
                            status = 3  # 3 = partial completion
                            current_app.logger.warning(f"No photos saved for marker {current_target}")
                    else:
                        status = 3  # 3 = partial completion
                        current_app.logger.warning(f"Photo failed at {current_target}: {photo_result.get('message')}")
                    
                    completed_markers.add(current_target)
                    
                # Handle failures
                elif move_status in ['failed', 'canceled']:
                    status = 3  # 3 = partial completion
                    current_app.logger.warning(f"Movement to {current_target} {move_status}")
                    completed_markers.add(current_target)
                
                time.sleep(1)  # Prevent too frequent polling
                
        elif task.action == 1:  # Recording task
            # Send move command with all markers
            markers = ','.join(marker.strip() for marker in marker_list)
            move_result = current_app.robot_control.send_command(f"/api/move?marker={markers}")
            if move_result.get('status') != 'OK':
                raise Exception(f"Failed to start movement: {move_result.get('message')}")

            current_app.logger.info("Started movement through markers for recording task")
            recording_started = False
            last_marker = marker_list[-1]
            
            # Monitor robot status
            while True:
                robot_status = current_app.robot_control.send_command("/api/robot_status")
                if robot_status.get('status') != 'OK':
                    raise Exception("Failed to get robot status")

                results = robot_status.get('results', {})
                current_target = results.get('move_target')
                move_status = results.get('move_status')
                
                # Start recording at first marker
                if not recording_started and move_status == 'succeeded':
                    current_app.logger.info("Robot reached first marker, starting recording")
                    start_result = current_app.obs_control.start_recording()
                    if start_result.get('status') != 'OK':
                        status = 3  # 3 = partial completion
                        current_app.logger.warning(f"Start recording failed: {start_result.get('message')}")
                    recording_started = True
                
                # Stop recording at last marker or on failure
                if (current_target == last_marker and move_status == 'succeeded') or \
                   move_status in ['failed', 'canceled']:
                    if recording_started:
                        current_app.logger.info("Stopping recording")
                        stop_result = current_app.obs_control.stop_recording()
                        if stop_result.get('status') != 'OK':
                            status = 3  # 3 = partial completion
                            current_app.logger.warning(f"Stop recording failed: {stop_result.get('message')}")
                        else:
                            file_paths.extend(stop_result.get('file_paths', []))
                    break
                
                time.sleep(1)  # Prevent too frequent polling
                
        else:
            status = 4  # 4 = failed
            raise Exception(f"Unknown action type: {task.action}")
            
        # Update task log with final status
        if status == 1:  # If still in progress
            status = 2  # 2 = completed
            
        task_log.status = status
        task_log.end_time = datetime.now()
        task_log.file_count = len(file_paths)
        task_log.file_paths = json.dumps(file_paths)
        db.session.commit()
        
        return jsonify({
            'status': 'OK',
            'message': 'Task executed successfully',
            'file_paths': file_paths
        })
        
    except Exception as e:
        status = 4  # 4 = failed
        current_app.logger.error(f"Error running task {task_id}: {str(e)}")
        # Try to stop recording if exception occurs during recording task
        if task.action == 1 and recording_started:
            try:
                stop_result = current_app.obs_control.stop_recording()
                if stop_result.get('status') == 'OK':
                    file_paths.extend(stop_result.get('file_paths', []))
            except Exception as stop_error:
                current_app.logger.error(f"Error stopping recording after failure: {stop_error}")
                
        return jsonify({
            'status': 'ERROR', 
            'message': f'Failed to execute task: {str(e)}'
        }), 500
        
    finally:
        # Ensure task log is always updated
        try:
            task_log.status = status
            task_log.end_time = datetime.now()
            task_log.file_count = len(file_paths)
            task_log.file_paths = json.dumps(file_paths)
            db.session.commit()
            current_app.logger.info(f"Task log updated - Status: {status}, Files: {len(file_paths)}")
        except Exception as e:
            current_app.logger.error(f"Failed to update task log: {str(e)}")

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
