from datetime import datetime
from app import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marker = db.Column(db.String(2048), default='')
    action = db.Column(db.Integer, default=0)  # 0: photo, 1: recording
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    update_at = db.Column(db.DateTime)
    description = db.Column(db.String(255), default='')

    def __repr__(self):
        return f'<Task {self.task_id}>'

class TaskLog(db.Model):
    __tablename__ = 'task_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    marker = db.Column(db.String(2048), nullable=False)
    action = db.Column(db.Integer, nullable=False)  # 0: photo, 1: recording
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)  # 0: pending, 1: in progress, 2: completed
    file_count = db.Column(db.Integer, nullable=False)
    file_paths = db.Column(db.Text, nullable=False)  # JSON string of file paths

    def __repr__(self):
        return f'<TaskLog {self.log_id}>'

class MarkerConfig(db.Model):
    __tablename__ = 'marker_config'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mid = db.Column(db.String(255), unique=True, nullable=False)
    poi_id = db.Column(db.String(255), nullable=True)
    poi_name = db.Column(db.String(255), nullable=True)
    building = db.Column(db.String(255), nullable=True)
    floor = db.Column(db.String(255), nullable=True)
    map_id = db.Column(db.String(255), nullable=True)
    pose_x = db.Column(db.Float, nullable=True)
    pose_y = db.Column(db.Float, nullable=True)
    pose_yaw = db.Column(db.Float, nullable=True)
    mid2 = db.Column(db.String(255), nullable=True)  # 新增点位名称2
    mid_short = db.Column(db.String(255), unique=True, nullable=False)
    x = db.Column(db.Integer, default=0)
    y = db.Column(db.Integer, default=0)
    w = db.Column(db.Integer, default=0)
    h = db.Column(db.Integer, default=0)
    x2 = db.Column(db.Integer, default=0)
    y2 = db.Column(db.Integer, default=0)
    w2 = db.Column(db.Integer, default=0)
    h2 = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<MarkerConfig {self.mid}>'
