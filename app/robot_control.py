import socket
import json
from flask import current_app
import time
import struct
import random
from config import Config

class RobotControl:
    def __init__(self, host=Config.ROBOT_IP, port=Config.ROBOT_PORT, mock=Config.MOCK_MODE):
        """Initialize robot control with TCP connection parameters
        
        Args:
            host (str): Robot server IP address
            port (int): Robot server port
            mock (bool): Enable mock mode for development without real robot
        """
        self.host = host
        self.port = port
        self.mock = mock
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
        if self.mock:
            self.connected = True
            self._get_logger().info(f"Mock connected to robot at {self.host}:{self.port}")
            return True
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self._get_logger().info(f"Connected to robot at {self.host}:{self.port}")
            return True
        except Exception as e:
            self._get_logger().error(f"Connection failed: {str(e)}")
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
        """
        Send generic API command to robot and wait for response
        
        Args:
            cmd_str (str): API command string (e.g. '/api/move')
            params (str|dict): Optional parameters as string or dict
            
        Returns:
            dict: Response from robot
        """
        if not self.connected and not self.connect():
            return {'status': 'error', 'message': 'Connection failed'}

        if self.mock:
            # Mock responses for development
            time.sleep(0.1)  # Simulate network delay

            print(f"Mock command: {cmd_str} ")
            return {
                'status': 'ok',
                'command': cmd_str,
                'message': f'Mock response for {cmd_str}'
            }
        try:
            # Construct API request
            api_request = cmd_str
            print(f"Sending command: {api_request}")
            
            # Send request
            print('Sending socket request to robot >>>>>>>>>>')
            self.socket.send(api_request.encode('utf-8'))
            
            # Receive response
            rx = self.socket.recv(self.buffer_size)
            if not rx:
                raise ConnectionError("No response from robot")
                
            response = json.loads(rx.decode('utf-8'))
            return response
            
        except Exception as e:
            self._get_logger().error(f"Command {cmd_str} failed: {str(e)}")
            self.disconnect()
            return {'status': 'error', 'message': str(e)}


    def __del__(self):
        """Destructor to ensure clean disconnect"""
        self.disconnect()

    def _get_logger(self):
        """Get logger from Flask app or current_app"""
        if self.app:
            return self.app.logger
        return current_app.logger

    def get_status(self):
        """Get current robot status"""
        if not self.connected and not self.connect():
            return {
                'type': 'response',
                'command': '/api/robot_status',
                'status': 'ERROR',
                'error_message': 'Connection failed',
                'results': None
            }

        if self.mock:
            # Mock response with sample data
            return {
                'type': 'response',
                'command': '/api/robot_status',
                'uuid': '',
                'status': 'OK',
                'error_message': '',
                'results': {
                    'move_target': 'target_name',
                    'move_status': 'running',
                    'running_status': 'running',
                    'move_retry_times': 3,
                    'charge_state': False,
                    'soft_estop_state': False,
                    'hard_estop_state': False,
                    'estop_state': False,
                    'power_percent': 85,
                    'current_pose': {
                        'x': 11.0,
                        'y': 11.0,
                        'theta': 0.5
                    },
                    'current_floor': 16,
                    'chargepile_id': '0',
                    'error_code': '00000000'
                }
            }

        try:
            # Call actual robot status API
            api_request = '/api/robot_status'
            print(f"Sending command: {api_request}")
            
            # Send request
            print('Sending socket request to robot >>>>>>>>>>')
            self.socket.send(api_request.encode('utf-8'))
            
            # Receive response
            rx = self.socket.recv(self.buffer_size)
            if not rx:
                raise ConnectionError("No response from robot")
                
            response = json.loads(rx.decode('utf-8'))
            return response
        except Exception as e:
            self._get_logger().error(f"Status check failed: {str(e)}")
            return {
                'type': 'response',
                'command': '/api/robot_status',
                'status': 'ERROR',
                'error_message': str(e),
                'results': None
            }
