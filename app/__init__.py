# Last config update: 2025-06-15 14:55:40
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os
from .robot_control import RobotControl
from .obs_control import OBSControl
from .opencv_control import OpenCVControl
from loguru import logger

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
robot_control = RobotControl()

# Initialize both controllers but only use one based on USE_OPENCV flag
obs_control = OBSControl()
opencv_control = OpenCVControl()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # 记录环境变量初始状态
    # logger.debug(f"[create_app] Initial env USE_OPENCV={os.environ.get('USE_OPENCV')}")
    
    # 设置ROOT_PATH为项目根目录
    app.config['ROOT_PATH'] = os.path.dirname(app.root_path)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'tasks.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        # Load configuration directly from Config class to ensure all settings are available
        from config import Config
        # logger.debug(f"[create_app] Before loading Config, env USE_OPENCV={os.environ.get('USE_OPENCV')}")
        app.config.from_object(Config)
        logger.debug(f"[create_app] After loading Config, USE_OPENCV in app.config={app.config.get('USE_OPENCV')}")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    robot_control.init_app(app)
    
    # Add robot_control to app instance
    app.robot_control = robot_control
    
    # Initialize camera control based on USE_OPENCV flag
    use_opencv_raw = app.config.get('USE_OPENCV', '0')
    # logger.debug(f"[create_app] Raw USE_OPENCV from config={use_opencv_raw} (type={type(use_opencv_raw)})")
    
    # 统一的布尔值转换逻辑
    use_opencv = str(use_opencv_raw).lower() in ('true', '1', 'yes', 'on')
    # logger.debug(f"[create_app] Converted USE_OPENCV={use_opencv} (type={type(use_opencv)})")
    
    if use_opencv:
        logger.info(f"[create_app] Using OpenCV for camera control (USE_OPENCV={use_opencv})")
        opencv_control.init_app(app)
        app.opencv_control = opencv_control
        app.camera_control = opencv_control
    else:
        logger.info(f"[create_app] Using OBS for camera control (USE_OPENCV={use_opencv})")
        obs_control.init_app(app)
        app.obs_control = obs_control  
        app.camera_control = obs_control
        logger.info("Using OBS for camera control")
        # Verify OBS config was loaded
        if not app.config.get('OBS_WS_URL') or not app.config.get('OBS_PASSWORD'):
            logger.warning("OBS configuration not properly loaded - check config.py")

    from . import routes
    app.register_blueprint(routes.bp)

    return app
