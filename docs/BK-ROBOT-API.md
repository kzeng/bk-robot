# BK Robot API

## Robot Base

Robot movement is backed by the Slamtec Slamware REST API. The application keeps
stable local endpoints for the UI and task engine while `app/robot_control.py`
maps those calls to Slamware actions.

### Robot Command

- **Method:** `POST`
- **Path:** `/api/robot/cmd`

For diagnostics, this route accepts selected REST paths such as:

```json
{
  "cmd": "/api/core/system/v1/robot/info",
  "params": ""
}
```

### Robot Status

- **Method:** `GET`
- **Path:** `/api/robot/status`

Returns normalized fields used by the UI: `move_target`, `move_status`,
`running_status`, `charge_state`, `estop_state`, `power_percent`, and current
floor metadata.

### Cancel Move

- **Method:** `POST`
- **Path:** `/api/move/cancel`

Cancels the current Slamware motion action.

### Recharge

- **Method:** `POST`
- **Path:** `/api/robot/recharge`

Moves to a configured `CD*` point. The current floor is preferred; if no charging
point exists on that floor, the first `CD*` point by name is used.

## Marker Configuration

### List Markers

- **Method:** `GET`
- **Path:** `/api/marker-config`
- **Query:** `building`, `floor`, `search`, `page`, `size`, `all`

Returns locally synced marker records, including `mid`, `mid_short`,
`building`, `floor`, pose, and crop parameters. `mid` is the business point
identifier used for shelf position and image naming. Normal inventory points
must use an 11-digit `mid`; charging points may use `CD*`.

### Sync Markers

- **Method:** `POST`
- **Path:** `/api/marker-config/sync`

Synchronizes all Slamtec floors and POIs. The Slamtec POI name is stored as the
local `mid`, so field staff should name POIs in the Slamtec tool with the legacy
11-digit point code or `CD*` for charging points. Existing crop parameters are
preserved when records can be matched by the internal Slamtec POI ID or
building/floor/marker name.

## Tasks

Tasks continue to store comma-separated `mid_short` values. The task runner
resolves each short name to the local marker record, moves by Slamware
floor/pose data, and uses `mid`/`mid2` for photo filenames. Inventory execution
does not allow cross-floor point selections. The task runner appends a same-floor
`CD*` point when possible.
