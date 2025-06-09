import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# you  can change these variables in .env file


class Config:
    NEED_AUTH = os.environ.get('NEED_AUTH') or True
    # admin password hashlib.sha1
    ADMIN_PASSWORD = 'f865b53623b121fd34ee5426c792e5c33af8c227'
    
    # Camera configuration
    CAMERA_CONFIG = {
        'resolution': {
            'width': int(os.environ.get('CAMERA_WIDTH') or 1920),
            'height': int(os.environ.get('CAMERA_HEIGHT') or 1080)
        },
        'fps': int(os.environ.get('CAMERA_FPS') or 30),
        'jpeg_quality': int(os.environ.get('JPEG_QUALITY') or 95),
        'buffer_size': int(os.environ.get('CAMERA_BUFFER_SIZE') or 10),  # Number of frames to buffer
        'enable_monitoring': os.environ.get('CAMERA_MONITORING', 'true').lower() == 'true'
    }

    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # 机器人底座配置
    MOCK_MODE = os.environ.get('MOCK_MODE') or True
    ROBOT_IP = os.environ.get('ROBOT_IP') or '192.168.10.10'
    ROBOT_PORT = int(os.environ.get('ROBOT_PORT') or 31001)
    
    # OBS WebSocket配置
    # My Ubuntu
    OBS_WS_URL = os.environ.get('OBS_WS_URL') or 'ws://192.168.0.109:4455'

    # # My macOS
    # OBS_WS_URL = os.environ.get('OBS_WS_URL') or 'ws://192.168.0.102:4455'
    
    OBS_PASSWORD = os.environ.get('OBS_PASSWORD') or '123456'

    # USE opencv-python (default obs)
    USE_OPENCV = os.environ.get('USE_OPENCV') or True

    # FTP Server configuration
    FTP_HOST = os.environ.get('FTP_HOST') or 'ftp.example.com'
    FTP_PORT = int(os.environ.get('FTP_PORT') or 21)
    FTP_USER = os.environ.get('FTP_USER') or 'username'
    FTP_PASS = os.environ.get('FTP_PASS') or 'password'
    MOCK_FTP = os.environ.get('MOCK_FTP') or True

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance/tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
