# Development Notes

## Runtime Environment

Use the project Conda environment when running tools locally:

```powershell
conda activate venv-pyside2
```

For non-interactive validation, prefer:

```powershell
conda run -n venv-pyside2 python -m compileall app
```

## Camera Stack

Camera capture is handled by OpenCV over RTSP. Configure camera streams with
`CAMERA_URLS` in `.env`, using a comma-separated list:

```text
CAMERA_URLS=rtsp://admin@192.168.10.21:554/user=admin&password=&channel=1&stream=0.sdp?
```

The camera API is exposed through `/api/camera/start_recording`,
`/api/camera/stop_recording`, and `/api/camera/screenshot`.

## Robot And Task Flow

Task execution is coordinated in `app/routes.py`. A task moves the robot through
configured marker points, records or captures images through the OpenCV camera
controller, and writes progress to task logs. The `tasks` table stores marker,
action, description, and timestamps only.

Keep hardware support aligned with the current robot design. Do not add task
fields, configuration values, database migrations, scripts, or UI controls for
hardware that is not present on the deployed robot.

## Configuration

Runtime configuration is read from `.env` through `config.py`. Keep secrets and
site-specific values out of source control when possible. Common local settings:

- `CAMERA_URLS`
- `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`, `FTP_REMOTE_DIR`
- `ROBOT_IP`
- `SCHOOL_ID`

## Maintenance Checks

Before committing changes, run:

```powershell
conda run -n venv-pyside2 python -m compileall app
git diff --check
```

When cleaning generated files, avoid deleting user data. `app/logs/app.log` can
be cleared during maintenance, but database files under `instance/` should only
be changed intentionally.
