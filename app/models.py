from datetime import datetime
from app import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marker = db.Column(db.String(255), default='')
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
    marker = db.Column(db.String(255), nullable=False)
    action = db.Column(db.Integer, nullable=False)  # 0: photo, 1: recording
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)  # 0: pending, 1: in progress, 2: completed
    file_count = db.Column(db.Integer, nullable=False)
    file_paths = db.Column(db.Text, nullable=False)  # JSON string of file paths

    def __repr__(self):
        return f'<TaskLog {self.log_id}>'
