# Last config update: 2025-07-06 22:21:22
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os
import subprocess
from datetime import datetime
from .robot_control import RobotControl
from .obs_control import OBSControl
from .ffmpeg_control import FFmpegControl
from .lift_control import Lift
from config import Config
from app.utils.logger import configured_logger as logger

def get_git_revision():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short=4', 'HEAD']).decode('ascii').strip()
    except:
        return 'dev0'

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
robot_control = RobotControl()

def create_app(test_config=None):
    # Initialize camera controllers only when needed
    obs_control = None
    opencv_control = None
    ffmpeg_control = None
    app = Flask(__name__)
    
    # 设置ROOT_PATH为项目根目录
    app.config['ROOT_PATH'] = os.path.dirname(app.root_path)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'tasks.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'git_version': get_git_revision()
        }

    if test_config is None:
        # Load configuration directly from Config class to ensure all settings are available
        from config import Config
        app.config.from_object(Config)
        logger.debug(f"[create_app] After loading Config, PHOTO_MODE in app.config={app.config.get('PHOTO_MODE')}")
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
    
    # Initialize camera control based on PHOTO_MODE
    photo_mode = str(app.config.get('PHOTO_MODE', '0'))
    logger.debug(f"[create_app] Using photo mode: {photo_mode}")
    
    if photo_mode == '0':
        logger.info("[create_app] Using OBS for camera control")
        obs_control = OBSControl()
        obs_control.init_app(app)
        app.obs_control = obs_control
        app.camera_control = obs_control
        # Verify OBS config was loaded
        if not app.config.get('OBS_WS_URL') or not app.config.get('OBS_PASSWORD'):
            logger.warning("OBS configuration not properly loaded - check config.py")
    elif photo_mode == '1':
        logger.info("[create_app] Using OpenCV for camera control")
        from .opencv_control import OpenCVControl
        opencv_control = OpenCVControl()
        opencv_control.init_app(app)
        # Load camera URLs from environment - handle both newline and comma separated
        urls_str = os.environ.get('CAMERA_URLS', '')
        # First split by newlines, then split each line by commas
        camera_urls = []
        for line in urls_str.splitlines():
            camera_urls.extend([url.strip() for url in line.split(',') if url.strip()])
        if camera_urls:
            opencv_control.set_camera_urls(camera_urls)
            logger.info(f"Configured {len(camera_urls)} camera URLs")
        else:
            logger.warning("No camera URLs configured in CAMERA_URLS environment variable")
        app.opencv_control = opencv_control
        app.camera_control = opencv_control
    elif photo_mode == '2':
        logger.info("[create_app] Using FFmpeg for camera control")
        ffmpeg_control = FFmpegControl()
        ffmpeg_control.init_app(app)
        app.ffmpeg_control = ffmpeg_control
        app.camera_control = ffmpeg_control
    else:
        logger.warning(f"[create_app] Invalid PHOTO_MODE: {photo_mode}, falling back to OBS")
        obs_control = OBSControl()
        obs_control.init_app(app)
        app.obs_control = obs_control
        app.camera_control = obs_control

    # Initialize lift control
    try:
        app.lift = Lift(
            port=app.config.get('LIFT_PORT', '/dev/ttyUSB0'),
            baudrate=app.config.get('LIFT_BAUDRATE', 115200)
        )
        logger.info(f"Lift initialized on port {app.lift.serial_connection.port}")
    except Exception as e:
        logger.error(f"Failed to initialize lift: {str(e)}")
        app.lift = None

    # 注册蓝图和其他初始化代码
    from . import routes
    app.register_blueprint(routes.bp)


    from . import routes1
    app.register_blueprint(routes1.bp1)


    from .routes_videos import bp as videos_api_bp
    app.register_blueprint(videos_api_bp, url_prefix='/api/videos')

    @app.route('/videos')
    def videos_page():
        """视频管理页面"""
        return app.render_template('videos.html') if hasattr(app, 'render_template') else __import__('flask').render_template('videos.html')

    return app
