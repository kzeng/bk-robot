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
                
                    # Generate filename
                    filename = f"{position_info}-s{layer_id}-c{layer_id}-{timestamp}.png"
                    if i > 6:
                        mid2 = MarkerConfig.query.filter_by(mid=position_info).first().mid2
                        filename = f"{mid2}-s{layer_id}-c{layer_id}-{timestamp}.png"

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
        self._log('info', "OpenCVControl closed")
