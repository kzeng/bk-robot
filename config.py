from dotenv import load_dotenv
import os
from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

# 检查 .env 文件
# logger.debug(f"[Config] .env path: {env_path}")
# logger.debug(f"[Config] .env exists: {os.path.exists(env_path)}")
# if os.path.exists(env_path):
#     with open(env_path, 'r') as f:
#         logger.debug(f"[Config] .env content:\n{f.read()}")

# # 记录 .env 加载前的环境变量值
# raw_use_opencv = os.environ.get('USE_OPENCV')
# logger.debug(f"[Config] Before load_dotenv, USE_OPENCV={raw_use_opencv}")

load_dotenv(env_path, override=True)  # 添加 override=True 确保重载

# # 记录 .env 加载后的环境变量值
# env_use_opencv = os.environ.get('USE_OPENCV')
# logger.debug(f"[Config] After load_dotenv, USE_OPENCV={env_use_opencv}")

# you  can change these variables in .env file


class Config:
    NEED_AUTH = os.environ.get('NEED_AUTH', False) 
    # Set BASEDIR for the application
    BASEDIR = basedir
    # admin password hashlib.sha1
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'f865b53623b121fd34ee5426c792e5c33af8c227')
    
    # Camera control configuration
    USE_OPENCV = os.environ.get('USE_OPENCV')
    # logger.debug(f"[Config] Config class reading USE_OPENCV directly from environ: {USE_OPENCV}")
    # 如果没有值，设置默认值
    if USE_OPENCV is None:
        USE_OPENCV = '0'
    # logger.debug(f"[Config] Config class final USE_OPENCV={USE_OPENCV}")
    
    # Camera configuration
    CAMERA_CONFIG = {
        'resolution': {
            'width': int(os.environ.get('CAMERA_WIDTH', '1920')),
            'height': int(os.environ.get('CAMERA_HEIGHT', '1080'))
        },
        'fps': int(os.environ.get('CAMERA_FPS', '30')),
        'jpeg_quality': int(os.environ.get('CAMERA_JPEG_QUALITY', '100')),
        'buffer_size': int(os.environ.get('CAMERA_BUFFER_SIZE', '10')),  # Number of frames to buffer
        'enable_monitoring': os.environ.get('CAMERA_MONITORING', False),
        'control_params': {
            'brightness': int(os.environ.get('CAMERA_BRIGHTNESS', '16')),
            'contrast': int(os.environ.get('CAMERA_CONTRAST', '40')), 
            'saturation': int(os.environ.get('CAMERA_SATURATION', '80')),
            'sharpness': int(os.environ.get('CAMERA_SHARPNESS', '6')),
            'gamma': int(os.environ.get('CAMERA_GAMMA', '120')),
            'auto_exposure': int(os.environ.get('CAMERA_AUTO_EXPOSURE', '1')),
            'exposure_time': int(os.environ.get('CAMERA_EXPOSURE_TIME', '80')),
            'gain': int(os.environ.get('CAMERA_GAIN', '20')),
            'white_balance_auto': int(os.environ.get('CAMERA_WB_AUTO', '0')),
            'white_balance_temp': int(os.environ.get('CAMERA_WB_TEMP', '5000')),
            'focus_auto': int(os.environ.get('CAMERA_FOCUS_AUTO', '0')), 
            'focus_absolute': int(os.environ.get('CAMERA_FOCUS', '200')),
            'backlight_comp': int(os.environ.get('CAMERA_BACKLIGHT', '0')),
            'power_line_freq': int(os.environ.get('CAMERA_POWERLINE_FREQ', '1'))
        }
    }

    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
      # 机器人底座配置
    ROBOT_MOCK_MODE = os.environ.get('ROBOT_MOCK_MODE', False)
    if ROBOT_MOCK_MODE == 'true' or ROBOT_MOCK_MODE == 'True' or ROBOT_MOCK_MODE == True or ROBOT_MOCK_MODE == '1':
        ROBOT_MOCK_MODE = True
    else:
        ROBOT_MOCK_MODE = False

    ROBOT_IP = os.environ.get('ROBOT_IP', '192.168.10.10')
    ROBOT_PORT = int(os.environ.get('ROBOT_PORT', '31001'))
    
    # OBS WebSocket配置
    # My Ubuntu
    OBS_WS_URL = os.environ.get('OBS_WS_URL', 'ws://192.168.0.109:4455')
    OBS_PASSWORD = os.environ.get('OBS_PASSWORD', '123456')

    # USE opencv-python (default obs)
    USE_OPENCV = os.environ.get('USE_OPENCV', False) 
    if USE_OPENCV == 'true' or USE_OPENCV == 'True' or USE_OPENCV == True or USE_OPENCV == '1':
        USE_OPENCV = True
    else:
        USE_OPENCV = False

    # FTP Server configuration
    FTP_HOST = os.environ.get('FTP_HOST', 'ftp.example.com')
    FTP_PORT = int(os.environ.get('FTP_PORT', '21'))
    FTP_USER = os.environ.get('FTP_USER', 'username')
    FTP_PASS = os.environ.get('FTP_PASS', 'password')
    FTP_MOCK_MODE = os.environ.get('FTP_MOCK_MODE', False) 
    if FTP_MOCK_MODE == 'true' or FTP_MOCK_MODE == 'True' or FTP_MOCK_MODE == True or FTP_MOCK_MODE == '1':
        FTP_MOCK_MODE = True
    else:
        FTP_MOCK_MODE = False

    # Add Lift configuration
    LIFT_PORT = os.environ.get('LIFT_PORT', '/dev/ttyUSB0')  # Serial port for lift control

    LIFT_WAIT_TIME = int(os.environ.get('LIFT_WAIT_TIME', '15'))  # Time to wait after sending lift command

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance/tasks.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
