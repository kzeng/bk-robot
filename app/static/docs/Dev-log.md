# Development Log

## 2026-06 Cleanup

- Standardized camera operations on OpenCV plus RTSP streams.
- Removed stale capture and auxiliary hardware paths from code,
  configuration, scripts, and task data.
- Updated task management so tasks contain marker, action, description, and
  timestamp data only.
- Cleared runtime log output after cleanup.

## Current Architecture Notes

The robot control surface now has two main responsibilities:

- Robot movement and task execution through the robot HTTP API.
- Camera recording and screenshots through `OpenCVControl`.

The web UI should call camera endpoints under `/api/camera/*`. New UI, database,
or configuration work should follow the current OpenCV/RTSP camera path and the
current deployed robot hardware.

## Validation

Use:

```powershell
conda run -n venv-pyside2 python -m compileall app
```

Also check for stale implementation terms before release using a project-wide
search.
