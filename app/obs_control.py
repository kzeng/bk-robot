import os
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from flask import current_app
from obswebsocket import obsws, requests, exceptions
from loguru import logger

class OBSControl:
    def __init__(self, app=None):
        self.app = app
        self.ws = None
        self.simulation_mode = False  # 禁用模拟模式，使用实际的OBS摄像头
        self.camera_scenes = []  # Will be populated when connecting to OBS
        self.connected = False  # 新增连接状态属性
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
                try:
                    self.ws.connect()
                    self.connected = True  # 设置连接状态为True
                    
                    # Get available scenes from OBS
                    scenes = self.ws.call(requests.GetSceneList())
                    self.camera_scenes = [scene['sceneName'] for scene in scenes.getScenes()]
                except Exception as e:
                    self.connected = False
                    raise e
                
                if not self.camera_scenes:
                    logger.warning("No scenes found in OBS")
                    return {
                        "status": "ERROR", 
                        "message": "No scenes found in OBS"
                    }
                    
            return {
                "status": "OK", 
                "message": "Connected to OBS",
                "scenes": self.camera_scenes
            }
        except exceptions.ConnectionFailure as e:
            self.connected = False
            return {"status": "ERROR", "message": f"Failed to connect to OBS: {str(e)}"}

    def take_screenshot_all_cameras(self, position_info):
        """Capture screenshots from all configured OBS cameras
        
        Handles the full workflow:
        1. Creates dated directory for screenshots
        2. Connects to OBS WebSocket if not already connected
        3. Gets list of available scenes/sources
        4. For each camera scene:
           - Switches to the scene
           - Captures screenshot
           - Saves with standardized filename format
           - Records result status
        
        Args:
            position_info (str): Marker name/position identifier to include in filenames
            
        Returns:
            dict: {
                "status": "OK"|"ERROR",
                "timestamp": str,  # Capture timestamp
                "position": str,    # Position info
                "results": [        # List of capture results per camera
                    {
                        "camera_id": int,
                        "scene": str,
                        "status": "OK"|"ERROR",
                        "filename": str,  # Only if OK
                        "filepath": str,   # Only if OK 
                        "message": str     # Only if ERROR
                    }
                ]
            }
        """
        results = []
        # 使用日期作为文件夹名
        date_str = datetime.now().strftime("%Y%m%d")
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        if not position_info:
            position_info = 'Unknown'

        try:
            # 如果不是模拟模式，先连接到OBS
            if not self.simulation_mode:
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    raise RuntimeError(connect_result["message"])
                logger.info(f"OBS connection successful.")

                # Check if the directory exists
                if not os.path.exists(base_dir):
                    os.makedirs(base_dir)
                    logger.info(f"Created directory: {base_dir}")
                else:
                    logger.info(f"Directory exists: {base_dir}")

                # 获取可用场景列表
                scenes = self.ws.call(requests.GetSceneList())
                scene_names = [scene['sceneName'] for scene in scenes.getScenes()]
                logger.debug(f"Available scenes: {scene_names}")

                # powered by LAO-ZENG
                scene_sources = {}

                for scene_name in scene_names:
                    scene_items = self.ws.call(requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
                    if scene_items:
                        # Extract name of the first source (lowest index = bottom layer in OBS)
                        first_source_name = scene_items[0]['sourceName'].strip().replace(' ', '')
                        scene_sources[scene_name] = first_source_name
                        logger.info(f"First source in scene '{first_source_name}': {first_source_name}")
                    else:
                        logger.warning("No sources found in the current scene! so use scene name as source")
                        scene_sources[scene_name] = scene_name
        


                # # Get list of sources and map them to scenes
                # # Handles multiple OBS WebSocket API versions with fallbacks:
                # # 1. First tries modern GetInputList API (OBS WebSocket v5+)
                # # 2. Falls back to GetSources for older versions
                # # 3. Uses scene names as last resort if no sources found
                # try:
                #     # First attempt: GetInputList (modern API)
                #     try:
                #         inputs = self.ws.call(requests.GetInputList())
                #         source_names = []
                #         if hasattr(inputs, 'inputs'):
                #             source_names = [input['inputName'] for input in inputs.inputs]
                #         logger.info(f"Got sources using GetInputList: {source_names}")
                #     except Exception as input_error:
                #         logger.warning(f"Could not get inputs, trying GetSources: {str(input_error)}")
                #         # Fallback to GetSources for older versions
                #         sources = self.ws.call(requests.GetSources())
                #         source_names = []
                #         if hasattr(sources, 'sources'):
                #             source_names = [source['name'] for source in sources.sources]
                #         elif hasattr(sources, 'getSources') and callable(sources.getSources):
                #             source_names = [source['name'] for source in sources.getSources()]
                    
                #     # If still no sources, use scene names as a last resort
                #     if not source_names:
                #         source_names = scene_names.copy()
                #         logger.warning("No sources found, using scene names as sources")

                #     if not source_names:
                #         raise RuntimeError("No sources found in OBS")
                #     logger.info(f"Available sources: {source_names}")

                #     # Create mapping of scene names to their sources
                #     scene_sources = {}
                #     for scene in self.camera_scenes:
                #         # First try exact match (case-insensitive)
                #         exact_matches = [s for s in source_names if s.lower() == scene.lower()]
                        
                #         if exact_matches:
                #             # Use exact match if available
                #             scene_sources[scene] = exact_matches[0]
                #             continue
                            
                #         # If no exact match, try substring match
                #         matching_sources = [s for s in source_names if scene.lower() in s.lower()]
                        
                #         if matching_sources:
                #             # Use first matching source
                #             scene_sources[scene] = matching_sources[0]
                #         else:
                #             # Fallback to first available source if no match found
                #             scene_sources[scene] = source_names[0]
                #             logger.warning(
                #                 f"No matching source for scene {scene}, using {source_names[0]}"
                #             )

                # except Exception as e:
                #     logger.error(f"Error getting sources: {str(e)}")





            for i, scene in enumerate(self.camera_scenes, 1):
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
                    
                    
                    # 拍摄截图 - 文件名格式: {marker名称}-{场景名称}-{摄像头名称}-{时间戳}.jpg
                    filename = f"{position_info}-{scene}-{scene_sources[scene]}-{timestamp}.jpg"
                    filepath = os.path.join(base_dir, filename)
                    
                    # 确保基础目录存在
                    os.makedirs(base_dir, exist_ok=True)
                    logger.info(f"确保目录存在: {base_dir}")
                    # 使用绝对路径并确保其有效性
                    abs_filepath = os.path.abspath(filepath)
                    logger.info(f"尝试保存截图至: {abs_filepath}")
                    
                    # Use the source mapped to this scene
                    self.ws.call(requests.SaveSourceScreenshot(
                        sourceName=scene_sources[scene],
                        imageFormat="jpg",
                        imageFilePath=abs_filepath
                    ))
                    logger.info(f"截图成功保存至: {abs_filepath}")
                    
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
            logger.error(f"Error in take_screenshot_all_cameras: {str(e)}")
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




    def start_recording(self, marker_names=None):
        """Start recording on all configured cameras
        
        Args:
            marker_names (list, optional): List of marker names that will be visited during recording.
                Used for naming the output file. Defaults to empty list if not provided.
            
        Returns:
            dict: {
                "status": "OK"|"ERROR",
                "message": str,    # Status message
                "timestamp": float  # Unix timestamp of operation
            }
        """
        self.recording_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_markers = "_".join(marker_names) if marker_names else ""
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
            logger.info("Recording started successfully.")
            return {
                "status": "OK",
                "message": "Recording started",
                "timestamp": time.time()
            }
        except exceptions.ConnectionFailure as e:
            logger.error(f"Connection failure during start_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Connection failure: {str(e)}",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error in start_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": time.time()
            }

    def stop_recording(self):
        """Stop recording and handle the recorded file
        
        Performs the following operations:
        1. Checks if recording is actually active (handles multiple OBS API versions)
        2. Stops the recording via OBS WebSocket
        3. Attempts to locate the recorded file (handles different OBS versions/paths)
        4. Moves the file to the configured output directory with standardized naming
        5. Returns status including the final file path if successful
        
        Returns:
            dict: {
                "status": "OK"|"ERROR",
                "message": str,      # Status message
                "timestamp": float,  # Unix timestamp
                "file_path": str     # Path to recording file if successful
            }
        """
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
                logger.info(f"Current recording settings: {record_settings}")
                output_path = record_settings.get('outputDirectory', '')
                logger.info(f"Configured output directory: {output_path}")
            except Exception as e:
                logger.warning(f"Could not get recording settings: {str(e)}")
                # Fallback to getting output path from StopRecord response
            
            # First check if recording is actually active
            is_recording = False
            recording_filename = None
            
            try:
                # Get current program scene first as it may indicate active recording
                current_scene = self.ws.call(requests.GetCurrentProgramScene())
                logger.info(f"Current program scene: {current_scene.sceneName}")
                
                # Check recording status - handles multiple OBS API versions:
                # 1. GetRecordStatus (modern API)
                status = self.ws.call(requests.GetRecordStatus())
                
                # Handle different response formats from different OBS versions
                if hasattr(status, 'isRecording'):  # OBS WebSocket v5+
                    is_recording = status.isRecording
                    recording_filename = getattr(status, 'recordingFilename', None)
                elif hasattr(status, 'outputActive'):  # Older OBS versions
                    is_recording = status.outputActive
                    recording_filename = getattr(status, 'outputPath', None)
                elif hasattr(status, 'recording'):  # Alternative format
                    is_recording = status.recording
                    recording_filename = getattr(status, 'filename', None)
                else:  # Unknown format - log warning and proceed to fallback
                    logger.debug(f"Unrecognized status format: {vars(status)}")
                    # Fallback to checking output status directly
                    try:
                        output_status = self.ws.call(requests.GetOutputStatus('adv_file_output'))
                        if hasattr(output_status, 'active'):
                            is_recording = output_status.active
                            recording_filename = getattr(output_status, 'path', None)
                        logger.info(f"Output status: {vars(output_status)}")
                    except Exception as e:
                        logger.warning(f"Could not get output status: {str(e)}")
                
                if not is_recording:
                    logger.warning(f"Initial status check shows no active recording")
                    # Try one last check by looking for active outputs
                    try:
                        outputs = self.ws.call(requests.ListOutputs())
                        logger.info(f"All outputs: {outputs.outputs}")
                        for output in outputs.outputs:
                            if output.outputKind == 'adv_file_output' and output.outputActive:
                                is_recording = True
                                recording_filename = output.outputSettings.get('path', None)
                                logger.info(f"Found active output: {output}")
                                break
                    except Exception as e:
                        logger.warning(f"Could not list outputs: {str(e)}")
                    
                    if not is_recording:
                        # As final fallback, just attempt to stop recording anyway
                        logger.warning("No active recording found, but attempting stop anyway")
                        # Don't return error - proceed with stop attempt
            except Exception as e:
                logger.error(f"Error checking recording status: {str(e)}")
                logger.info("Proceeding with stop recording despite status check error")

                # Configure our desired output path
                date_str = datetime.now().strftime("%Y%m%d")
                output_dir = os.path.abspath(os.path.join("static", "videos", date_str))
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"{self.recording_markers}_Camera1_{self.recording_start_time}.mkv"
                logger.info(f"Configured output directory: {output_dir}")
                
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
                    logger.warning(f"Could not configure recording settings: {str(e)}")

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
                    logger.info(f"Successfully moved recording to: {recording_path}")
                else:
                    logger.warning("Could not locate recording file")
                    recording_path = ""
                    
            except Exception as e:
                logger.error(f"Error during stop recording: {str(e)}")
                recording_path = ""
            
            return {
                "status": "OK",
                "message": "Recording stopped successfully",
                "timestamp": time.time(),
                "file_path": recording_path if recording_path else ""
            }
        except exceptions.ConnectionFailure as e:
            logger.error(f"Connection failure during stop_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Connection failure: {str(e)}",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error in stop_recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Unexpected error: {str(e)}",
                "timestamp": time.time()
            }
    
    def close(self):
        """关闭WebSocket连接"""
        if not self.simulation_mode and self.ws:
            self.ws.disconnect()
        self.connected = False  # 设置连接状态为False
