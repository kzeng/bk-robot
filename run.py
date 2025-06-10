import os

os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
