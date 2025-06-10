import cv2
import platform
import subprocess
from loguru import logger

class CameraControl:
    """Camera control implementation that works on both Windows and Linux"""
    
    def __init__(self, device_id):
        self.device_id = device_id
        self.is_windows = platform.system() == 'Windows'
        self.cap = None
        
    def open(self):
        """Open camera device"""
        self.cap = cv2.VideoCapture(self.device_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.device_id}")
            
    def close(self):
        """Close camera device"""
        if self.cap:
            self.cap.release()
            self.cap = None
                
    def _log(self, level, msg):
        """Simple logger for OpenCVControl"""
        print(f"[{level.upper()}] {msg}")
        
    def set_params(self, params):
        """Set camera parameters using platform-specific method"""
        if self.is_windows:
            self._log("info", "Setting camera parameters on Windows")
            self._set_params_windows(params)
        else:
            self._log("info", "Setting camera parameters on Linux")
            self._set_params_linux(params)
            
    def _set_params_windows(self, params):
        """Set camera parameters using OpenCV on Windows"""
        if not self.cap:
            return
            
        param_map = {
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'sharpness': cv2.CAP_PROP_SHARPNESS,
            'gamma': cv2.CAP_PROP_GAMMA,
            'gain': cv2.CAP_PROP_GAIN,
            'exposure_time': cv2.CAP_PROP_EXPOSURE,
            'white_balance_temp': cv2.CAP_PROP_WB_TEMPERATURE,
            'focus_absolute': cv2.CAP_PROP_FOCUS,
            'auto_exposure': cv2.CAP_PROP_AUTO_EXPOSURE,
            'white_balance_auto': cv2.CAP_PROP_AUTO_WB,
            'focus_auto': cv2.CAP_PROP_AUTOFOCUS
        }
        
        for param_name, value in params.items():
            if param_name in param_map:
                prop_id = param_map[param_name]
                success = self.cap.set(prop_id, value)
                if not success:
                    logger.warning(f"Failed to set {param_name}={value}")
                    
    def _set_params_linux(self, params):
        """Set camera parameters using v4l2-ctl on Linux"""
        if not self.device_id.startswith('/dev/video'):
            return
            
        cmd = ['v4l2-ctl', '-d', self.device_id]
        
        param_map = {
            'brightness': 'brightness',
            'contrast': 'contrast', 
            'saturation': 'saturation',
            'sharpness': 'sharpness',
            'gamma': 'gamma',
            'gain': 'gain',
            'exposure_time': 'exposure_absolute',
            'white_balance_temp': 'white_balance_temperature',
            'focus_absolute': 'focus_absolute',
            'auto_exposure': 'exposure_auto',
            'white_balance_auto': 'white_balance_temperature_auto',
            'focus_auto': 'focus_auto',
            'backlight_comp': 'backlight_compensation',
            'power_line_freq': 'power_line_frequency'
        }
        
        for param_name, value in params.items():
            if param_name in param_map:
                v4l2_name = param_map[param_name]
                cmd.extend(['--set-ctrl', f"{v4l2_name}={value}"])
                
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set camera parameters: {e}")
