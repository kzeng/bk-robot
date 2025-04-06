from datetime import datetime
from app import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marker = db.Column(db.String(255), default='')
    action = db.Column(db.Integer, default=0)  # 0: photo, 1: recording
    status = db.Column(db.Integer, default=0)  # 0: pending, 1: running, 2: failed, 3: finished
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    update_at = db.Column(db.DateTime)
    run_at = db.Column(db.DateTime)
    description = db.Column(db.String(255), default='')

    def __repr__(self):
        return f'<Task {self.task_id}>'
