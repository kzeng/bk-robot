from flask import render_template, jsonify, request, Blueprint, current_app, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from app.models import Task, TaskLog
from app import db
from datetime import datetime, timezone, timedelta
import asyncio
import os
from functools import wraps
import time
from threading import Thread

import serial
from .lift import Lift



def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

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
def index():
    """调试界面主页"""
    return render_template('index.html', robot_all_apis_options=robot_all_apis_options)


@bp.route('/docs/<path:filename>')
def serve_docs(filename):
    return send_from_directory('static/docs', filename)


@bp.route('/tasks')
def tasks_page():
    """盘点任务管理页面"""
    return render_template('task.html')

@bp.route('/task-logs')
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
    thread = Thread(target=async_run_task, args=(current_app._get_current_object(), task.task_id))
    thread.start()
    return jsonify({
        'status': 'OK',
        'message': 'Task execution started',
        'task_log_id': task.task_id
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
                    if move_result.get('status') != 'OK':
                        raise Exception(f"Failed to start movement: {move_result.get('message')}")
                    while True:
                        robot_status = app.robot_control.send_command("/api/robot_status")
                        if robot_status.get('status') != 'OK':
                            raise Exception("Failed to get robot status")
                        results = robot_status.get('results', {})
                        move_status = results.get('move_status')
                        if move_status == 'succeeded':
                            app.logger.info(f"Robot reached marker {end_marker}, taking photos")
                            photo_result = app.obs_control.take_screenshot_all_cameras(position_info=end_marker)
                            if photo_result.get('status') == 'OK':
                                new_files = photo_result.get('file_paths', [])
                                if new_files:
                                    file_paths.extend(new_files)
                                    app.logger.info(f"Saved {len(new_files)} photos at {end_marker}")
                                else:
                                    status = 3
                                    app.logger.warning(f"No photos saved at {end_marker}")
                            else:
                                status = 3
                                app.logger.warning(f"Photo failed at {end_marker}: {photo_result.get('message')}")
                            completed_markers.add(end_marker)
                            break
                        elif move_status in ['failed', 'canceled']:
                            status = 3
                            app.logger.warning(f"Movement to {end_marker} {move_status}")
                            break
                        time.sleep(1)
            elif task.action == 1:  # 录像
                markers = ','.join(marker_list)
                move_result = app.robot_control.send_command(f"/api/move?marker={markers}")
                if move_result.get('status') != 'OK':
                    raise Exception(f"Failed to start movement: {move_result.get('message')}")
                app.logger.info("Started movement through markers for recording task")
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
                        app.logger.info("Robot reached first marker, starting recording")
                        start_result = app.obs_control.start_recording()
                        if start_result.get('status') != 'OK':
                            status = 3
                            app.logger.warning(f"Start recording failed: {start_result.get('message')}")
                        recording_started = True
                    if (current_target == last_marker and move_status == 'succeeded') or \
                       move_status in ['failed', 'canceled']:
                        if recording_started:
                            app.logger.info("Stopping recording")
                            stop_result = app.obs_control.stop_recording()
                            if stop_result.get('status') != 'OK':
                                status = 3
                                app.logger.warning(f"Stop recording failed: {stop_result.get('message')}")
                            else:
                                file_paths.extend(stop_result.get('file_paths', []))
                        break
                    time.sleep(1)
            elif task.action == 99:  # 仅是移动
                subtasks = [(marker_list[i], marker_list[i+1]) for i in range(len(marker_list)-1)]
                for start_marker, end_marker in subtasks:
                    app.logger.info(f"Moving from {start_marker} to {end_marker} (move only, no photo/video)")
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
                            app.logger.info(f"Robot reached marker {end_marker}")
                            break
                        elif move_status in ['failed', 'canceled']:
                            status = 3
                            app.logger.warning(f"Movement to {end_marker} {move_status}")
                            break
                        time.sleep(1)
            else:
                status = 4
                raise Exception(f"Unknown action type: {task.action}")
            if status == 1:
                status = 2
        except Exception as e:
            status = 4
            app.logger.error(f"Error executing task {task_id}: {str(e)}")
            if task.action == 1 and 'recording_started' in locals() and recording_started:
                try:
                    stop_result = app.obs_control.stop_recording()
                    if stop_result.get('status') == 'OK':
                        file_paths.extend(stop_result.get('file_paths', []))
                except Exception as stop_error:
                    app.logger.error(f"Error stopping recording after failure: {stop_error}")
        finally:
            try:
                if task_log:
                    task_log.status = status
                    task_log.end_time = datetime.now()
                    task_log.file_count = len(file_paths)
                    task_log.file_paths = json.dumps(file_paths)
                    db.session.commit()
                    app.logger.info(f"Task log updated - Status: {status}, Files: {len(file_paths)}")
            except Exception as e:
                app.logger.error(f"Failed to update task log: {str(e)}")

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

SERIAL_PORT = '/dev/ttyUSB0'  # Replace with actual serial port
BAUDRATE = 9600
lift = None  # Initialize as None

try:
    # Initialize the Lift instance with logging
    print(f"Attempting to connect to lift on {SERIAL_PORT} at {BAUDRATE} baud")
    lift = Lift(port=SERIAL_PORT, baudrate=BAUDRATE)
    print("Lift connection established successfully")
except serial.SerialException as e:
    print(f"Serial connection error: {e}")
    print("Running in simulation mode (no hardware connected)")
except Exception as e:
    print(f"Unexpected error initializing Lift: {e}")
    print("Running in simulation mode")


@bp.route('/api/lift/status', methods=['GET'])
def lift_status():
    """Check lift connection status"""
    if lift is None:
        return jsonify({
            'status': 'error',
            'message': 'Lift not initialized',
            'connected': False
        }), 503
    
    try:
        # Simple check if serial connection is open
        connected = lift.serial_connection.is_open
        return jsonify({
            'status': 'success',
            'message': 'Lift is connected' if connected else 'Lift is disconnected',
            'connected': connected
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'connected': False
        }), 500

@bp.route('/api/lift/<command>', methods=['POST'])
def lift_command(command):
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