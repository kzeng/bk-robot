# OpenCV Control Class for handling image processing tasks using OpenCV
# implement all features that obs_control.py has

import os
import cv2
import time
import queue
import numpy as np
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

class OpenCVControl:
    def __init__(self, app=None):
        self.app = app
        self.cameras = {}  # Dictionary mapping camera index to capture object
        self.camera_indices = []  # List of camera indices to use
        self.recording = False  # Recording state
        self.recording_threads = {}  # Threads for recording from each camera
        self.recording_start_time = None
        self.recording_markers = None
        self.simulation_mode = False

        # Camera status monitoring
        self.camera_status = {}  # Dictionary mapping camera index to CameraStatus
        self.frame_queues = {}  # Dictionary mapping camera index to frame queue
        self.frame_threads = {}  # Dictionary mapping camera index to frame grabber thread
        self.stop_events = {}  # Dictionary mapping camera index to stop event

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize app configuration and detect available cameras"""
        # Get camera configuration from app config
        self.config = app.config.get('CAMERA_CONFIG', {
            'resolution': {'width': 1920, 'height': 1080},
            'fps': 30,
            'jpeg_quality': 95,
            'buffer_size': 10,
            'enable_monitoring': True
        })
        self.camera_indices = self._detect_cameras()

    def _detect_cameras(self):
        """Detect available cameras in the system"""
        camera_indices = []
        for i in range(10):  # Check first 10 possible camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                camera_indices.append(i)
                cap.release()
        return camera_indices

    def _configure_camera(self, cap, camera_id):
        """Configure camera with high-definition settings"""
        width = self.config['resolution']['width']
        height = self.config['resolution']['height']
        fps = self.config['fps']

        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Verify settings were applied
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        
        current_app.logger.info(f"Camera {camera_id} configured: {actual_width}x{actual_height} @ {actual_fps}fps")
        
        # Initialize frame queue and status monitoring
        self.frame_queues[camera_id] = queue.Queue(maxsize=self.config['buffer_size'])
        self.camera_status[camera_id] = CameraStatus()
        self.stop_events[camera_id] = Event()

        # Start frame grabber thread
        self._start_frame_grabber(camera_id, cap)

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

    def connect(self):
        """Connect to available cameras and configure them for HD recording"""
        try:
            if self.simulation_mode:
                return {"status": "OK", "message": "Connected in simulation mode"}

            for idx in self.camera_indices:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    self._configure_camera(cap, idx)
                    self.cameras[idx] = cap
            
            if not self.cameras:
                return {
                    "status": "ERROR",
                    "message": "No cameras found"
                }

            return {
                "status": "OK",
                "message": f"Connected to {len(self.cameras)} cameras",
                "cameras": list(self.cameras.keys())
            }
        except Exception as e:
            current_app.logger.error(f"Error connecting to cameras: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    def get_camera_status(self, camera_id=None):
        """Get status information for one or all cameras"""
        if camera_id is not None:
            if camera_id in self.camera_status:
                return self.camera_status[camera_id].get_stats()
            return None
        
        return {idx: status.get_stats() for idx, status in self.camera_status.items()}

    def get_latest_frame(self, camera_id):
        """Get the most recent frame from a camera's buffer"""
        if camera_id not in self.frame_queues:
            return None
        
        try:
            # Clear queue until the most recent frame
            while self.frame_queues[camera_id].qsize() > 1:
                self.frame_queues[camera_id].get_nowait()
            return self.frame_queues[camera_id].get_nowait()
        except queue.Empty:
            return None

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
                    # Get the latest frame from the buffer
                    frame = self.get_latest_frame(camera_id)
                    if frame is None:
                        raise RuntimeError("No frame available in buffer")

                    filename = f"{position_info}-Camera{camera_id}-{timestamp}.jpg"
                    filepath = os.path.join(base_dir, filename)
                    abs_filepath = os.path.abspath(filepath)

                    # Save with configured JPEG quality
                    cv2.imwrite(abs_filepath, frame, 
                              [cv2.IMWRITE_JPEG_QUALITY, self.config['jpeg_quality']])

                    results.append({
                        "camera_id": camera_id,
                        "status": "OK",
                        "filename": filename,
                        "filepath": filepath
                    })
                except Exception as e:
                    current_app.logger.error(f"Error capturing from camera {camera_id}: {str(e)}")
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
            current_app.logger.error(f"Error in take_screenshot_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": []
            }

    def _record_camera(self, camera_id, output_path):
        """Record video from a single camera using the frame buffer"""
        try:
            # Get initial frame to setup video writer
            frame = self.get_latest_frame(camera_id)
            if frame is None:
                raise RuntimeError("No frame available to start recording")

            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, self.config['fps'], (width, height))

            # Write the initial frame
            out.write(frame)
            
            while self.recording:
                frame = self.get_latest_frame(camera_id)
                if frame is not None:
                    out.write(frame)
                else:
                    time.sleep(1.0 / self.config['fps'])  # Wait for next frame
                    
        except Exception as e:
            current_app.logger.error(f"Error recording from camera {camera_id}: {str(e)}")
        finally:
            if 'out' in locals():
                out.release()

    def start_recording(self, marker_names=None):
        """Start recording on all cameras"""
        if self.simulation_mode:
            return {
                "status": "OK",
                "message": "Recording started in simulation mode",
                "timestamp": time.time()
            }

        try:
            if not self.cameras:
                connect_result = self.connect()
                if connect_result["status"] != "OK":
                    return connect_result

            if self.recording:
                return {
                    "status": "ERROR",
                    "message": "Recording is already in progress",
                    "timestamp": time.time()
                }

            self.recording = True
            self.recording_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.recording_markers = "_".join(marker_names) if marker_names else ""

            # Create output directory
            date_str = datetime.now().strftime("%Y%m%d")
            output_dir = os.path.join("static", "videos", date_str)
            os.makedirs(output_dir, exist_ok=True)

            # Start recording threads for each camera
            for camera_id in self.cameras.keys():
                filename = f"{self.recording_markers}_Camera{camera_id}_{self.recording_start_time}.avi"
                output_path = os.path.join(output_dir, filename)
                
                thread = Thread(target=self._record_camera, args=(camera_id, output_path))
                thread.daemon = True
                thread.start()
                self.recording_threads[camera_id] = thread

            return {
                "status": "OK",
                "message": "Recording started",
                "timestamp": time.time()
            }

        except Exception as e:
            self.recording = False
            current_app.logger.error(f"Error starting recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": time.time()
            }

    def stop_recording(self):
        """Stop recording on all cameras"""
        if self.simulation_mode:
            return {
                "status": "OK",
                "message": "Recording stopped in simulation mode",
                "timestamp": time.time()
            }

        try:
            if not self.recording:
                return {
                    "status": "ERROR",
                    "message": "No recording in progress",
                    "timestamp": time.time()
                }

            self.recording = False
            
            # Wait for all recording threads to finish
            for thread in self.recording_threads.values():
                thread.join(timeout=5.0)
            
            self.recording_threads.clear()

            return {
                "status": "OK",
                "message": "Recording stopped",
                "timestamp": time.time()
            }

        except Exception as e:
            current_app.logger.error(f"Error stopping recording: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": time.time()
            }

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

