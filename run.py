import os
from app.utils.logger import configured_logger as logger

os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    logger.info("Starting bk-robot application...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
