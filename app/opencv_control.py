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

    def take_photo_all_cameras(self, position_info):
        """Capture screenshots from all configured IP cameras with highest quality"""
        if self.simulation_mode:
            return {
                "status": "OK",
                "timestamp": str(int(time.time())),
                "position": position_info,
                "results": []
            }

        results = []
        timestamp = str(int(time.time()))
        date_str = datetime.now().strftime("%Y%m%d")
        base_dir = os.path.join("static", "screenshots", date_str)
        os.makedirs(base_dir, exist_ok=True)

        if not position_info:
            position_info = "Unknown"

        try:
            self._log('info', f"Starting capture for {len(self.camera_urls)} cameras")
            if not self.camera_urls:
                raise RuntimeError("No camera URLs configured - check .env CAMERA_URLS setting")

            for i, url in enumerate(self.camera_urls, start=1):
                self._log('debug', f"Attempting capture from camera {i} with URL: {url}")
                try:
                    # Open RTSP stream with timeout settings
                    self._log('debug', f"Opening RTSP stream for camera {i}")
                    cap = cv2.VideoCapture(url)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['resolution']['width'])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['resolution']['height'])
                    
                    # Set timeout for RTSP connection (5 seconds)
                    start_time = time.time()
                    while not cap.isOpened() and (time.time() - start_time) < 5:
                        time.sleep(0.1)
                    
                    if not cap.isOpened():
                        error_msg = f"Could not open camera {i} at {url} after 5 seconds"
                        self._log('error', error_msg)
                        raise RuntimeError(error_msg)
                    self._log('debug', f"Successfully opened camera {i} stream")

                    # Read multiple frames to allow buffer to fill
                    for _ in range(5):
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            break
                        time.sleep(0.1)
                    
                    cap.release()

                    if not ret or frame is None:
                        error_msg = f"Failed to capture frame from camera {i} after multiple attempts"
                        self._log('error', error_msg)
                        raise RuntimeError(error_msg)
                    self._log('debug', f"Successfully captured frame from camera {i}")

                    # Generate filename in format: position-sX-cX-timestamp.png
                    filename = f"{position_info}-s{i}-c{i}-{timestamp}.png"

                    if i > 6: 
                        # For cameras 7-12, use mid2 from MarkerConfig
                        # query marker_config by mid (position_info) , get mid2
                        mid2 = MarkerConfig.query.filter_by(mid=position_info).first().mid2
                        filename = f"{mid2}-s{i}-c{i}-{timestamp}.png"
                        self._log('debug', f"Using mid2 for camera {i}: {mid2}")
                    else:
                        # For cameras 1-6, use mid from MarkerConfig
                        filename = f"{position_info}-s{i}-c{i}-{timestamp}.png"
                        self._log('debug', f"Using mid for camera {i}: {position_info}")

                    filepath = os.path.join(base_dir, filename)
                    filepath = filepath.replace("\\", "/")
                    abs_filepath = os.path.abspath(filepath)
                    self._log('debug', f"Saving frame to: {abs_filepath}")


                    # # 保存为 PNG，压缩级别 9
                    # cv2.imwrite('output_compressed.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                    # 压缩级别选择：
                    # 如果优先考虑文件大小，选择较高的值（如 6-9）。
                    # 如果优先考虑保存速度，选择较低的值（如 0-3）。
                    # 默认值为 3，平衡了速度和文件大小。


                    # # 保存为 JPEG，质量 90
                    # cv2.imwrite('output_compressed.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])


                    # Save as PNG with highest quality (no compression)
                    if not cv2.imwrite(abs_filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0]):
                        raise RuntimeError(f"Failed to save image for camera {i}")
                    self._log('debug', f"Successfully saved image for camera {i}")

                    results.append({
                        "camera_id": i,
                        "status": "OK",
                        "filename": filename,
                        "filepath": filepath,
                        "debug": {
                            "url": url,
                            "resolution": f"{frame.shape[1]}x{frame.shape[0]}"
                        }
                    })
                except Exception as e:
                    self._log('error', f"Error capturing from camera {i}: {str(e)}")
                    results.append({
                        "camera_id": i,
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
            self._log('error', f"Error in take_photo_all_cameras: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "timestamp": timestamp,
                "position": position_info,
                "results": []
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
