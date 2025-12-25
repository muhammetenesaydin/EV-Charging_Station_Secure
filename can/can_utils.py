"""
CAN Bus Utilities Module

This module provides utilities for CAN bus communication including:
- Sending and receiving CAN messages
- Message validation and logging
- Interface management
"""

import can
import time
import sys
from typing import Optional, List, Callable
from datetime import datetime


class CANInterface:
    """Manages CAN bus interface operations"""
    
    def __init__(self, interface: str = 'vcan0', bustype: str = 'socketcan'):
        """
        Initialize CAN interface
        
        Args:
            interface: CAN interface name (default: vcan0)
            bustype: Bus type (default: socketcan)
        """
        self.interface = interface
        self.bustype = bustype
        self.bus: Optional[can.Bus] = None
        
    def connect(self) -> bool:
        """
        Connect to CAN bus
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.bus = can.interface.Bus(self.interface, bustype=self.bustype)
            print(f"[CAN] Connected to {self.interface}")
            return True
        except OSError as e:
            print(f"[CAN ERROR] Failed to connect to {self.interface}: {e}")
            print(f"[CAN ERROR] Make sure vcan0 is set up: sudo modprobe vcan && sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0")
            return False
    
    def disconnect(self):
        """Disconnect from CAN bus"""
        if self.bus:
            self.bus.shutdown()
            print(f"[CAN] Disconnected from {self.interface}")
    
    def send_message(self, arbitration_id: int, data: List[int], 
                    extended: bool = False, log: bool = True) -> bool:
        """
        Send a CAN message
        
        Args:
            arbitration_id: CAN ID (11-bit or 29-bit)
            data: Data bytes (list of integers 0-255)
            extended: Use extended frame format
            log: Log the message
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.bus:
            print("[CAN ERROR] Not connected to bus")
            return False
        
        # Validate data
        if len(data) > 8:
            print(f"[CAN ERROR] Data length {len(data)} exceeds maximum of 8 bytes")
            return False
        
        for byte in data:
            if not 0 <= byte <= 255:
                print(f"[CAN ERROR] Invalid byte value: {byte}")
                return False
        
        try:
            msg = can.Message(
                arbitration_id=arbitration_id,
                data=data,
                is_extended_id=extended
            )
            self.bus.send(msg)
            
            if log:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                data_str = ' '.join([f'{b:02X}' for b in data])
                print(f"[CAN TX] [{timestamp}] ID: 0x{arbitration_id:03X} Data: [{data_str}]")
            
            return True
        except Exception as e:
            print(f"[CAN ERROR] Failed to send message: {e}")
            return False
    
    def receive_message(self, timeout: float = 1.0) -> Optional[can.Message]:
        """
        Receive a CAN message
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            CAN message if received, None otherwise
        """
        if not self.bus:
            print("[CAN ERROR] Not connected to bus")
            return None
        
        try:
            msg = self.bus.recv(timeout=timeout)
            return msg
        except Exception as e:
            print(f"[CAN ERROR] Failed to receive message: {e}")
            return None
    
    def listen(self, callback: Callable[[can.Message], None], 
              duration: Optional[float] = None, filter_id: Optional[int] = None):
        """
        Listen for CAN messages and call callback for each
        
        Args:
            callback: Function to call for each message
            duration: How long to listen (None = forever)
            filter_id: Only process messages with this ID (None = all)
        """
        if not self.bus:
            print("[CAN ERROR] Not connected to bus")
            return
        
        print(f"[CAN] Listening on {self.interface}...")
        start_time = time.time()
        
        try:
            while True:
                msg = self.bus.recv(timeout=0.1)
                
                if msg:
                    # Apply filter if specified
                    if filter_id is None or msg.arbitration_id == filter_id:
                        callback(msg)
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                    
        except KeyboardInterrupt:
            print("\n[CAN] Listening stopped by user")


class CANMessageLogger:
    """Logs CAN messages to file and console"""
    
    def __init__(self, log_file: str = "logs/can_traffic.log"):
        """
        Initialize logger
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        
    def log_message(self, msg: can.Message, direction: str = "RX"):
        """
        Log a CAN message
        
        Args:
            msg: CAN message
            direction: TX or RX
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        data_str = ' '.join([f'{b:02X}' for b in msg.data])
        log_line = f"[{timestamp}] {direction} | ID: 0x{msg.arbitration_id:03X} | DLC: {msg.dlc} | Data: [{data_str}]\n"
        
        # Write to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_line)
        except Exception as e:
            print(f"[LOG ERROR] Failed to write to {self.log_file}: {e}")
        
        # Print to console
        print(log_line.strip())


def send_can_message(arbitration_id: int, data: List[int], 
                    interface: str = 'vcan0') -> bool:
    """
    Quick helper to send a single CAN message
    
    Args:
        arbitration_id: CAN ID
        data: Data bytes
        interface: CAN interface name
        
    Returns:
        True if successful, False otherwise
    """
    can_if = CANInterface(interface)
    if can_if.connect():
        result = can_if.send_message(arbitration_id, data)
        can_if.disconnect()
        return result
    return False


def format_can_message(msg: can.Message) -> str:
    """
    Format CAN message for display
    
    Args:
        msg: CAN message
        
    Returns:
        Formatted string
    """
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    data_str = ' '.join([f'{b:02X}' for b in msg.data])
    return f"[{timestamp}] ID: 0x{msg.arbitration_id:03X} DLC: {msg.dlc} Data: [{data_str}]"


if __name__ == "__main__":
    # Test the CAN interface
    print("Testing CAN Interface...")
    
    can_if = CANInterface()
    if can_if.connect():
        # Send test message
        print("\nSending test message...")
        can_if.send_message(0x123, [0x01, 0x02, 0x03, 0x04])
        
        # Listen for messages
        print("\nListening for 5 seconds...")
        can_if.listen(
            callback=lambda msg: print(format_can_message(msg)),
            duration=5.0
        )
        
        can_if.disconnect()
    else:
        print("Failed to connect to CAN interface")
        sys.exit(1)
