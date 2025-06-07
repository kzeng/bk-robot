from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os
from .robot_control import RobotControl
from .obs_control import OBSControl

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
robot_control = RobotControl()
obs_control = OBSControl()

def create_app(test_config=None):
    app = Flask(__name__)
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
        app.config.from_object(Config)
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
    
    # Initialize OBS control with app
    obs_control.init_app(app)
    app.robot_control = robot_control
    app.obs_control = obs_control
    
    # Verify OBS config was loaded
    if not app.config.get('OBS_WS_URL') or not app.config.get('OBS_PASSWORD'):
        app.logger.warning("OBS configuration not properly loaded - check config.py")

    from . import routes
    app.register_blueprint(routes.bp)

    return app
