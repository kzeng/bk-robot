# BK Robot

BK Robot is a Flask application for library inventory robot control. The current
hardware profile uses a Slamtec robot base plus RTSP IP cameras captured through
OpenCV.

## Features

- Robot movement and status control through the Slamtec Slamware REST API.
- Multi-floor POI synchronization and local marker-short-name mapping.
- Inventory task creation, execution, and task-log tracking.
- Multi-camera RTSP configuration and OpenCV photo/video capture.
- System settings for robot, camera, FTP, and school code values.

## Stack

- Python
- Flask
- Flask-SocketIO
- Flask-SQLAlchemy / Flask-Migrate
- SQLite
- OpenCV

## Project Structure

```text
bk-robot/
|-- run.py                         # Application entry point
|-- config.py                      # Environment-backed configuration
|-- requirements.txt               # Python dependencies
|-- app/
|   |-- __init__.py                # Flask app factory and extension setup
|   |-- routes.py                  # Main pages, robot APIs, task APIs, camera APIs
|   |-- routes1.py                 # Marker config, photo, and auxiliary routes
|   |-- routes_videos.py           # Video management routes
|   |-- models.py                  # SQLAlchemy models
|   |-- opencv_control.py          # RTSP/OpenCV camera capture and recording
|   |-- robot_control.py           # Slamtec REST robot base adapter
|   |-- templates/                 # Jinja templates
|   |-- static/                    # JavaScript, CSS, images, frontend assets
|   `-- logs/                      # Runtime logs
|-- docs/                          # API and hardware documentation
|-- instance/tasks.db              # Local SQLite database
|-- migrations/                    # Alembic migrations
`-- scripts/                       # Deployment and maintenance scripts
```

## Local Development

```powershell
conda activate venv-pyside2
pip install -r requirements.txt
python run.py
```

The development server listens on `0.0.0.0:5000`.

## Configuration

Runtime configuration is loaded from `.env`. Important keys include:

- `CAMERA_URLS`: one RTSP camera URL per line.
- `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`, `CAMERA_JPEG_QUALITY`: OpenCV capture settings.
- `ROBOT_IP`, `ROBOT_PORT`, `ROBOT_BASE_URL`, `ROBOT_API_TIMEOUT`: Slamtec REST robot base settings.
- `FTP_HOST`, `FTP_PORT`, `FTP_USER`, `FTP_PASS`: upload settings.
- `CCODE`: two-digit school/campus code.

## Validation

Use the project Conda environment:

```powershell
conda run -n venv-pyside2 python -m compileall app
```
