import socket
import json
from config import Config
import time
import struct
import random
from threading import RLock
from app.utils.logger import configured_logger as logger

class RobotControl:
    def __init__(self, host=Config.ROBOT_IP, port=Config.ROBOT_PORT):
        """Initialize robot control with TCP connection parameters
        
        Args:
            host (str): Robot server IP address
            port (int): Robot server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.timeout = 5  # seconds
        self.buffer_size = 4096
        self.app = None
        self._command_lock = RLock()
        self._rx_buffer = b''

    def init_app(self, app):
        """Initialize with Flask application"""
        self.app = app

    def connect(self):
        """Establish TCP connection to robot server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self._rx_buffer = b''
            logger.info(f"Connected to robot at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.disconnect()
            return False

    def disconnect(self):
        """Close TCP connection"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self._rx_buffer = b''
        self.connected = False

    def _pop_json_from_buffer(self):
        if not self._rx_buffer:
            return None

        try:
            text = self._rx_buffer.decode('utf-8')
        except UnicodeDecodeError:
            return None

        if not text.strip():
            self._rx_buffer = b''
            return None

        decoder = json.JSONDecoder()
        stripped_text = text.lstrip()

        try:
            response, end_index = decoder.raw_decode(stripped_text)
        except json.JSONDecodeError:
            return None

        # Preserve any bytes that belong to the next response on the same TCP stream.
        self._rx_buffer = stripped_text[end_index:].lstrip().encode('utf-8')
        return response

    def _command_path(self, command):
        if not command:
            return ''
        return str(command).split('?', 1)[0]

    def _commands_match(self, expected_command, actual_command):
        if not expected_command or not actual_command:
            return True
        expected = str(expected_command)
        actual = str(actual_command)
        return actual == expected or self._command_path(actual) == self._command_path(expected)

    def _should_return_response(self, response, expected_command=None):
        if not expected_command or not isinstance(response, dict):
            return True

        response_type = response.get('type')
        actual_command = response.get('command')

        if response_type == 'notification':
            logger.info(f"Ignoring robot notification while waiting for {expected_command}: {response}")
            return False

        if response_type == 'response':
            if self._commands_match(expected_command, actual_command):
                return True
            logger.warning(
                f"Ignoring stale robot response for {actual_command} "
                f"while waiting for {expected_command}: {response}"
            )
            return False

        # Some robot notifications have no status field but include code/description.
        if 'status' not in response and ('code' in response or 'description' in response):
            logger.info(f"Ignoring robot event while waiting for {expected_command}: {response}")
            return False

        # Be compatible with older or undocumented responses that omit type/command.
        if actual_command and not self._commands_match(expected_command, actual_command):
            logger.warning(
                f"Ignoring unmatched robot message for {actual_command} "
                f"while waiting for {expected_command}: {response}"
            )
            return False

        return True

    def _receive_json_response(self, require_complete=False, expected_command=None, max_wait=None):
        """Receive and parse a JSON response from robot socket.

        Handles TCP packet fragmentation where UTF-8 multibyte characters
        or JSON payload may arrive across multiple recv calls. The robot can
        also interleave async notification messages on the same TCP stream, so
        callers can pass expected_command to skip unrelated messages.
        """
        if not self.socket:
            raise ConnectionError("Socket not initialized")

        deadline = time.monotonic() + max_wait if max_wait else None

        while True:
            if deadline and time.monotonic() > deadline:
                raise socket.timeout(f"Timed out waiting for response to {expected_command}")

            response = self._pop_json_from_buffer()
            if response is not None:
                if require_complete and isinstance(response, dict) and not response.get('complete', True):
                    continue
                if self._should_return_response(response, expected_command):
                    return response
                continue

            chunk = self.socket.recv(self.buffer_size)
            if not chunk:
                break

            self._rx_buffer += chunk

        response = self._pop_json_from_buffer()
        if response is not None:
            if require_complete and isinstance(response, dict) and not response.get('complete', True):
                raise ConnectionError("Connection closed before complete response")
            if self._should_return_response(response, expected_command):
                return response

        raise ConnectionError("No complete JSON response received")

    def send_command(self, cmd_str):
        """Send command to robot and handle response
        
        Handles the full command cycle:
        1. Ensures connection is established
        2. Sends command via TCP socket
        3. Waits for and parses response
        4. Handles errors and connection drops
        
        Args:
            cmd_str (str): API command string (e.g. '/api/move')
            
        Returns:
            dict: {
                'status': 'ok'|'error',
                'message': str,      # Status message
                'command': str,       # Original command sent
                'response': dict      # Optional response data
            }
            
        Note:
            Automatically reconnects if connection is lost
        """
        with self._command_lock:
            if not self.connected and not self.connect():
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': 'Connection failed',
                    'error_type': 'connection_failed',
                    'results': None
                }

            try:
                if not self.socket:
                    raise ConnectionError("Socket not initialized")

                logger.info(f"Sending command: {cmd_str}")
                
                # Send command
                cmd_bytes = cmd_str.encode('utf-8')
                self.socket.sendall(cmd_bytes)

                # Wait for response
                response = self._receive_json_response(
                    require_complete=True,
                    expected_command=cmd_str,
                    max_wait=self.timeout
                )
                return response
            
            except socket.timeout as e:
                error_msg = f"Command timeout: {str(e)}"
                logger.error(error_msg)
                self.disconnect()
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': error_msg,
                    'error_type': 'connection_timeout',
                    'results': None
                }
            except ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(error_msg)
                self.disconnect()
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': error_msg,
                    'error_type': 'connection_failed',
                    'results': None
                }
            except json.JSONDecodeError as e:
                error_msg = f"Invalid response format: {str(e)}"
                logger.error(error_msg)
                self.disconnect()
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': error_msg,
                    'error_type': 'invalid_response',
                    'results': None
                }
            except UnicodeDecodeError as e:
                error_msg = f"Invalid UTF-8 response: {str(e)}"
                logger.error(error_msg)
                self.disconnect()
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': error_msg,
                    'error_type': 'invalid_response',
                    'results': None
                }
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                self.disconnect()
                return {
                    'type': 'response',
                    'command': cmd_str,
                    'status': 'ERROR',
                    'error_message': error_msg,
                    'error_type': 'unexpected_error',
                    'results': None
                }
    


    def __del__(self):
        """Destructor to ensure clean disconnect"""
        self.disconnect()

    def _get_logger(self):
        """Get logger from Flask app or current_app"""
        return logger

    def recharge(self):
        """Move robot to charging station (marker=CD)"""
        result = self.send_command("/api/move?marker=CD")
        # if result.get('status') == 'OK':
        #     # Check if robot is already at charging station
        #     status = self.get_status()
        #     if status.get('results', {}).get('move_target') == 'CD' and \
        #        status.get('results', {}).get('move_status') == 'succeeded':
        #         return {
        #             'status': 'OK',
        #             'message': 'Already at charging station',
        #             'results': status.get('results', {})
        #         }
        return result

    def cancel_move(self):
        """Cancel current move command"""
        result = self.send_command("/api/move/cancel")
        if result.get('status') == 'OK':
            return {
                'status': 'OK',
                'message': 'Move command cancelled successfully',
                'results': result.get('results', {})
            }
        else:
            return {
                'status': 'ERROR',
                'message': result.get('error_message', 'Failed to cancel move'),
                'results': None
            }
    


    def get_status(self):
        # returns the current status of the robot.
        # OK:
        #     {
        #     "type": "response",
        #     "command": "/api/robot_status",
        #     "uuid": "",
        #     "status": "OK",
        #     "error_message": "",
        #     "results": {
        #     "move_target": "target_name", // 移动指令指定的目标点位名称
        #     "move_status": "running", // 移动指令的执行状态。详细解释见后边
        #     "running_status": "running", // v0.7.12新增，移动任务的具体状态， 详细见后面解释
        #     "move_retry_times": 3, //此次数每增加1，表示机器人进行了新一轮的路径重试；路径规划
        #     "charge_state": bool, //true->充电中状态。false->未充电状态。
        #     "soft_estop_state": bool, // 通过API接口设置的软急停状态, true->急停中，false->非急
        #     "hard_estop_state": bool, // 通过硬件急停按钮设置的硬急停状态, true->急停中，false
        #     "estop_state": bool, // hard_estop_state || sofpt_estop_state, true->急停中，false
        #     "power_percent": 100, //电量百分比，单位：%
        #     "current_pose": {
        #     "x": 11.0,
        #     // 单位：m
        #     "y": 11.0,
        #     // 单位：m
        #     "theta": 0.5, //单位：rad
        #     }
        #     "current_floor": 16,
        #     "chargepile_id": "1234", // v0.9.6新增。充电状态下表示当前正在充电的充电桩ID，非充
        #     "error_code": "00000000"
        #     // v0.7.7新增，16进制错误码，总共8个字节表示，非0表示机
        #     }
        #     }

        # ERROR:        
        #     {
        #     "type": "response",
        #     "command": "/api/robot_status",
        #     "uuid": "",
        #     "status": "UNKNOWN_ERROR",
        #     "error_message": "Can't catch current robot status"
        #     "results"
        #     }

        """Get current robot status"""
        with self._command_lock:
            if not self.connected and not self.connect():
                return {
                    'type': 'response',
                    'command': '/api/robot_status',
                    'status': 'ERROR',
                    'error_message': 'Connection failed',
                    'results': None
                }

            try:
                # Call actual robot status API
                api_request = '/api/robot_status'
                logger.debug(f"Sending status request: {api_request}")
                # Send request
                self.socket.sendall(api_request.encode('utf-8'))
                # Receive response
                response = self._receive_json_response(
                    require_complete=False,
                    expected_command=api_request,
                    max_wait=self.timeout
                )
                return response
            except Exception as e:
                logger.error(f"Status check failed: {str(e)}")
                self.disconnect()
                return {
                    'type': 'response',
                    'command': '/api/robot_status',
                    'status': 'ERROR',
                    'error_message': str(e),
                    'results': None
                }
