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
from .camera_control import CameraControl

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
        self.camera_controls = {} # 新增: 相机控制对象字典
        self.camera_indices = []  
        self.recording = False
        self.recording_threads = {}
        self.recording_start_time = None
        self.recording_markers = None
        self.simulation_mode = False
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
            'enable_monitoring': True,
            'control_params': {}
        })
        
        # Get list of available video devices
        self.camera_indices = []
        camera_paths = []
        
        # Find all video devices
        if os.name == 'posix':  # Linux
            try:
                devices = os.listdir('/dev')
                video_devices = [d for d in devices if d.startswith('video')]
                for device in sorted(video_devices):
                    try:
                        device_path = f"/dev/{device}"
                        camera_paths.append(device_path)
                        self.camera_indices.append(device_path)
                    except Exception as e:
                        self._log("warning", f"Could not open {device_path}: {e}")
            except Exception as e:
                self._log("warning", f"Could not list video devices: {e}")
        else:  # Windows
            for i in range(10):  # Try first 10 camera indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.camera_indices.append(i)
                    camera_paths.append(str(i))
                    cap.release()

        # Initialize cameras and their controls
        for cam_path in camera_paths:
            try:
                cam_control = CameraControl(cam_path)
                cam_control.open()
                # Set initial parameters
                if 'control_params' in self.config:
                    cam_control.set_params(self.config['control_params'])
                self.camera_controls[cam_path] = cam_control
            except Exception as e:
                self._log("warning", f"Could not initialize camera {cam_path}: {e}")
                continue

        # Start camera monitoring if enabled
        if self.config.get('enable_monitoring', False):
            self.start_monitoring()
            

    def _log(self, level, msg):
        """Simple logger for OpenCVControl"""
        print(f"[{level.upper()}] {msg}")


    def update_camera_params(self, camera_id, params):
        """Update camera parameters
        Args:
            camera_id: Camera ID or path
            params: Dictionary of parameter name-value pairs
        """
        if camera_id in self.camera_controls:
            cam_control = self.camera_controls[camera_id]
            cam_control.set_params(params)
        else:
            raise ValueError(f"Camera {camera_id} not found")

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
                    
                    # 仅在Linux下配置V4L2
                    if os.name == 'posix':
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

