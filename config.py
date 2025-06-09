import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# you  can change these variables in .env file


class Config:
    NEED_AUTH = os.environ.get('NEED_AUTH', False) 
    # Set BASEDIR for the application
    BASEDIR = basedir
    # admin password hashlib.sha1
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'f865b53623b121fd34ee5426c792e5c33af8c227')
    
    # Camera configuration
    CAMERA_CONFIG = {
        'resolution': {
            'width': int(os.environ.get('CAMERA_WIDTH', '1920')),
            'height': int(os.environ.get('CAMERA_HEIGHT', '1080'))
        },
        'fps': int(os.environ.get('CAMERA_FPS', '30')),
        'jpeg_quality': int(os.environ.get('JPEG_QUALITY', '100')),
        'buffer_size': int(os.environ.get('CAMERA_BUFFER_SIZE', '10')),  # Number of frames to buffer
        'enable_monitoring': os.environ.get('CAMERA_MONITORING', False)
    }

    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
      # 机器人底座配置
    MOCK_MODE = os.environ.get('MOCK_MODE', False)
    if MOCK_MODE == 'true' or MOCK_MODE == 'True' or MOCK_MODE == True:
        MOCK_MODE = True
    else:
        MOCK_MODE = False

    ROBOT_IP = os.environ.get('ROBOT_IP', '192.168.10.10')
    ROBOT_PORT = int(os.environ.get('ROBOT_PORT', '31001'))
    
    # OBS WebSocket配置
    # My Ubuntu
    OBS_WS_URL = os.environ.get('OBS_WS_URL', 'ws://192.168.0.109:4455')
    OBS_PASSWORD = os.environ.get('OBS_PASSWORD', '123456')

    # USE opencv-python (default obs)
    USE_OPENCV = os.environ.get('USE_OPENCV', False) 
    if USE_OPENCV == 'true' or USE_OPENCV == 'True' or USE_OPENCV == True:
        USE_OPENCV = True
    else:
        USE_OPENCV = False

    # FTP Server configuration
    FTP_HOST = os.environ.get('FTP_HOST', 'ftp.example.com')
    FTP_PORT = int(os.environ.get('FTP_PORT', '21'))
    FTP_USER = os.environ.get('FTP_USER', 'username')
    FTP_PASS = os.environ.get('FTP_PASS', 'password')
    MOCK_FTP = os.environ.get('MOCK_FTP', False) 
    if MOCK_FTP == 'true' or MOCK_FTP == 'True' or MOCK_FTP == True:
        MOCK_FTP = True
    else:
        MOCK_FTP = False

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance/tasks.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
