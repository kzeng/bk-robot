# OpenCV Control Class for handling IP camera image capture
import os
import cv2
import time
from datetime import datetime
from flask import current_app
from app.utils.logger import configured_logger as logger
from app.models import MarkerConfig


class OpenCVControl:
    def __init__(self, app=None):
        self.app = app
        self.camera_urls = []  # List of RTSP camera URLs
        self.simulation_mode = False
        
        # Recording state management
        self.recording_cameras = {}  # Dictionary to track recording state per camera
        self.video_writers = {}  # Dictionary to store VideoWriter objects
        self.video_paths = {}  # Dictionary to store video paths
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize app configuration"""
        self.app = app
        self.config = app.config.get('CAMERA_CONFIG', {
            'resolution': {
                'width': int(os.environ.get('CAMERA_WIDTH', 2880)),
                'height': int(os.environ.get('CAMERA_HEIGHT', 1620))
            }
        })
        
        # Camera URLs should be set via set_camera_urls()
        self._log('info', "OpenCVControl initialized for IP cameras")

    def _log(self, level, msg):
        """Simple logger for OpenCVControl"""
        if level.lower() == 'info':
            logger.info(msg)
        elif level.lower() == 'warning':
            logger.warning(msg)
        elif level.lower() == 'error':
            logger.error(msg)
        else:
            logger.debug(msg)

    def set_camera_urls(self, urls):
        """Set the RTSP URLs for IP cameras"""
        self.camera_urls = urls
        self._log('info', f"Set {len(urls)} camera URLs")

    # def take_photo_all_cameras(self, position_info, timestamp):
    #     """Capture screenshots from all configured IP cameras with highest quality"""
    #     if self.simulation_mode:
    #         return {
    #             "status": "OK",
    #             "timestamp": str(int(time.time())),
    #             "position": position_info,
    #             "results": []
    #         }

    #     results = []

    #     if timestamp is None:
    #         timestamp = str(int(time.time()))

    #     date_str = datetime.now().strftime("%Y%m%d")
    #     base_dir = os.path.join("static", "screenshots", date_str)
    #     os.makedirs(base_dir, exist_ok=True)

    #     if not position_info:
    #         position_info = "Unknown"

    #     try:
    #         self._log('info', f"Starting capture for {len(self.camera_urls)} cameras")
    #         if not self.camera_urls:
    #             raise RuntimeError("No camera URLs configured - check .env CAMERA_URLS setting")

    #         for i, url in enumerate(self.camera_urls, start=1):
    #             self._log('debug', f"Attempting capture from camera {i} with URL: {url}")
    #             try:
    #                 # Open RTSP stream with timeout settings
    #                 self._log('debug', f"Opening RTSP stream for camera {i}")
    #                 cap = cv2.VideoCapture(url)
    #                 cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['resolution']['width'])
    #                 cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['resolution']['height'])
                    
    #                 # Set timeout for RTSP connection (5 seconds)
    #                 start_time = time.time()
    #                 while not cap.isOpened() and (time.time() - start_time) < 5:
    #                     time.sleep(0.1)
                    
    #                 if not cap.isOpened():
    #                     error_msg = f"Could not open camera {i} at {url} after 5 seconds"
    #                     self._log('error', error_msg)
    #                     raise RuntimeError(error_msg)
    #                 self._log('debug', f"Successfully opened camera {i} stream")

    #                 # Read multiple frames to allow buffer to fill
    #                 for _ in range(5):
    #                     ret, frame = cap.read()
    #                     if ret and frame is not None:
    #                         break
    #                     time.sleep(0.1)
                    
    #                 cap.release()

    #                 if not ret or frame is None:
    #                     error_msg = f"Failed to capture frame from camera {i} after multiple attempts"
    #                     self._log('error', error_msg)
    #                     raise RuntimeError(error_msg)
    #                 self._log('debug', f"Successfully captured frame from camera {i}")

    #                 # Generate filename in format: position-sX-cX-timestamp.png
    #                 filename = f"{position_info}-s{i}-c{i}-{timestamp}.png"

    #                 if i > 6: 
    #                     # For cameras 7-12, use mid2 from MarkerConfig
    #                     # query marker_config by mid (position_info) , get mid2
    #                     mid2 = MarkerConfig.query.filter_by(mid=position_info).first().mid2
    #                     filename = f"{mid2}-s{i}-c{i}-{timestamp}.png"
    #                     self._log('debug', f"Using mid2 for camera {i}: {mid2}")
    #                 else:
    #                     # For cameras 1-6, use mid from MarkerConfig
    #                     filename = f"{position_info}-s{i}-c{i}-{timestamp}.png"
    #                     self._log('debug', f"Using mid for camera {i}: {position_info}")

    #                 filepath = os.path.join(base_dir, filename)
    #                 filepath = filepath.replace("\\", "/")
    #                 abs_filepath = os.path.abspath(filepath)
    #                 self._log('debug', f"Saving frame to: {abs_filepath}")


    #                 # # 保存为 PNG，压缩级别 9
    #                 # cv2.imwrite('output_compressed.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    #                 # 压缩级别选择：
    #                 # 如果优先考虑文件大小，选择较高的值（如 6-9）。
    #                 # 如果优先考虑保存速度，选择较低的值（如 0-3）。
    #                 # 默认值为 3，平衡了速度和文件大小。


    #                 # # 保存为 JPEG，质量 90
    #                 # cv2.imwrite('output_compressed.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])


    #                 # Save as PNG with highest quality (no compression)
    #                 if not cv2.imwrite(abs_filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0]):
    #                     raise RuntimeError(f"Failed to save image for camera {i}")
    #                 self._log('debug', f"Successfully saved image for camera {i}")

    #                 results.append({
    #                     "camera_id": i,
    #                     "status": "OK",
    #                     "filename": filename,
    #                     "filepath": filepath,
    #                     "debug": {
    #                         "url": url,
    #                         "resolution": f"{frame.shape[1]}x{frame.shape[0]}"
    #                     }
    #                 })
    #             except Exception as e:
    #                 self._log('error', f"Error capturing from camera {i}: {str(e)}")
    #                 results.append({
    #                     "camera_id": i,
    #                     "status": "ERROR",
    #                     "message": str(e)
    #                 })

    #         return {
    #             "status": "OK",
    #             "timestamp": timestamp,
    #             "position": position_info,
    #             "results": results
    #         }

    #     except Exception as e:
    #         self._log('error', f"Error in take_photo_all_cameras: {str(e)}")
    #         return {
    #             "status": "ERROR",
    #             "message": str(e),
    #             "timestamp": timestamp,
    #             "position": position_info,
    #             "results": []
    #         }


    def take_photo_all_cameras(self, position_info, timestamp):
        """Capture screenshots from all configured IP cameras with highest quality
        
        Args:
            position_info: Position information for the image
            timestamp: Optional timestamp string. If None, current time will be used
        """
        if self.simulation_mode:
            return {
                "status": "OK",
                "timestamp": timestamp or str(int(time.time())),
                "position": position_info,
                "results": []
            }

        results = []
        # Use provided timestamp or generate new one if not provided
        if timestamp is None:
            timestamp = str(int(time.time()))
            
        date_str = datetime.now().strftime("%Y%m%d")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        if not position_info:
            position_info = "Unknown"

        overall_status = "OK"
        try:
            self._log('info', f"Starting capture for {len(self.camera_urls)} cameras")
            if not self.camera_urls:
                raise RuntimeError("No camera URLs configured - check .env CAMERA_URLS setting")

            for i, url in enumerate(self.camera_urls, start=1):
                self._log('debug', f"Attempting capture from camera {i} with URL: {url}")
                cap = None
                frame = None
                try:
                    # Open RTSP stream with timeout settings
                    self._log('debug', f"Opening RTSP stream for camera {i}")
                    cap = cv2.VideoCapture(url)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['resolution']['width'])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['resolution']['height'])
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                    
                    # Set timeout for RTSP connection (5 seconds)
                    start_time = time.time()
                    while not cap.isOpened() and (time.time() - start_time) < 5:
                        time.sleep(0.1)
                    
                    if not cap.isOpened():
                        self._log('error', f"Could not open camera {i} at {url} after 5 seconds")
                        results.append({
                            "camera_id": i,
                            "status": "ERROR",
                            "message": "Failed to open camera connection",
                            "debug": {"url": url}
                        })
                        overall_status = "PARTIAL"
                        continue

                    # Clear buffer by reading frames
                    for _ in range(10):
                        cap.grab()

                    # Read frame with retry mechanism
                    max_retries = 5
                    frame = None
                    ret = False
                    
                    for retry in range(max_retries):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            if frame.shape[0] > 0 and frame.shape[1] > 0 and len(frame.shape) == 3:
                                break
                        time.sleep(0.2)

                    if not ret or frame is None or frame.size == 0:
                        self._log('error', f"Failed to capture valid frame from camera {i}")
                        results.append({
                            "camera_id": i,
                            "status": "ERROR",
                            "message": "Failed to capture valid frame",
                            "debug": {"url": url, "retries": max_retries}
                        })
                        overall_status = "PARTIAL"
                        continue

                    # convert camera id to layer id
                    layer_id = 1
                    if i == 1 or i == 7:
                        layer_id = 1
                    elif i == 2 or i == 8:
                        layer_id = 2
                    elif i == 3 or i == 9:
                        layer_id = 3
                    elif i == 4 or i == 10:
                        layer_id = 4    
                    elif i == 5 or i == 11:
                        layer_id = 5
                    elif i == 6 or i == 12:
                        layer_id = 6
                

                    if position_info == "Unknown":
                        # self._log('warning', "Position info is 'Unknown', using default filename")
                        filename = f"Unknown-s{i}-c{i}-{timestamp}.png"
                    else:
                        # Generate filename
                        filename = f"{position_info}-s{layer_id}-c{layer_id}-{timestamp}.png"
                        if i > 6:
                            mid2 = MarkerConfig.query.filter_by(mid=position_info).first().mid2
                            filename = f"{mid2}-s{layer_id}-c{layer_id}-{timestamp}.png"
                            if mid2 == '00000000000' or len(mid2) != 11: #not save if mid2 not configured
                                continue


                    filepath = os.path.join(base_dir, filename)
                    filepath = filepath.replace("\\", "/")
                    abs_filepath = os.path.abspath(filepath)

                    # Save with multiple retry attempts
                    save_success = False
                    save_retries = 3
                    
                    for save_retry in range(save_retries):
                        try:
                            save_result = cv2.imwrite(abs_filepath, frame, 
                                                    [cv2.IMWRITE_PNG_COMPRESSION, 0])
                            if save_result:
                                save_success = True
                                break
                            time.sleep(0.1)
                        except Exception as save_error:
                            self._log('error', f"Save attempt {save_retry + 1} failed: {str(save_error)}")

                    if not save_success:
                        self._log('error', f"Failed to save image for camera {i}")
                        results.append({
                            "camera_id": i,
                            "status": "ERROR",
                            "message": "Failed to save image",
                            "filename": filename,
                            "filepath": filepath,
                            "debug": {
                                "url": url,
                                "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                                "frame_size": frame.size,
                                "save_attempts": save_retries
                            }
                        })
                        overall_status = "PARTIAL"
                        continue

                    # Success case
                    self._log('debug', f"Successfully captured and saved image for camera {i}")
                    results.append({
                        "camera_id": i,
                        "status": "OK",
                        "filename": filename,
                        "filepath": filepath,
                        "debug": {
                            "url": url,
                            "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                            "frame_size": frame.size
                        }
                    })

                except Exception as e:
                    self._log('error', f"Error processing camera {i}: {str(e)}")
                    results.append({
                        "camera_id": i,
                        "status": "ERROR",
                        "message": str(e),
                        "debug": {"url": url}
                    })
                    overall_status = "PARTIAL"
                    continue
                    
                finally:
                    if cap is not None:
                        cap.release()

            return {
                "status": overall_status,
                "timestamp": timestamp,
                "position": position_info,
                "results": results
            }

        except Exception as e:
            self._log('error', f"Error in take_photo_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": results
            }




    def connect(self):
        """For IP cameras, connection is handled when capturing frames"""
        return {
            "status": "OK",
            "message": "IP cameras will connect when capturing frames"
        }

    def close(self):
        """Simple close method for IP cameras"""
        # Stop all ongoing recordings
        for camera_id in list(self.recording_cameras.keys()):
            if self.recording_cameras.get(camera_id, False):
                self.stop_recording(camera_id)
                
        self._log('info', "OpenCVControl closed")

    def start_recording(self, camera_id, task_id=None, marker=None):
        """Start video recording for a specific camera
        
        Args:
            camera_id (int): The ID of the camera to record from (1-based index)
            task_id (int, optional): Task ID for file naming
            marker (str, optional): Start marker position for file naming
            
        Returns:
            dict: Status information about the recording start
        """
        try:
            if self.recording_cameras.get(camera_id, False):
                return {"status": "ERROR", "message": f"Camera {camera_id} is already recording"}

            if camera_id < 1 or camera_id > len(self.camera_urls):
                return {"status": "ERROR", "message": f"Invalid camera ID {camera_id}"}

            url = self.camera_urls[camera_id - 1]
            
            # Create video directory if it doesn't exist
            os.makedirs("static/video", exist_ok=True)

            # Initialize video capture with optimal settings
            cap = cv2.VideoCapture(url)
            if not cap.isOpened():
                raise RuntimeError(f"Failed to open camera {camera_id}")

            # Configure video capture properties
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Set buffer size
            
            # Set video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 15.0  # Fixed FPS for consistent recording

            # Clear buffer
            for _ in range(5):
                cap.grab()

            # Initialize video writer
            timestamp = int(time.time())
            video_path = f"static/video/temp_video_{camera_id}_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

            if not writer.isOpened():
                cap.release()
                raise RuntimeError("Failed to initialize video writer")

            # Store recording state
            self.recording_cameras[camera_id] = True
            self.video_writers[camera_id] = writer
            self.video_paths[camera_id] = video_path

            # Start recording thread
            self._start_recording_thread(camera_id, cap)

            self._log('info', f"Started recording for camera {camera_id}")
            return {"status": "OK", "message": "Recording started"}

        except Exception as e:
            self._log('error', f"Error starting recording for camera {camera_id}: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    def stop_recording(self, camera_id, task_id=None, start_marker=None, start_timestamp=None, end_marker=None):
        """Stop video recording for a specific camera
        
        Args:
            camera_id (int): The ID of the camera to stop recording
            task_id (int, optional): Task ID for file naming
            start_marker (str, optional): Start marker position for file naming
            start_timestamp (int, optional): Start timestamp for file naming
            end_marker (str, optional): End marker position for file naming
            
        Returns:
            dict: Status information about the recording stop
        """
        try:
            if not self.recording_cameras.get(camera_id, False):
                return {"status": "ERROR", "message": f"Camera {camera_id} is not recording"}

            # Stop recording
            self.recording_cameras[camera_id] = False
            writer = self.video_writers.get(camera_id)
            temp_video_path = self.video_paths.get(camera_id)

            if writer:
                writer.release()
                self.video_writers.pop(camera_id, None)

            # Check if temporary video exists
            if not temp_video_path or not os.path.exists(temp_video_path):
                raise RuntimeError("Video file not found after recording")

            # Generate final video path with task information
            final_video_path = temp_video_path
            if all([task_id, start_marker, start_timestamp, end_marker]):
                end_timestamp = int(time.time())
                final_name = f"{task_id}-{start_marker}-{start_timestamp}-{end_marker}-{end_timestamp}.mp4"
                final_video_path = os.path.join("static/video", final_name)
                
                # Rename temporary file to final name
                try:
                    os.rename(temp_video_path, final_video_path)
                    self._log('info', f"Renamed video from {temp_video_path} to {final_video_path}")
                except Exception as e:
                    self._log('error', f"Failed to rename video file: {str(e)}")
                    final_video_path = temp_video_path  # Fall back to temp path if rename fails

            self._log('info', f"Successfully stopped recording for camera {camera_id}")
            self.video_paths.pop(camera_id, None)
            return {
                "status": "OK",
                "message": "Recording stopped",
                "filepath": final_video_path
            }

        except Exception as e:
            self._log('error', f"Error stopping recording for camera {camera_id}: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    def _start_recording_thread(self, camera_id, cap):
        """Start a thread to continuously capture frames for recording
        
        Args:
            camera_id (int): The camera ID being recorded
            cap (cv2.VideoCapture): The video capture object
        """
        import threading

        def record_frames():
            try:
                writer = self.video_writers.get(camera_id)
                while self.recording_cameras.get(camera_id, False) and writer:
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        writer.write(frame)
                    else:
                        self._log('warning', f"Failed to read frame from camera {camera_id}")
                    time.sleep(1/30)  # Limit to ~30 fps
            except Exception as e:
                self._log('error', f"Error in recording thread for camera {camera_id}: {str(e)}")
            finally:
                cap.release()

        thread = threading.Thread(target=record_frames)
        thread.daemon = True
        thread.start()
