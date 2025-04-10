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
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'tasks.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        # Load config.py from root directory to ensure OBS settings are available
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')
        app.config.from_pyfile(config_path, silent=False)
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
    
    # Initialize OBS control only if config is present
    if 'OBS_WS_URL' in app.config and 'OBS_PASSWORD' in app.config:
        obs_control.init_app(app)
    else:
        app.logger.warning("OBS configuration not found - OBS features will be disabled")
        app.obs_control = None

    app.robot_control = robot_control
    app.obs_control = obs_control if 'OBS_WS_URL' in app.config and 'OBS_PASSWORD' in app.config else None

    from . import routes
    app.register_blueprint(routes.bp)

    return app
