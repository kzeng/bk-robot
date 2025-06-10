# OpenCV Control Class for handling image processing tasks using OpenCV
# implement all features that obs_control.py has

import os
import cv2
import time
import queue
import numpy as np
import subprocess
from datetime import datetime
from threading import Thread, Lock, Event
from PIL import Image, ImageDraw, ImageFont
from flask import current_app

class CameraStatus:
    def __init__(self):
        self.frame_count = 0
        self.dropped_frames = 0
        self.last_frame_time = time.time()
        self.fps = 0.0
        self.is_connected = False
        self.last_error = None
        self.lock = Lock()

    def update_fps(self):
        current_time = time.time()
        with self.lock:
            time_diff = current_time - self.last_frame_time
            if time_diff > 0:
                self.fps = 1.0 / time_diff
            self.last_frame_time = current_time
            self.frame_count += 1

    def record_drop(self):
        with self.lock:
            self.dropped_frames += 1

    def get_stats(self):
        with self.lock:
            return {
                'frame_count': self.frame_count,
                'dropped_frames': self.dropped_frames,
                'fps': round(self.fps, 2),
                'is_connected': self.is_connected,
                'last_error': self.last_error
            }
            return {
                'frame_count': self.frame_count,
                'dropped_frames': self.dropped_frames,
                'fps': round(self.fps, 2),
                'is_connected': self.is_connected,
                'last_error': self.last_error
            }

class OpenCVControl:
    def __init__(self, app=None):
        self.app = app
        self.cameras = {}  
        self.camera_indices = []  
        self.recording = False
        self.recording_threads = {}
        self.recording_start_time = None
        self.recording_markers = None
        self.simulation_mode = False        # Camera monitoring
        self.camera_status = {}
        self.frame_queues = {}
        self.frame_threads = {}
        self.stop_events = {}
        
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize app configuration and detect cameras"""
        self.app = app
        self.config = app.config.get('CAMERA_CONFIG', {
            'resolution': {
                'width': int(app.config.get('CAMERA_WIDTH', 1920)),
                'height': int(app.config.get('CAMERA_HEIGHT', 1080))
            },
            'fps': int(app.config.get('CAMERA_FPS', 30)),
            'jpeg_quality': int(app.config.get('JPEG_QUALITY', 95)),
            'buffer_size': int(app.config.get('CAMERA_BUFFER_SIZE', 10)),
            'enable_monitoring': True
        })
        
        # Get list of available video devices
        self.camera_indices = []
        camera_paths = []
        
        # Find all video devices
        try:
            devices = os.listdir('/dev')
            video_devices = [d for d in devices if d.startswith('video')]
            for device in sorted(video_devices):
                try:
                    device_path = f"/dev/{device}"
                    # Check if device is a capture device
                    result = subprocess.run(
                        ['v4l2-ctl', '-d', device_path, '--info'],
                        capture_output=True,
                        text=True
                    )
                    if 'Video Capture' in result.stdout:
                        camera_paths.append(device_path)
                except Exception:
                    continue
        except Exception as e:
            self._log('error', f"Error enumerating video devices: {e}")
            
        self._log('info', f"Found video capture devices: {camera_paths}")
        
        # Initialize each camera
        with app.app_context():
            for device_path in camera_paths:
                try:
                    device_num = int(device_path.replace('/dev/video', ''))
                    self._configure_v4l2_device(device_path)
                    
                    # Try opening with OpenCV using V4L2 backend
                    cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
                    if not cap.isOpened():
                        self._log('warning', f"Failed to open {device_path}")
                        continue
                        
                    # Configure format and buffer for high quality
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['resolution']['width'])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['resolution']['height'])
                    cap.set(cv2.CAP_PROP_FPS, self.config['fps'])
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Smaller buffer for fresher frames
                    
                    # Test frame capture
                    for _ in range(5):  # Capture a few frames to let the camera adjust
                        ret, frame = cap.read()
                    if ret and frame is not None:
                        self.camera_indices.append(device_num)
                        self._log('info', f"Successfully initialized {device_path}")
                    else:
                        self._log('warning', f"Could not capture frame from {device_path}")
                    cap.release()
                    
                except Exception as e:
                    self._log('error', f"Error initializing {device_path}: {e}")
                    
            if not self.camera_indices:
                self._log('warning', "No cameras were detected!")
            else:
                self._log('info', f"Detected cameras: {self.camera_indices}")

    def _get_v4l2_devices(self):
        """Get information about available V4L2 devices"""
        try:
            result = subprocess.run(
                ['v4l2-ctl', '--list-devices'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self._log('error', f"v4l2-ctl command failed: {e}")
        except FileNotFoundError:
            self._log('warning', "v4l2-ctl not found. Install v4l-utils package")
        except Exception as e:
            self._log('error', f"Error getting V4L2 devices: {e}")
        return None

    def _configure_v4l2_device(self, device_path):
        """Configure V4L2 device settings for optimal image quality"""
        try:
            # Get device info and check for MagicView cameras
            info_result = subprocess.run(
                ['v4l2-ctl', '-d', device_path, '--info'],
                capture_output=True,
                text=True
            )
            is_magicview = 'MagicView' in info_result.stdout
            if is_magicview:
                self._log('info', f"Detected MagicView camera at {device_path}")
            
            # Get supported formats and choose the best one
            formats_result = subprocess.run(
                ['v4l2-ctl', '-d', device_path, '--list-formats-ext'],
                capture_output=True,
                text=True
            )
            # Prefer MJPG format for better quality
            if 'MJPG' in formats_result.stdout:
                subprocess.run(['v4l2-ctl', '-d', device_path, '--set-fmt-video=width=1920,height=1080,pixelformat=MJPG'])
            elif 'YUYV' in formats_result.stdout:
                subprocess.run(['v4l2-ctl', '-d', device_path, '--set-fmt-video=width=1920,height=1080,pixelformat=YUYV'])
            
            # Get available controls
            ctrl_result = subprocess.run(
                ['v4l2-ctl', '-d', device_path, '--list-ctrls'],
                capture_output=True,
                text=True
            )
            controls = ctrl_result.stdout.lower()
            
            # # Configure image quality settings for MagicView cameras
            # try:
            #     if is_magicview:
            #         # 1. 基础图像参数优化
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=32'])      # 降低亮度避免过曝
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=48'])        # 适中对比度
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=64'])      # 适中饱和度
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=sharpness=5'])        # 适度锐化
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gamma=100'])          # 标准伽马值
                    
            #         # 2. 曝光设置优化
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=auto_exposure=1'])    # 手动曝光模式
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=exposure_time_absolute=100'])  # 减少曝光时间
                    
            #         # 3. 白平衡与色彩优化
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_automatic=0'])    # 手动白平衡
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_temperature=4600'])  # 室内色温
                    
            #         # 4. 对焦和其他优化
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_automatic_continuous=0']) # 关闭自动对焦
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_absolute=250'])          # 固定对焦距离
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gain=50'])                     # 降低增益
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=backlight_compensation=1'])    # 开启背光补偿
            #         subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=power_line_frequency=1'])      # 设置电源频率为50Hz
                    
            #         self._log('info', f"MagicView camera parameters optimized for {device_path}")
            #     else:
            #         # Generic camera settings
            #         if 'brightness' in controls:
            #             subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=128'])
            #         if 'contrast' in controls:
            #             subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=128'])
            #         if 'saturation' in controls:
            #             subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=128'])
            # except:
            #     self._log('warning', f"Some controls could not be set for {device_path}")


            # kzeng-optimized
            # Configure image quality settings for MagicView cameras in library environment
            try:
                if is_magicview:
                    # 1. 基础图像参数
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=16'])      # 降低亮度避免过曝
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=40'])        # 适中对比增强文字
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=80'])      # 增强书封色彩
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=sharpness=6'])        # 最大锐化提升文字
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gamma=120'])          # 优化中灰对比
                    
                    # 2. 曝光设置
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=auto_exposure=1'])    # 手动曝光模式
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=exposure_time_absolute=80'])  # 缩短曝光时间
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gain=20'])            # 降低增益减少噪点
                    
                    # 3. 白平衡
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_automatic=0'])    # 手动白平衡
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_temperature=5000'])  # 图书馆光线
                    
                    # 4. 对焦及其他设置
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_automatic_continuous=0'])  # 手动对焦
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_absolute=200'])           # 优化书架距离
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=backlight_compensation=0'])     # 关闭背光补偿
                    subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=power_line_frequency=1'])       # 50 Hz
                    
                    self._log('info', f"MagicView camera parameters optimized for {device_path} in library lighting")
                else:
                    # 通用相机设置
                    if 'brightness' in controls:
                        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=128'])
                    if 'contrast' in controls:
                        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=128'])
                    if 'saturation' in controls:
                        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=128'])
            except:
                self._log('warning', f"Some controls could not be set for {device_path}")
            
            self._log('info', f"Image quality settings configured for {device_path}")
            return True
            
        except Exception as e:
            self._log('error', f"Failed to configure V4L2 device {device_path}: {e}")
            return False

    def _log(self, level, message):
        """Log messages using the app logger"""
        if hasattr(self, 'app') and self.app:
            logger = self.app.logger
        else:
            # Fallback to print if app logger is not available
            print(f"[{level}] {message}")
            return
            
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)

    def take_screenshot_all_cameras(self, position_info):
        """Capture screenshots from all connected cameras with high quality"""
        if self.simulation_mode:
            return {
                "status": "OK",
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "position": position_info,
                "results": []
            }

        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_str = datetime.now().strftime("%Y%m%d")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        if not position_info:
            position_info = "Unknown"

        try:
            # Ensure cameras are connected
            if not self.cameras:
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    raise RuntimeError(connect_result["message"])

            for camera_id in self.cameras.keys():
                try:
                    # Wait for a frame, with timeout
                    frame = None
                    wait_start = time.time()
                    while frame is None and (time.time() - wait_start) < 2.0:
                        frame = self.get_latest_frame(camera_id)
                        if frame is None:
                            time.sleep(0.1)

                    if frame is None:
                        raise RuntimeError("No frame available in buffer after waiting")

                    filename = f"{position_info}-Camera{camera_id}-{timestamp}.jpg"
                    filepath = os.path.join(base_dir, filename)
                    # Fix: ensure filepath uses web URL format
                    filepath = filepath.replace("\\", "/")
                    abs_filepath = os.path.abspath(filepath)

                    # Save with maximum JPEG quality and additional settings
                    params = [
                        cv2.IMWRITE_JPEG_QUALITY, 100,  # 使用最高JPEG质量
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1,   # 启用JPEG优化
                        cv2.IMWRITE_JPEG_PROGRESSIVE, 1, # 使用渐进式JPEG

                        # 额外的JPEG参数, kzeng-optimized 
                        cv2.IMWRITE_JPEG_LUMA_QUALITY, 100, # 亮度质量
                        cv2.IMWRITE_JPEG_CHROMA_QUALITY, 100, # 色度质量
                        cv2.IMWRITE_JPEG_SAMPLING_FACTOR, 1111 # 4:4:4采样,不降采样
                    ]
                    cv2.imwrite(abs_filepath, frame, params)

                    results.append({
                        "camera_id": camera_id,
                        "status": "OK",
                        "filename": filename,
                        "filepath": filepath
                    })
                except Exception as e:
                    self._log('error', f"Error capturing from camera {camera_id}: {str(e)}")
                    results.append({
                        "camera_id": camera_id,
                        "status": "ERROR",
                        "message": str(e)
                    })

            return {
                "status": "OK",
                "timestamp": timestamp,
                "position": position_info,
                "results": results
            }

        except Exception as e:
            self._log('error', f"Error in take_screenshot_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": []
            }

    def connect(self):
        """Connect to available cameras and configure them for HD recording"""
        try:
            if self.simulation_mode:
                return {"status": "OK", "message": "Connected in simulation mode"}

            # Close any existing connections first
            self.close()
            
            successful_connects = []
            failed_connects = []

            for idx in self.camera_indices:
                try:
                    device_path = f"/dev/video{idx}"
                    self._log('info', f"Connecting to camera {idx}")
                    
                    # Configure V4L2 settings first
                    self._configure_v4l2_device(device_path)
                    
                    # Try opening with OpenCV
                    cap = cv2.VideoCapture(idx)
                    if not cap.isOpened():
                        failed_connects.append(idx)
                        self._log('error', f"Failed to connect to camera {idx}")
                        continue

                    # Configure camera settings
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['resolution']['width'])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['resolution']['height'])
                    cap.set(cv2.CAP_PROP_FPS, self.config['fps'])
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                    
                    # Test frame capture
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        self.cameras[idx] = cap
                        successful_connects.append(idx)
                        
                        # Initialize monitoring
                        self.frame_queues[idx] = queue.Queue(maxsize=self.config['buffer_size'])
                        self.camera_status[idx] = CameraStatus()
                        self.stop_events[idx] = Event()
                        
                        # Start frame grabber thread
                        self._start_frame_grabber(idx, cap)
                        
                        self._log('info', f"Successfully connected to camera {idx}")
                    else:
                        cap.release()
                        failed_connects.append(idx)
                        self._log('error', f"Could not capture test frame from camera {idx}")
                        
                except Exception as e:
                    failed_connects.append(idx)
                    self._log('error', f"Error connecting to camera {idx}: {str(e)}")
            
            if not successful_connects:
                return {
                    "status": "ERROR",
                    "message": f"No cameras connected successfully. Failed attempts: {failed_connects}"
                }

            status_msg = f"Connected to {len(successful_connects)} cameras"
            if failed_connects:
                status_msg += f". Failed to connect to cameras: {failed_connects}"

            return {
                "status": "OK",
                "message": status_msg,
                "cameras": successful_connects
            }
        except Exception as e:
            self._log('error', f"Error in connect(): {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    def get_latest_frame(self, camera_id):
        """Get the most recent frame from a camera's buffer"""
        if camera_id not in self.frame_queues:
            return None
        
        try:
            # Clear queue until the most recent frame
            while self.frame_queues[camera_id].qsize() > 1:
                try:
                    self.frame_queues[camera_id].get_nowait()
                except queue.Empty:
                    break
            return self.frame_queues[camera_id].get_nowait()
        except queue.Empty:
            return None

    def _start_frame_grabber(self, camera_id, cap):
        """Start a thread to continuously grab frames from the camera"""
        def grab_frames():
            while not self.stop_events[camera_id].is_set():
                ret, frame = cap.read()
                if ret:
                    # Update status
                    self.camera_status[camera_id].update_fps()
                    self.camera_status[camera_id].is_connected = True
                    
                    # Add frame to queue, dropping oldest if full
                    try:
                        if self.frame_queues[camera_id].full():
                            self.frame_queues[camera_id].get_nowait()
                            self.camera_status[camera_id].record_drop()
                        self.frame_queues[camera_id].put_nowait(frame)
                    except queue.Full:
                        self.camera_status[camera_id].record_drop()
                else:
                    self.camera_status[camera_id].is_connected = False
                    self.camera_status[camera_id].last_error = "Failed to read frame"
                    time.sleep(0.1)  # Prevent tight loop on error

        thread = Thread(target=grab_frames, daemon=True)
        self.frame_threads[camera_id] = thread
        thread.start()

    def close(self):
        """Release all camera resources"""
        # Stop frame grabber threads
        for camera_id in self.stop_events:
            self.stop_events[camera_id].set()
        
        # Wait for threads to finish
        for thread in self.frame_threads.values():
            thread.join(timeout=5.0)
        
        # Clear frame queues
        for queue in self.frame_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except queue.Empty:
                    pass
        
        # Release camera resources
        for cap in self.cameras.values():
            cap.release()
        
        # Clear all containers
        self.cameras.clear()
        self.frame_queues.clear()
        self.frame_threads.clear()
        self.stop_events.clear()
        self.camera_status.clear()

