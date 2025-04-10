import os
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from flask import current_app
from obswebsocket import obsws, requests, exceptions

class OBSControl:
    def __init__(self, app=None):
        self.app = app
        self.ws = None
        self.simulation_mode = False  # 禁用模拟模式，使用实际的OBS摄像头
        self.camera_scenes = [
            "Scene1"  # 使用实际的场景名称
        ]
        if app is not None:
            self.init_app(app)
        else:
            self.host = None
            self.port = None
            self.password = None
    
    def init_app(self, app):
        """从配置中初始化OBS WebSocket连接参数"""
        ws_url = app.config['OBS_WS_URL']
        # 解析 WebSocket URL 获取 host 和 port
        # 格式: ws://host:port
        ws_parts = ws_url.replace('ws://', '').split(':')
        self.host = ws_parts[0]
        self.port = int(ws_parts[1])
        self.password = app.config['OBS_PASSWORD']
    
    def get_connection_params(self):
        """获取连接参数"""
        if self.host is None:
            ws_url = current_app.config['OBS_WS_URL']
            ws_parts = ws_url.replace('ws://', '').split(':')
            self.host = ws_parts[0]
            self.port = int(ws_parts[1])
            self.password = current_app.config['OBS_PASSWORD']
        return self.host, self.port, self.password

    def add_info_to_image(self, img, position_info, camera_id):
        """向图片添加位置和时间信息"""
        draw = ImageDraw.Draw(img)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加测试图案（如果是模拟模式）
        if self.simulation_mode:
            # 绘制网格
            for i in range(0, 300, 30):
                draw.line([(i, 0), (i, 200)], fill='gray', width=1)
                draw.line([(0, i), (300, i)], fill='gray', width=1)
            
            # 绘制相机编号
            draw.text((140, 90), f"Camera {camera_id}", fill='white', font=ImageFont.load_default())
            
            # 绘制十字准心
            draw.line([(140, 90), (160, 110)], fill='red', width=2)
            draw.line([(160, 90), (140, 110)], fill='red', width=2)
        
        # 添加位置信息
        position_text = f"Position: X={position_info['x']:.2f}, Y={position_info['y']:.2f}, θ={position_info['theta']:.2f}"
        draw.text((10, 10), position_text, fill='white', font=ImageFont.load_default())
        
        # 添加时间信息
        time_text = f"Time: {timestamp}"
        draw.text((10, 30), time_text, fill='white', font=ImageFont.load_default())
        
        # 添加摄像头编号
        camera_text = f"Camera: {camera_id}"
        draw.text((10, 50), camera_text, fill='white', font=ImageFont.load_default())
        
        return img

    def is_connected(self):
        """检查WebSocket连接是否有效"""
        try:
            if self.ws:
                # 尝试发送一个轻量级请求来测试连接
                self.ws.call(requests.GetVersion())
                return True
        except Exception:
            return False
        return False

    def connect(self):
        """连接到OBS WebSocket服务器"""
        if self.simulation_mode:
            return {"status": "OK", "message": "Connected in simulation mode"}

        try:
            host, port, password = self.get_connection_params()
            if self.ws is None or not self.is_connected():  # Use is_connected() to check connection
                self.ws = obsws(host=host, port=port, password=password)
                self.ws.connect()
            return {"status": "OK", "message": "Connected to OBS"}
        except exceptions.ConnectionFailure as e:
            return {"status": "ERROR", "message": f"Failed to connect to OBS: {str(e)}"}

    def take_screenshot_all_cameras(self, marker_name, camera_id=None):
        """拍摄所有摄像头的截图
        
        Args:
            marker_name (str): Name of the marker where photo is taken
            camera_id (str|int): Optional specific camera ID to capture
            
        Returns:
            dict: Results including file paths and status
        """
        results = []
        # 使用日期作为文件夹名
        date_str = datetime.now().strftime("%Y%m%d")
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        try:
            # 如果不是模拟模式，先连接到OBS
            if not self.simulation_mode:
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    raise RuntimeError(connect_result["message"])

                # 确保WebSocket连接有效
                if not self.is_connected():  # Use is_connected() to check connection
                    reconnect_result = self.connect()
                    if reconnect_result["status"] != "OK":
                        raise RuntimeError(reconnect_result["message"])

                # 获取可用场景列表
                scenes = self.ws.call(requests.GetSceneList())
                scene_names = [scene['sceneName'] for scene in scenes.getScenes()]
                print(f"Available scenes: {scene_names}")  # 打印可用场景列表，用于调试

            for i, scene in enumerate(self.camera_scenes, 1):
                if self.simulation_mode:
                    # 创建一个模拟的截图（深蓝色背景）
                    filename = f"{timestamp}_camera{i}_x{position_info['x']:.2f}_y{position_info['y']:.2f}_theta{position_info['theta']:.2f}.jpg"
                    filepath = os.path.join(base_dir, filename)
                    
                    # 创建一个300x200的深蓝色图片作为模拟
                    img = Image.new('RGB', (300, 200), color='navy')
                    img = self.add_info_to_image(img, position_info, f"Camera {i}")
                    img.save(filepath)
                    
                    results.append({
                        "camera_id": i,
                        "scene": scene,
                        "status": "OK",
                        "message": f"Screenshot taken for camera {i} in simulation mode",
                        "timestamp": time.time(),
                        "filename": filename,
                        "filepath": filepath
                    })
                else:
                    if scene not in scene_names:
                        results.append({
                            "camera_id": i,
                            "scene": scene,
                            "status": "ERROR",
                            "message": f"Scene '{scene}' not found in OBS"
                        })
                        continue

                    try:
                        # 切换到对应的场景
                        self.ws.call(requests.SetCurrentProgramScene(sceneName=scene))
                        
                        # 等待场景切换完成
                        time.sleep(0.5)
                        
                        # 拍摄截图 - 新文件名格式: 标记点_摄像头编号_时间戳.jpg
                        filename = f"{marker_name}_camera{i}_{timestamp}.jpg"
                        filepath = os.path.join(base_dir, filename)
                        
                        # 使用场景名称
                        self.ws.call(requests.SaveSourceScreenshot(
                            sourceName="Camera1",  # 使用实际的摄像头源名称
                            imageFormat="jpg",
                            imageFilePath=os.path.abspath(filepath)
                        ))
                        
                        results.append({
                            "camera_id": i,
                            "scene": scene,
                            "status": "OK",
                            "filename": filename,
                            "filepath": filepath
                        })
                    except Exception as e:
                        results.append({
                            "camera_id": i,
                            "scene": scene,
                            "status": "ERROR",
                            "message": str(e)
                        })

        except Exception as e:
            # 捕获所有异常并记录日志
            current_app.logger.error(f"Error in take_screenshot_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": []
            }

        return {
            "status": "OK",
            "timestamp": timestamp,
            "position": position_info,
            "results": results
        }

    def start_recording(self, marker_names):
        """开始录制
        
        Args:
            marker_names (list): List of marker names that will be visited during recording
            
        Returns:
            dict: Recording start status with timestamp
        """
        self.recording_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_markers = "_".join(marker_names)
        if self.simulation_mode:
            return {
                "status": "OK",
                "message": "Recording started in simulation mode",
                "timestamp": time.time()
            }
            
        try:
            if not self.ws or not self.is_connected():  # Ensure WebSocket is connected
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    raise RuntimeError(connect_result["message"])
            
            self.ws.call(requests.StartRecord())
            current_app.logger.info("Recording started successfully.")
            return {
                "status": "OK",
                "message": "Recording started",
                "timestamp": time.time()
            }
        except exceptions.ConnectionFailure as e:
            current_app.logger.error(f"Connection failure during start_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Connection failure: {str(e)}",
                "timestamp": time.time()
            }
        except Exception as e:
            current_app.logger.error(f"Error in start_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": time.time()
            }

    def stop_recording(self):
        """停止录制"""
        if self.simulation_mode:
            return {
                "status": "OK",
                "message": "Recording stopped in simulation mode",
                "timestamp": time.time()
            }
            
        try:
            if not self.ws:
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    return connect_result
            
            # Try to get recording settings (may fail on some OBS versions)
            output_path = ""
            try:
                record_settings = self.ws.call(requests.GetRecordSettings())
                current_app.logger.info(f"Current recording settings: {record_settings}")
                output_path = record_settings.get('outputDirectory', '')
                current_app.logger.info(f"Configured output directory: {output_path}")
            except Exception as e:
                current_app.logger.warning(f"Could not get recording settings: {str(e)}")
                # Fallback to getting output path from StopRecord response
            
            # First check if recording is actually active
            is_recording = False
            recording_filename = None
            
            try:
                # Get current program scene first as it may indicate active recording
                current_scene = self.ws.call(requests.GetCurrentProgramScene())
                current_app.logger.info(f"Current program scene: {current_scene.sceneName}")
                
                # Try multiple ways to check recording status
                status = self.ws.call(requests.GetRecordStatus())
                current_app.logger.info(f"Recording status response: {vars(status)}")
                
                # Handle different OBS response formats
                if hasattr(status, 'isRecording'):
                    is_recording = status.isRecording
                    recording_filename = getattr(status, 'recordingFilename', None)
                elif hasattr(status, 'outputActive'):
                    is_recording = status.outputActive
                    recording_filename = getattr(status, 'outputPath', None)
                elif hasattr(status, 'recording'):
                    is_recording = status.recording
                    recording_filename = getattr(status, 'filename', None)
                else:
                    current_app.logger.warning(f"Unknown status format: {vars(status)}")
                    # Fallback to checking output status directly
                    try:
                        output_status = self.ws.call(requests.GetOutputStatus('adv_file_output'))
                        if hasattr(output_status, 'active'):
                            is_recording = output_status.active
                            recording_filename = getattr(output_status, 'path', None)
                        current_app.logger.info(f"Output status: {vars(output_status)}")
                    except Exception as e:
                        current_app.logger.warning(f"Could not get output status: {str(e)}")
                
                if not is_recording:
                    current_app.logger.warning(f"Initial status check shows no active recording")
                    # Try one last check by looking for active outputs
                    try:
                        outputs = self.ws.call(requests.ListOutputs())
                        current_app.logger.info(f"All outputs: {outputs.outputs}")
                        for output in outputs.outputs:
                            if output.outputKind == 'adv_file_output' and output.outputActive:
                                is_recording = True
                                recording_filename = output.outputSettings.get('path', None)
                                current_app.logger.info(f"Found active output: {output}")
                                break
                    except Exception as e:
                        current_app.logger.warning(f"Could not list outputs: {str(e)}")
                    
                    if not is_recording:
                        # As final fallback, just attempt to stop recording anyway
                        current_app.logger.warning("No active recording found, but attempting stop anyway")
                        # Don't return error - proceed with stop attempt
            except Exception as e:
                current_app.logger.error(f"Error checking recording status: {str(e)}")
                # Continue with stop attempt since some OBS versions may not support status check
                current_app.logger.info("Proceeding with stop recording despite status check error")

                # Configure our desired output path
                date_str = datetime.now().strftime("%Y%m%d")
                output_dir = os.path.abspath(os.path.join("static", "videos", date_str))
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"{self.recording_markers}_Camera1_{self.recording_start_time}.mkv"
                current_app.logger.info(f"Configured output directory: {output_dir}")
                
                # Try to set recording settings if possible
                try:
                    settings = self.ws.call(requests.GetRecordSettings())
                    if hasattr(settings, 'outputDirectory'):
                        settings.outputDirectory = output_dir
                        settings.outputFormat = "mkv"
                        self.ws.call(requests.SetRecordSettings(settings))
                    elif hasattr(settings, 'outputPath'):
                        settings.outputPath = os.path.join(output_dir, filename)
                        self.ws.call(requests.SetRecordSettings(settings))
                except Exception as e:
                    current_app.logger.warning(f"Could not configure recording settings: {str(e)}")

            # Stop recording and get the output path
            try:
                response = self.ws.call(requests.StopRecord())
                recording_path = ""
                
                # Try to get path from response
                if hasattr(response, 'outputPath'):
                    recording_path = response.outputPath
                elif hasattr(response, 'recordingFilename'):
                    recording_path = response.recordingFilename
                
                # If no path from response, check default OBS locations
                if not recording_path:
                    default_locations = [
                        os.path.expanduser("~/Videos"),
                        os.path.expanduser("~"),
                        "/tmp"
                    ]
                    for loc in default_locations:
                        try:
                            files = [f for f in os.listdir(loc) if f.endswith(('.mp4','.mkv'))]
                            if files:
                                files.sort(key=lambda x: os.path.getmtime(os.path.join(loc, x)))
                                recording_path = os.path.join(loc, files[-1])
                                break
                        except Exception:
                            continue
                
                # Move file to our desired location if found
                if recording_path and os.path.exists(recording_path):
                    file_ext = os.path.splitext(recording_path)[1]
                    end_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{self.recording_markers}_Camera1_{self.recording_start_time}_{end_time}{file_ext}"
                    new_path = os.path.join(output_dir, new_filename)
                    
                    # Ensure target directory exists
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Move the file
                    os.rename(recording_path, new_path)
                    recording_path = new_path
                    current_app.logger.info(f"Successfully moved recording to: {recording_path}")
                else:
                    current_app.logger.warning("Could not locate recording file")
                    recording_path = ""
                    
            except Exception as e:
                current_app.logger.error(f"Error during stop recording: {str(e)}")
                recording_path = ""
            
            return {
                "status": "OK",
                "message": "Recording stopped successfully",
                "timestamp": time.time(),
                "file_path": recording_path if recording_path else ""
            }
        except exceptions.ConnectionFailure as e:
            current_app.logger.error(f"Connection failure during stop_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Connection failure: {str(e)}",
                "timestamp": time.time()
            }
        except Exception as e:
            current_app.logger.error(f"Error in stop_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": time.time()
            }
    
    def close(self):
        """关闭WebSocket连接"""
        if not self.simulation_mode and self.ws:
            self.ws.disconnect()
