import socket
import json
from config import Config
import time
import struct
import random
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
            logger.info(f"Connected to robot at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
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
        self.connected = False

    def _receive_json_response(self, require_complete=False):
        """Receive and parse a JSON response from robot socket.

        Handles TCP packet fragmentation where UTF-8 multibyte characters
        or JSON payload may arrive across multiple recv calls.
        """
        if not self.socket:
            raise ConnectionError("Socket not initialized")

        rx = b''
        decoder = json.JSONDecoder()

        while True:
            chunk = self.socket.recv(self.buffer_size)
            if not chunk:
                break

            rx += chunk

            # Keep receiving until current bytes can form valid UTF-8 text.
            try:
                text = rx.decode('utf-8')
            except UnicodeDecodeError:
                continue

            # Keep receiving until a complete JSON object is available.
            try:
                response, _ = decoder.raw_decode(text)
            except json.JSONDecodeError:
                continue

            if require_complete and not response.get('complete', True):
                continue

            return response

        if not rx:
            raise ConnectionError("No response received")

        text = rx.decode('utf-8')
        response = json.loads(text)

        if require_complete and not response.get('complete', True):
            raise ConnectionError("Connection closed before complete response")

        return response

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
        if not self.connected and not self.connect():
            return {'status': 'error', 'message': 'Connection failed'}

        try:
            if not self.socket:
                raise ConnectionError("Socket not initialized")
                
            logger.info(f"Sending command: {cmd_str}")
            
            # Send command
            cmd_bytes = cmd_str.encode('utf-8')
            self.socket.sendall(cmd_bytes)

            # Wait for response
            response = self._receive_json_response(require_complete=True)
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
            response = self._receive_json_response(require_complete=False)
            return response
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {
                'type': 'response',
                'command': '/api/robot_status',
                'status': 'ERROR',
                'error_message': str(e),
                'results': None
            }
