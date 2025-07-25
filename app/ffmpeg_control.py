"""
FFmpeg based camera control implementation
"""
import os
import subprocess
import time
import cv2
from datetime import datetime
from loguru import logger

class FFmpegControl:
    """FFmpeg camera control implementation"""
    def __init__(self):
        """Initialize FFmpeg camera control"""
        logger.info("Initializing FFmpeg camera control")
        self.camera_indices = []  # 存储可用的摄像头索引
        
        # 初始化 FFmpeg 路径
        if os.name == 'posix':
            self.ffmpeg_path = 'ffmpeg'  # Linux 通常在 PATH 中
        else:
            # 在 Windows 常见位置查找 FFmpeg
            possible_paths = [
                os.getenv('FFMPEG_PATH', ''),  # 首先检查环境变量
                r'C:\Work\Apps\ffmpeg\bin\ffmpeg.exe',
                'ffmpeg'  # 最后尝试 PATH
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    self.ffmpeg_path = path
                    logger.info(f"Found FFmpeg at: {path}")
                    break
            else:
                logger.error("FFmpeg not found. Please install FFmpeg or set FFMPEG_PATH environment variable.")
                self.ffmpeg_path = 'ffmpeg'  # 设置默认值，让系统继续运行

        self._detect_cameras()
        self._load_camera_config()

    def _detect_cameras(self):
        """检测系统中可用的摄像头并初始化配置"""
        logger.info("Detecting available cameras...")
        if os.name == 'posix':  # Linux
            try:
                # 使用v4l2-ctl命令列出所有视频设备
                result = subprocess.run(
                    ['v4l2-ctl', '--list-devices'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode == 0:
                    # 解析输出找到所有视频设备
                    current_device = None
                    for line in result.stdout.split('\n'):
                        if ':' in line:  # 这是设备名称行
                            current_device = line.strip().rstrip(':')
                        elif '/dev/video' in line:  # 这是设备路径行
                            device = line.strip()
                            try:
                                device_num = int(device.replace('/dev/video', ''))
                                # 验证设备是否支持视频捕获
                                caps_result = subprocess.run(
                                    ['v4l2-ctl', '-d', device, '-D'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                                )
                                if 'Video Capture' in caps_result.stdout:
                                    self.camera_indices.append(device_num)
                                    
                                    # 初始化时配置摄像头参数
                                    try:
                                        # 设置视频格式和摄像头参数
                                        subprocess.run([
                                            'v4l2-ctl', '-d', device,
                                            f'--set-fmt-video=width={self.width},height={self.height},pixelformat=MJPG',
                                            f'--set-ctrl=brightness={self.brightness}',
                                            f'--set-ctrl=contrast={self.contrast}',
                                            f'--set-ctrl=saturation={self.saturation}',
                                            f'--set-ctrl=sharpness={self.sharpness}',
                                            f'--set-ctrl=exposure_auto={self.exposure_auto}',
                                            f'--set-ctrl=exposure_absolute={self.exposure_absolute}',
                                            f'--set-ctrl=white_balance_temperature_auto={self.white_balance_auto}',
                                            f'--set-ctrl=white_balance_temperature={self.white_balance_temperature}'
                                        ])
                                        time.sleep(0.5)  # 稍微减少等待时间，因为设备已经被验证
                                        logger.info(f"Camera {device_num} ({current_device}) initialized with parameters")
                                    except Exception as e:
                                        logger.warning(f"Failed to configure camera {device}: {e}")
                                        # Fall back to default resolution
                                        self.width = 640
                                        self.height = 480
                            except Exception as e:
                                logger.warning(f"Could not check device {device}: {e}")
                else:
                    logger.warning("Failed to list video devices using v4l2-ctl")
                    # 回退到传统的设备检测方法
                    devices = os.listdir('/dev')
                    video_devices = [d for d in devices if d.startswith('video')]
                    for device in sorted(video_devices):
                        try:
                            device_num = int(device.replace('video', ''))
                            self.camera_indices.append(device_num)
                        except Exception as e:
                            logger.warning(f"Could not check device {device}: {e}")
            except Exception as e:
                logger.warning(f"Could not list video devices: {e}")
        else:  # Windows
            try:
                # 使用 FFmpeg 列出 DirectShow 设备
                result = subprocess.run(
                    [self.ffmpeg_path, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 解析输出查找摄像头设备
                found_video_devices = False
                for line in result.stderr.split('\n'):
                    if 'DirectShow video devices' in line:
                        found_video_devices = True
                        continue
                    if found_video_devices:
                        if 'DirectShow audio devices' in line:
                            break
                        if '(video)' in line and '"' in line:
                            # 提取设备名称
                            device_name = line.split('"')[1]
                            self.camera_indices.append(device_name)
                            logger.info(f"Found DirectShow camera: {device_name}")
                
                if not self.camera_indices:
                    logger.warning("No DirectShow devices found, falling back to numeric indices")
                    # 回退到基本检测
                    for i in range(10):
                        cap = cv2.VideoCapture(i)
                        if cap.isOpened():
                            self.camera_indices.append(str(i))  # 存储为字符串
                            cap.release()
                
            except Exception as e:
                logger.warning(f"Failed to detect DirectShow cameras: {e}")
                self.camera_indices = ['0']  # 默认使用 camera 0

        if not self.camera_indices:
            logger.warning("No cameras were detected!")
        else:
            logger.info(f"Detected cameras: {self.camera_indices}")

    def _load_camera_config(self):
        """Load camera configuration from environment variables"""
        logger.debug("Loading camera configuration")
        
        # Get requested resolution from env or use defaults
        self.width = int(os.getenv('CAMERA_WIDTH', '1080'))
        self.height = int(os.getenv('CAMERA_HEIGHT', '720'))
        self.fps = os.getenv('CAMERA_FPS', '30')
        self.jpeg_quality = os.getenv('CAMERA_JPEG_QUALITY', '95')
        
        # Camera control parameters
        self.brightness = int(os.getenv('CAMERA_BRIGHTNESS', '128'))
        self.contrast = int(os.getenv('CAMERA_CONTRAST', '128'))
        self.saturation = int(os.getenv('CAMERA_SATURATION', '128'))
        self.sharpness = int(os.getenv('CAMERA_SHARPNESS', '128'))
        self.exposure_auto = int(os.getenv('CAMERA_EXPOSURE_AUTO', '1'))
        self.exposure_absolute = int(os.getenv('CAMERA_EXPOSURE_ABSOLUTE', '250'))
        self.white_balance_auto = int(os.getenv('CAMERA_WHITE_BALANCE_AUTO', '0'))
        self.white_balance_temperature = int(os.getenv('CAMERA_WHITE_BALANCE_TEMP', '5000'))
        
        logger.info(f"Camera config loaded: {self.width}x{self.height} @{self.fps}fps, quality:{self.jpeg_quality}")
        logger.debug(f"Camera control parameters loaded: brightness={self.brightness}, contrast={self.contrast}, "
                    f"saturation={self.saturation}, sharpness={self.sharpness}, exposure_auto={self.exposure_auto}, "
                    f"exposure_absolute={self.exposure_absolute}, white_balance_auto={self.white_balance_auto}, "
                    f"white_balance_temperature={self.white_balance_temperature}")

    def take_photo(self, camera_id, save_path=None):
        """
        Take a photo using FFmpeg from a specific camera
        
        Args:
            camera_id (int): Camera index to capture from
            save_path (str, optional): Path to save the captured image. 
                                     If None, a default path will be used.
        
        Returns:
            tuple: (saved_path, success)
                - saved_path (str): Path of the saved image file
                - success (bool): True if successful, False otherwise
        """
        try:
            if not save_path:
                # 生成默认的保存路径
                now = datetime.now()
                date_folder = now.strftime("%Y%m%d")
                filename = f"Unknown-Camera{camera_id}-{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                
                # 确保目录存在，使用绝对路径
                save_dir = os.path.abspath(os.path.join("static", "screenshots", date_folder))
                os.makedirs(save_dir, exist_ok=True)
                
                save_path = os.path.join(save_dir, filename)
                # 确保使用正斜杠
                save_path = save_path.replace('\\', '/')
            else:
                # 如果提供了保存路径，也确保目录存在
                save_dir = os.path.dirname(os.path.abspath(save_path))
                os.makedirs(save_dir, exist_ok=True)
                save_path = save_path.replace('\\', '/')
            
            logger.info(f"Taking photo with FFmpeg from camera {camera_id}, saving to: {save_path}")
            
            # Check if camera exists (Linux only)
            if os.name == 'posix':
                device_path = f"/dev/video{camera_id}"
                if not os.path.exists(device_path):
                    logger.error(f"Camera device {device_path} not found")
                    return None, False
            
            # 构建FFmpeg命令
            command = [
                self.ffmpeg_path,
                '-y',  # 覆盖现有文件
            ]

            if os.name == 'posix':  # Linux
                command.extend([
                    '-f', 'video4linux2',
                    '-input_format', 'yuyv422',
                    '-i', f'/dev/video{camera_id}',
                    '-frames', '1',
                    '-pix_fmt', 'yuvj444p',
                    '-vf', 'unsharp=3:3:1.0',
                    '-video_size', f'{self.width}x{self.height}',
                    '-framerate', self.fps,
                    '-qscale:v', str(int(100/int(self.jpeg_quality))),
                    save_path
                ])
            else:  # Windows
                # 构建 Windows 专用的命令
                device_name = f'video={camera_id}' if isinstance(camera_id, (int, str)) else camera_id
                command.extend([
                    '-f', 'dshow',
                    '-video_size', f'{self.width}x{self.height}',
                    '-framerate', self.fps,
                    '-i', device_name,
                    '-frames:v', '1',
                    '-vcodec', 'mjpeg',
                    '-qscale:v', '2',
                    save_path
                ])

            logger.debug(f"Executing FFmpeg command: {' '.join(command)}")
            
            # 执行命令并捕获输出
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"Photo captured successfully from camera {camera_id}")
                # Log full FFmpeg output for debugging
                logger.debug(f"FFmpeg output:\n{result.stderr}")
                return save_path, True
            else:
                logger.error(f"FFmpeg capture failed for camera {camera_id}. Full output:\n{result.stderr}")
                return None, False

        except Exception as e:
            logger.exception(f"Error taking photo with FFmpeg from camera {camera_id}: {str(e)}")
            return None, False

    def take_photo_all_cameras(self, position_info, timestamp):
        """
        Capture photos from all connected cameras
        
        Args:
            position_info (str): Position information to be included in the filename
            timestamp (str): Timestamp for the photo capture

        Returns:
            dict: A dictionary containing:
                - status: "OK" or "ERROR"
                - timestamp: The timestamp when photos were taken
                - position: The provided position information
                - results: List of results for each camera
        """
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if timestamp is None:
            timestamp = str(int(time.time()))


        date_str = datetime.now().strftime("%Y%m%d")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        if not position_info:
            position_info = "Unknown"

        try:
            # 确保至少有一个摄像头被检测到
            if not self.camera_indices:
                self._detect_cameras()
                if not self.camera_indices:
                    raise RuntimeError("No cameras detected")

            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_str = datetime.now().strftime("%Y%m%d")
            
            # 使用绝对路径并确保目录存在
            base_dir = os.path.abspath(os.path.join("static", "screenshots", date_str))
            os.makedirs(base_dir, exist_ok=True)
            
            if not position_info:
                position_info = "Unknown"

            results = []
            overall_status = "OK"
            error_message = None

            # 遍历所有检测到的摄像头
            for camera_id in self.camera_indices:
                try:
                    filename = f"{position_info}-Camera{camera_id}-{timestamp}.jpg"
                    filepath = os.path.join(base_dir, filename)
                    # 确保使用正斜杠
                    filepath = filepath.replace('\\', '/')
                    
                    saved_path, success = self.take_photo(camera_id, filepath)
                    
                    if success:
                        results.append({
                            "camera_id": camera_id,
                            "status": "OK",
                            "filename": filename,
                            "filepath": filepath
                        })
                    else:
                        overall_status = "ERROR"
                        results.append({
                            "camera_id": camera_id,
                            "status": "ERROR",
                            "message": f"Failed to capture photo from camera {camera_id}"
                        })
                except Exception as e:
                    logger.exception(f"Error capturing from camera {camera_id}")
                    overall_status = "ERROR"
                    results.append({
                        "camera_id": camera_id,
                        "status": "ERROR",
                        "message": str(e)
                    })

            return {
                "status": overall_status,
                "message": error_message if error_message else None,
                "timestamp": timestamp,
                "position": position_info,
                "results": results
            }
                
        except Exception as e:
            logger.exception(f"Error in take_photo_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": []
            }

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        logger.info("Initialized FFmpeg camera control with Flask app")

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up FFmpeg camera control")
        # FFmpeg不需要特别的清理操作，但保留此方法以保持接口一致性
