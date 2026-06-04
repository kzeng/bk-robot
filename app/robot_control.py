import time
from threading import RLock
from urllib.parse import parse_qs, urlsplit

import requests

from config import Config
from app.utils.logger import configured_logger as logger


class RobotControl:
    """Slamtec REST adapter with the legacy app-facing response shape.

    The rest of the application expects a small set of robot operations:
    move to a named point, cancel movement, read status, and sync points. This
    adapter keeps those semantics while talking to Slamware REST APIs.
    """

    ACTION_MOVE = "slamtec.agent.actions.MultiFloorMoveAction"
    ACTION_GO_HOME = "slamtec.agent.actions.GoHomeAction"

    def __init__(self, base_url=None, timeout=None):
        self.base_url = (base_url or Config.ROBOT_BASE_URL).rstrip("/")
        self.timeout = timeout or Config.ROBOT_API_TIMEOUT
        self.app = None
        self._command_lock = RLock()
        self._last_action_id = None
        self.connected = True

    def init_app(self, app):
        self.app = app

    def _url(self, path):
        return f"{self.base_url}{path}"

    def _request(self, method, path, **kwargs):
        try:
            response = requests.request(
                method,
                self._url(path),
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            if not response.content:
                return None
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                return response.text
            return response.json()
        except requests.RequestException as exc:
            logger.error(f"Slamtec request failed: {method} {path}: {exc}")
            raise
        except ValueError as exc:
            logger.error(f"Slamtec returned non-JSON response: {method} {path}: {exc}")
            raise

    def _ok(self, command, results=None, message=""):
        return {
            "type": "response",
            "command": command,
            "status": "OK",
            "error_message": "",
            "message": message,
            "results": results or {},
        }

    def _error(self, command, message, error_type="robot_api_error"):
        return {
            "type": "response",
            "command": command,
            "status": "ERROR",
            "error_message": str(message),
            "message": str(message),
            "error_type": error_type,
            "results": None,
        }

    def _normalize_action_status(self, action):
        state = (action or {}).get("state") or {}
        status = state.get("status")
        result = state.get("result")
        reason = state.get("reason") or ""

        if status == 4:
            if result == 0:
                move_status = "succeeded"
                running_status = "idle"
            elif result == -2:
                move_status = "canceled"
                running_status = "idle"
            else:
                move_status = "failed"
                running_status = "error"
        elif status == 3:
            move_status = "paused"
            running_status = "paused"
        elif status in (0, 1):
            move_status = "running"
            running_status = "running"
        else:
            move_status = ""
            running_status = "idle"

        return {
            "task_id": action.get("action_id"),
            "action_id": action.get("action_id"),
            "action_name": action.get("action_name"),
            "stage": action.get("stage"),
            "move_status": move_status,
            "running_status": running_status,
            "error_message": reason,
        }

    def _marker_config_by_name(self, marker):
        from app.models import MarkerConfig

        return (
            MarkerConfig.query.filter_by(mid_short=marker).first()
            or MarkerConfig.query.filter_by(poi_name=marker).first()
            or MarkerConfig.query.filter_by(mid=marker).first()
        )

    def _target_from_marker_config(self, config):
        has_pose = config and config.pose_x is not None and config.pose_y is not None
        if has_pose and config.floor:
            target = {
                "building": config.building or "",
                "floor": config.floor,
                "pose": {
                    "x": float(config.pose_x),
                    "y": float(config.pose_y),
                    "yaw": float(config.pose_yaw or 0),
                },
            }
        else:
            target = {"poi_name": config.poi_name if config else None}
        return target

    def create_action(self, action_name, options=None):
        command = "/api/core/motion/v1/actions"
        body = {"action_name": action_name, "options": options or {}}
        with self._command_lock:
            try:
                action = self._request("POST", command, json=body)
                action_id = (action or {}).get("action_id")
                self._last_action_id = action_id
                results = self._normalize_action_status(action or {})
                return self._ok(command, results)
            except Exception as exc:
                return self._error(command, exc)

    def move_to_marker(self, marker):
        config = self._marker_config_by_name(marker)
        if not config:
            return self._error("/api/core/motion/v1/actions", f"Unknown marker: {marker}", "unknown_marker")

        target = self._target_from_marker_config(config)
        options = {"target": target}
        result = self.create_action(self.ACTION_MOVE, options)
        if result.get("status") == "OK":
            result["command"] = f"move_to_marker:{marker}"
            result["results"]["move_target"] = marker
            result["results"]["poi_name"] = config.poi_name
            result["results"]["floor"] = config.floor
            result["results"]["building"] = config.building
        return result

    def go_home(self):
        return self.create_action(self.ACTION_GO_HOME, {"gohome_options": {"flags": "dock"}})

    def cancel_move(self):
        command = "/api/core/motion/v1/actions/:current"
        with self._command_lock:
            try:
                self._request("DELETE", command)
                return self._ok(command, message="Move command cancelled successfully")
            except Exception as exc:
                return self._error(command, exc)

    def set_emergency_stop(self, enabled):
        command = "/api/core/system/v1/parameter"
        body = {
            "param": "base.emergency_stop",
            "value": "on" if enabled else "off",
        }
        with self._command_lock:
            try:
                result = self._request("PUT", command, json=body)
                return self._ok(
                    command,
                    {
                        "emergency_stop": bool(enabled),
                        "raw": result,
                    },
                    message="Emergency stop enabled" if enabled else "Emergency stop cleared",
                )
            except Exception as exc:
                return self._error(command, exc)

    def _normalize_emergency_stop_value(self, value):
        if isinstance(value, dict):
            for key in ("value", "data", "result"):
                if key in value:
                    return self._normalize_emergency_stop_value(value.get(key))
            if "emergency_stop" in value:
                return bool(value.get("emergency_stop"))
            return None

        if isinstance(value, bool):
            return value

        if value is None:
            return None

        normalized = str(value).strip().strip('"').lower()
        if normalized in ("on", "true", "1", "yes", "enabled"):
            return True
        if normalized in ("off", "false", "0", "no", "disabled"):
            return False
        return None

    def get_emergency_stop_state(self):
        command = "/api/core/system/v1/parameter"
        try:
            result = self._request("GET", command, params={"param": "base.emergency_stop"})
            estop_state = self._normalize_emergency_stop_value(result)
            if estop_state is None:
                return self._error(command, f"Unexpected emergency stop value: {result}", "invalid_estop_state")
            return self._ok(command, {"estop_state": estop_state, "raw": result})
        except Exception as exc:
            return self._error(command, exc)

    def get_action_status(self, action_id=None):
        action_id = action_id or self._last_action_id
        command = f"/api/core/motion/v1/actions/{action_id}" if action_id else "/api/core/motion/v1/actions/:current"
        try:
            action = self._request("GET", command)
            return self._ok(command, self._normalize_action_status(action or {}))
        except Exception as exc:
            return self._error(command, exc)

    def get_status(self):
        command = "/api/robot_status"
        try:
            current_action = None
            try:
                current_action = self._request("GET", "/api/core/motion/v1/actions/:current")
            except Exception:
                current_action = None

            power = {}
            try:
                power = self._request("GET", "/api/core/system/v1/power/status") or {}
            except Exception:
                pass

            health = {}
            try:
                health = self._request("GET", "/api/core/system/v1/robot/health") or {}
            except Exception:
                pass

            estop_state = None
            estop_source = "unavailable"
            estop_error = ""
            estop_result = self.get_emergency_stop_state()
            if estop_result.get("status") == "OK":
                estop_state = estop_result.get("results", {}).get("estop_state")
                estop_source = "base.emergency_stop"
            else:
                estop_error = estop_result.get("error_message", "")

            floor = {}
            try:
                floor = self._request("GET", "/api/multi-floor/map/v1/floors/:current") or {}
            except Exception:
                pass

            results = self._normalize_action_status(current_action or {})
            results.update({
                "move_target": results.get("move_target", ""),
                "charge_state": bool(power.get("isCharging") or power.get("is_charging")),
                "estop_state": estop_state,
                "estop_state_source": estop_source,
                "estop_state_error": estop_error,
                "has_error": bool(health.get("hasError")),
                "has_fatal": bool(health.get("hasFatal")),
                "power_percent": power.get("batteryPercentage", power.get("battery_percentage", 0)),
                "current_floor": floor.get("floor", ""),
                "current_building": floor.get("building", ""),
                "map_id": floor.get("map_id", ""),
                "raw_action": current_action,
            })
            return self._ok(command, results)
        except Exception as exc:
            return self._error(command, exc)

    def get_floors(self):
        try:
            return self._request("GET", "/api/multi-floor/map/v1/floors") or []
        except Exception as exc:
            logger.warning(f"Failed to query floors: {exc}")
            return []

    def get_all_pois(self, floor=None, building=None):
        params = {}
        if floor:
            params["floor"] = floor
        if building:
            params["building"] = building
        return self._request("GET", "/api/multi-floor/map/v1/pois", params=params) or []

    def sync_maps_and_pois(self):
        floors = self.get_floors()
        pois = self.get_all_pois()
        return {
            "floors": floors,
            "pois": pois,
        }

    def send_command(self, cmd_str):
        """Compatibility bridge for old UI/debug command calls."""
        parsed = urlsplit(cmd_str)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/move":
            marker = (params.get("marker") or [""])[0]
            return self.move_to_marker(marker)
        if path == "/api/move/cancel":
            return self.cancel_move()
        if path == "/api/robot_status":
            return self.get_status()
        if path == "/api/estop":
            flag = (params.get("flag") or ["false"])[0].strip().lower()
            return self.set_emergency_stop(flag in ("1", "true", "on", "yes"))
        readonly_paths = {
            "/api/core/artifact/v1/pois",
            "/api/core/motion/v1/action-factories",
            "/api/core/motion/v1/actions/:current",
            "/api/core/motion/v1/milestones",
            "/api/core/motion/v1/path",
            "/api/core/motion/v1/speed",
            "/api/core/motion/v1/strategies",
            "/api/core/motion/v1/strategies/:current",
            "/api/core/motion/v1/time",
            "/api/core/sensors/v1/masks",
            "/api/core/slam/v1/homedocks",
            "/api/core/slam/v1/homepose",
            "/api/core/slam/v1/imu",
            "/api/core/slam/v1/knownarea",
            "/api/core/slam/v1/localization/:enable",
            "/api/core/slam/v1/localization/odopose",
            "/api/core/slam/v1/localization/pose",
            "/api/core/slam/v1/localization/quality",
            "/api/core/slam/v1/loopclosure/:enable",
            "/api/core/slam/v1/mapping/:enable",
            "/api/core/statistics/v1/odometry",
            "/api/core/statistics/v1/runtime",
            "/api/core/system/v1/battery/pack",
            "/api/core/system/v1/capabilities",
            "/api/core/system/v1/network/status",
            "/api/core/system/v1/parameter",
            "/api/core/system/v1/robot/info",
            "/api/core/system/v1/power/status",
            "/api/core/system/v1/robot/health",
            "/api/delivery/v1/admin/line_speed",
            "/api/delivery/v1/admin/working_time",
            "/api/multi-floor/map/v1/floors",
            "/api/multi-floor/map/v1/floors/:current",
            "/api/multi-floor/map/v1/homedocks",
            "/api/multi-floor/map/v1/homedocks/:current",
            "/api/multi-floor/map/v1/pois",
            "/api/multi-floor/status",
            "/api/platform/v1/timestamp",
        }
        if path in readonly_paths:
            try:
                query_params = {key: values[-1] for key, values in params.items() if values}
                data = self._request("GET", path, params=query_params or None)
                return self._ok(path, data)
            except Exception as exc:
                return self._error(path, exc)

        dynamic_readonly_prefixes = (
            "/api/core/motion/v1/actions/",
            "/api/core/artifact/v1/pois/",
            "/api/multi-floor/map/v1/elevators/",
        )
        if any(path.startswith(prefix) for prefix in dynamic_readonly_prefixes):
            try:
                query_params = {key: values[-1] for key, values in params.items() if values}
                data = self._request("GET", path, params=query_params or None)
                return self._ok(path, data)
            except Exception as exc:
                return self._error(path, exc)

        return self._error(cmd_str, "Unsupported legacy robot command", "unsupported_command")

    def recharge(self):
        return self.go_home()

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
