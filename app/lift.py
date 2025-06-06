import serial
import datetime
import re
import time


class Lift:
    """Control class for the lift hardware via serial connection.
    
    Args:
        port (str): Serial port name (e.g. 'COM3')
        baudrate (int): Baud rate for serial communication (default: 9600)
    """
    def __init__(self, port, baudrate=115200, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE):
        """Initialize serial connection to lift hardware."""
        self.serial_connection = serial.Serial(
            port=port,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=1
        )
        self.last_command_time = None
        self.SET_CMD_TWICE = False  # Default: send command once

    def is_connected(self):
        """Check if serial connection is active.
        
        Returns:
            bool: True if connection is open, False otherwise
        """
        return self.serial_connection.is_open

    def send_command(self, command):
        """Send a command to the lift hardware.
        
        Args:
            command (bytes): Command bytes to send
            
        Raises:
            ConnectionError: If serial connection is not open
        """
        if not self.is_connected():
            raise ConnectionError("Serial connection is not open.")
            
        try:
            # Send command as hex and add a newline
            self.serial_connection.write(command + b'\n')
            self.last_command_time = datetime.datetime.now()

            # If SET_CMD_TWICE is True, send the command twice with a 0.5s interval
            if self.SET_CMD_TWICE:
                time.sleep(0.5)
                self.serial_connection.write(command + b'\n')
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to send command: {str(e)}")


    # FA 17 06 01 00 00 10 FD 一号位
    # FA 17 07 01 00 00 11 FD 二号位
    # FA 17 08 01 00 00 1E FD 三号位
    # FA 17 03 01 00 00 15 FD 上升
    # FA 17 04 01 00 00 12 FD 下降
    # FA 17 02 01 00 00 14 FD 复位
    # FA 17 03 00 00 00 14 FD 上升停止
    # FA 17 04 00 00 00 13 FD 下降停止

    def move_to_position_one(self):
        self.send_command(b'\xFA\x17\x06\x01\x00\x00\x10\xFD')

    def move_to_position_two(self):
        self.send_command(b'\xFA\x17\x07\x01\x00\x00\x11\xFD')

    def move_to_position_three(self):
        self.send_command(b'\xFA\x17\x08\x01\x00\x00\x1E\xFD')

    def move_up(self):
        self.send_command(b'\xFA\x17\x03\x01\x00\x00\x15\xFD')

    def move_down(self):
        self.send_command(b'\xFA\x17\x04\x01\x00\x00\x12\xFD')

    def reset(self):
        self.send_command(b'\xFA\x17\x02\x01\x00\x00\x14\xFD')

    def stop_moving_up(self):
        self.send_command(b'\xFA\x17\x03\x00\x00\x00\x14\xFD')

    def stop_moving_down(self):
        self.send_command(b'\xFA\x17\x04\x00\x00\x00\x13\xFD')
