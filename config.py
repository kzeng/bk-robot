import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # 机器人底座配置
    MOCK_MODE = os.environ.get('MOCK_MODE') or False
    ROBOT_IP = os.environ.get('ROBOT_IP') or '192.168.10.10'
    ROBOT_PORT = int(os.environ.get('ROBOT_PORT') or 31001)
    
    # OBS WebSocket配置
    OBS_WS_URL = os.environ.get('OBS_WS_URL') or 'ws://192.168.0.109:4455'
    OBS_PASSWORD = os.environ.get('OBS_PASSWORD') or '123456'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance/tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
