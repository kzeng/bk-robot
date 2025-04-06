from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from config import Config
from app.robot_control import RobotControl
from app.obs_control import OBSControl

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
robot_control = RobotControl()
obs_control = OBSControl()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    robot_control.init_app(app)
    obs_control.init_app(app)
    
    # 注册蓝图
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # 将控制器实例添加到应用上下文
    app.robot_control = robot_control
    app.obs_control = obs_control
    
    return app
