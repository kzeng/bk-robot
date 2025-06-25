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
        self._detect_cameras()
        self._load_camera_config()

    def _detect_cameras(self):
        """检测系统中可用的摄像头"""
        logger.info("Detecting available cameras...")
        if os.name == 'posix':  # Linux
            try:
                devices = os.listdir('/dev')
                video_devices = [d for d in devices if d.startswith('video')]
                for device in sorted(video_devices):
                    try:
                        device_num = int(device.replace('video', ''))
                        # 更可靠的设备检测方式
                        cap = cv2.VideoCapture(device_num)
                        if cap.isOpened():
                            self.camera_indices.append(device_num)
                            cap.release()
                    except Exception as e:
                        logger.warning(f"Could not check device {device}: {e}")
            except Exception as e:
                logger.warning(f"Could not list video devices: {e}")
        else:  # Windows
            for i in range(10):  # 尝试前10个摄像头索引
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.camera_indices.append(i)
                    cap.release()

        if not self.camera_indices:
            logger.warning("No cameras were detected!")
        else:
            logger.info(f"Detected cameras: {self.camera_indices}")

    def _load_camera_config(self):
        """Load camera configuration from environment variables"""
        logger.debug("Loading camera configuration")
        
        # Get requested resolution from env or use defaults
        self.width  = int(os.getenv('CAMERA_WIDTH', '1080'))
        self.height = int(os.getenv('CAMERA_HEIGHT', '720'))
        
        # # Camera hardware only supports up to 640x480
        # max_width = 640
        # max_height = 480
        
        # # Use requested resolution if supported, otherwise use max supported
        # self.width = str(min(req_width, max_width))
        # self.height = str(min(req_height, max_height))
        
        # if req_width > max_width or req_height > max_height:
        #     logger.warning(
        #         f"Requested resolution {req_width}x{req_height} not supported. "
        #         f"Using maximum supported resolution: {self.width}x{self.height}"
        #     )
            
        self.fps = os.getenv('CAMERA_FPS', '30')
        self.jpeg_quality = os.getenv('CAMERA_JPEG_QUALITY', '95')
        logger.info(f"Camera config loaded: {self.width}x{self.height} @{self.fps}fps, quality:{self.jpeg_quality}")

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
                
                # 确保目录存在
                save_dir = os.path.join("static", "screenshots", date_folder)
                os.makedirs(save_dir, exist_ok=True)
                
                save_path = os.path.join(save_dir, filename)
            
            logger.info(f"Taking photo with FFmpeg from camera {camera_id}, saving to: {save_path}")
            
            # Pre-configure camera using v4l2-ctl (Linux only)
            if os.name == 'posix':
                device_path = f"/dev/video{camera_id}"
                try:
                    # # Get supported formats and resolutions
                    # formats = subprocess.run(
                    #     ['v4l2-ctl', '-d', device_path, '--list-formats-ext'],
                    #     capture_output=True,
                    #     text=True
                    # ).stdout
                    
                    # # Try to set highest available resolution
                    # if '1920x1080' in formats:
                    #     target_width = 1920
                    #     target_height = 1080
                    # elif '1280x720' in formats:
                    #     target_width = 1280
                    #     target_height = 720
                    # else:
                    #     target_width = 640
                    #     target_height = 480

                    
                    # Set camera parameters
                    subprocess.run([
                        'v4l2-ctl', '-d', device_path,
                        f'--set-fmt-video=width={self.width},height={self.height},pixelformat=MJPG'
                    ])
                    subprocess.run([
                        'v4l2-ctl', '-d', device_path,
                        '--set-ctrl=brightness=128',
                        '--set-ctrl=contrast=128',
                        '--set-ctrl=saturation=128',
                        '--set-ctrl=sharpness=128',
                        '--set-ctrl=exposure_auto=1',
                        '--set-ctrl=exposure_absolute=250',
                        '--set-ctrl=white_balance_temperature_auto=0',
                        '--set-ctrl=white_balance_temperature=5000'
                    ])
                    time.sleep(1.0)  # Allow settings to stabilize
                    
                    # Update our resolution to match what we set
                    # self.width = str(target_width)
                    # self.height = str(target_height)
                    
                except Exception as e:
                    logger.warning(f"Failed to pre-configure camera {device_path}: {e}")
                    # Fall back to default resolution
                    self.width = '640'
                    self.height = '480'
            
            # 构建FFmpeg命令
            command = [
                'ffmpeg',
                '-y',  # 覆盖现有文件
            ]
            
            if os.name == 'posix':
                command.extend([
                    '-f', 'video4linux2',
                    '-i', f'/dev/video{camera_id}'
                ])
            else:  # Windows
                command.extend([
                    '-f', 'dshow',
                    '-i', f'video={camera_id}'
                ])
            
            # -input_format yuyv422 -qscale:v 1
            # ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -i /dev/video0 -frames 1 -c:v copy best_quality.jpg
            # command.extend([
            #     '-input_format', 'mjpeg',  # 明确指定输入格式
            #     '-pixel_format', 'yuvj420p',  # 指定像素格式
            #     '-vframes', '1',  # 只捕获一帧
            #     '-video_size', f'{self.width}x{self.height}',  # 设置分辨率
            #     '-framerate', self.fps,  # 设置帧率
            #     '-qscale:v', str(int(100/int(self.jpeg_quality))), 
            #     save_path  # 输出文件
            # ])

            # ffmpeg -f v4l2 -input_format yuyv422 -video_size 1280x720 -i /dev/video0 \
            #     -frames 1 -qscale:v 1 -pix_fmt yuvj444p -vf "unsharp=3:3:1.0" \
            #     -y best_photo.jpg
            command.extend([
                '-input_format', 'yuyv422',   
                '-frames', '1', 
                '-pix_fmt', 'yuvj444p',
                '-vf', 'unsharp=3:3:1.0',
                '-video_size', f'{self.width}x{self.height}',  # 设置分辨率
                '-framerate', self.fps,  # 设置帧率
                '-qscale:v', str(int(100/int(self.jpeg_quality))),
                save_path  # 输出文件
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

    def take_photo_all_cameras(self, position_info):
        """
        Capture photos from all connected cameras
        
        Args:
            position_info (str): Position information to be included in the filename

        Returns:
            dict: A dictionary containing:
                - status: "OK" or "ERROR"
                - timestamp: The timestamp when photos were taken
                - position: The provided position information
                - results: List of results for each camera
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

            results = []
            overall_status = "OK"
            error_message = None

            # 遍历所有检测到的摄像头
            for camera_id in self.camera_indices:
                try:
                    filename = f"{position_info}-Camera{camera_id}-{timestamp}.jpg"
                    filepath = os.path.join(base_dir, filename).replace("\\", "/")
                    
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
