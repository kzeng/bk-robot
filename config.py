from dotenv import load_dotenv
import os
from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')


load_dotenv(env_path, override=True)  # Ensure .env values override process defaults.

#-------------------------------------------------------------------------------------------
# you  can change these variables in .env file


class Config:
    NEED_AUTH = os.environ.get('NEED_AUTH', True) 
    # Set BASEDIR for the application
    BASEDIR = basedir
    # admin password hashlib.sha1 admin123
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'f865b53623b121fd34ee5426c792e5c33af8c227')
    
    # super user password hashlib.sha1 su123456
    SUPER_USER_PASSWORD = os.environ.get('SUPER_USER_PASSWORD', '4148d4c33f1809dc66c039dd44c0db4a7db76325' )



    # Camera configuration
    CAMERA_CONFIG = {
        'resolution': {
            'width': int(os.environ.get('CAMERA_WIDTH', '2880')),
            'height': int(os.environ.get('CAMERA_HEIGHT', '1620'))
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

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    # Robot base configuration
    ROBOT_MOCK_MODE = os.environ.get('ROBOT_MOCK_MODE', False)
    if ROBOT_MOCK_MODE == 'true' or ROBOT_MOCK_MODE == 'True' or ROBOT_MOCK_MODE == True or ROBOT_MOCK_MODE == '1':
        ROBOT_MOCK_MODE = True
    else:
        ROBOT_MOCK_MODE = False

    ROBOT_IP = os.environ.get('ROBOT_IP', '192.168.10.10')
    ROBOT_PORT = int(os.environ.get('ROBOT_PORT', '1448'))
    ROBOT_BASE_URL = os.environ.get('ROBOT_BASE_URL', f'http://{ROBOT_IP}:{ROBOT_PORT}')
    ROBOT_API_TIMEOUT = float(os.environ.get('ROBOT_API_TIMEOUT', '10'))
    

    # FTP Server configuration
    FTP_HOST = os.environ.get('FTP_HOST', 'ftp.example.com')
    FTP_PORT = int(os.environ.get('FTP_PORT', '21'))
    FTP_USER = os.environ.get('FTP_USER', 'username')
    FTP_PASS = os.environ.get('FTP_PASS', 'password')


    # School configuration
    CCODE = os.environ.get('CCODE', '01')  # Campus code, default 01.

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance/tasks.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
