"""
FFmpeg based camera control implementation
"""
import os
import subprocess
from datetime import datetime
from loguru import logger

class FFmpegCameraControl:
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
                        # 验证设备是否可用
                        test_command = [
                            'ffmpeg',
                            '-f', 'video4linux2',
                            '-i', f'/dev/video{device_num}',
                            '-t', '0.1',  # 只测试0.1秒
                            '-f', 'null',
                            '-'
                        ]
                        result = subprocess.run(test_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if result.returncode == 255:  # FFmpeg在快速退出时返回255
                            self.camera_indices.append(device_num)
                    except Exception as e:
                        logger.warning(f"Could not check device {device}: {e}")
            except Exception as e:
                logger.warning(f"Could not list video devices: {e}")
        else:  # Windows
            for i in range(10):  # 尝试前10个摄像头索引
                test_command = [
                    'ffmpeg',
                    '-f', 'dshow',  # Windows使用DirectShow
                    '-i', f'video={i}',
                    '-t', '0.1',
                    '-f', 'null',
                    '-'
                ]
                try:
                    result = subprocess.run(test_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if result.returncode == 255:  # FFmpeg在快速退出时返回255
                        self.camera_indices.append(i)
                except Exception:
                    continue

        if not self.camera_indices:
            logger.warning("No cameras were detected!")
        else:
            logger.info(f"Detected cameras: {self.camera_indices}")

    def _load_camera_config(self):
        """Load camera configuration from environment variables"""
        logger.debug("Loading camera configuration")
        # 从环境变量加载摄像头配置
        self.width = os.getenv('CAMERA_WIDTH', '1920')
        self.height = os.getenv('CAMERA_HEIGHT', '1080')
        self.fps = os.getenv('CAMERA_FPS', '30')
        self.jpeg_quality = os.getenv('CAMERA_JPEG_QUALITY', '100')
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
                
            command.extend([
                '-vframes', '1',  # 只捕获一帧
                '-video_size', f'{self.width}x{self.height}',  # 设置分辨率
                '-framerate', self.fps,  # 设置帧率
                '-qscale:v', str(int(100/int(self.jpeg_quality))),  # 设置质量
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
                return save_path, True
            else:
                logger.error(f"FFmpeg capture failed for camera {camera_id}: {result.stderr}")
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

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up FFmpeg camera control")
        # FFmpeg不需要特别的清理操作，但保留此方法以保持接口一致性
