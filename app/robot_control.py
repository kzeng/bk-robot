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
            bytes_sent = self.socket.send(cmd_bytes)
            if bytes_sent != len(cmd_bytes):
                raise ConnectionError(f"Only sent {bytes_sent}/{len(cmd_bytes)} bytes")
            
            # Wait for response
            rx = b''
            while True:
                chunk = self.socket.recv(self.buffer_size)
                if not chunk:
                    break
                rx += chunk
                try:
                    # Try to parse partial response
                    response = json.loads(rx.decode('utf-8'))
                    if response.get('complete', True):
                        return response
                except json.JSONDecodeError:
                    continue
            
            if not rx:
                raise ConnectionError("No response received")
                
            response = json.loads(rx.decode('utf-8'))
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
            self.socket.send(api_request.encode('utf-8'))
            # Receive response
            rx = self.socket.recv(self.buffer_size)
            if not rx:
                raise ConnectionError("No response from robot")
            response = json.loads(rx.decode('utf-8'))
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
