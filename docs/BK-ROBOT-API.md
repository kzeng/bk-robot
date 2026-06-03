# BK Robot API

This document lists the application-level APIs exposed by the Flask service. Camera capture is implemented with OpenCV over RTSP streams.

## Robot APIs

### Send Robot Command

- **Method:** `POST`
- **Path:** `/api/robot/cmd`
- **Body:**

```json
{
  "cmd": "/api/move",
  "params": "marker=M1"
}
```

The route forwards a robot-base command and returns the base response in the operation-status format used by the UI.

### Robot Status

- **Method:** `GET`
- **Path:** `/api/robot/status`

Returns selected robot status fields such as `move_target`, `move_status`, `running_status`, `charge_state`, `estop_state`, and `power_percent`.

### Recharge

- **Method:** `POST`
- **Path:** `/api/robot/recharge`

Finds the first configured charging marker whose short name starts with `CD` and sends a move command to that marker.

### Cancel Move

- **Method:** `POST`
- **Path:** `/api/move/cancel`

Cancels the current robot move task.

## Camera APIs

### Take Screenshot

- **Method:** `POST`
- **Path:** `/api/camera/screenshot`
- **Body:**

```json
{
  "position_info": "M1"
}
```

Captures photos from all configured RTSP cameras through OpenCV. Results include per-camera status and saved file paths.

### Start Recording

- **Method:** `POST`
- **Path:** `/api/camera/start_recording`
- **Body:**

```json
{
  "camera_id": 1,
  "task_id": 12,
  "marker": "M1"
}
```

Starts OpenCV recording for the selected camera.

### Stop Recording

- **Method:** `POST`
- **Path:** `/api/camera/stop_recording`
- **Body:**

```json
{
  "camera_id": 1,
  "task_id": 12,
  "start_marker": "M1",
  "start_timestamp": 1710000000,
  "end_marker": "M2"
}
```

Stops recording for the selected camera and returns the saved file path.

## Task APIs

### List Tasks

- **Method:** `GET`
- **Path:** `/api/tasks?page=1&size=10`

Returns paginated inventory tasks.

### Create Task

- **Method:** `POST`
- **Path:** `/api/tasks`
- **Body:**

```json
{
  "marker": "M1,M2,CD",
  "action": 0,
  "description": "Shelf scan"
}
```

`action` values: `0` photo, `1` video, `99` move only.

### Run Task

- **Method:** `POST`
- **Path:** `/api/tasks/{task_id}/run`

Starts a background task execution thread and returns `task_log_id`.

### Task Logs

- **Method:** `GET`
- **Path:** `/api/task-logs?page=1&size=10`

Returns paginated task execution logs.
