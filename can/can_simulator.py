"""
CAN Traffic Simulator

Generates realistic CAN bus traffic patterns for testing
"""

import can
import time
import random
import threading
from typing import Dict, List
from datetime import datetime
from can.can_utils import CANInterface


class CANTrafficSimulator:
    """Simulates normal CAN bus traffic"""
    
    def __init__(self, interface: str = 'vcan0'):
        """
        Initialize simulator
        
        Args:
            interface: CAN interface name
        """
        self.interface = interface
        self.can_if = CANInterface(interface)
        self.running = False
        self.threads: List[threading.Thread] = []
        
        # Normal traffic patterns (ID: (rate_hz, data_generator))
        self.traffic_patterns: Dict = {
            0x100: (10, lambda: [0x01, random.randint(0, 100), 0x00, 0x00]),  # Battery status
            0x200: (1, lambda: [0x02, 0x00, 0x00, 0x00]),                      # Charge control
            0x300: (1, lambda: [0x03, random.randint(20, 80), 0x00, 0x00]),   # Temperature
            0x400: (5, lambda: [0x04, random.randint(0, 255), random.randint(0, 255), 0x00]),  # Voltage/Current
        }
    
    def start(self):
        """Start generating traffic"""
        if not self.can_if.connect():
            print("[SIMULATOR ERROR] Failed to connect to CAN bus")
            return False
        
        self.running = True
        print(f"[SIMULATOR] Starting CAN traffic simulation on {self.interface}")
        
        # Start a thread for each traffic pattern
        for can_id, (rate, data_gen) in self.traffic_patterns.items():
            thread = threading.Thread(
                target=self._generate_traffic,
                args=(can_id, rate, data_gen),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            print(f"[SIMULATOR] Started traffic for CAN ID 0x{can_id:03X} at {rate} Hz")
        
        return True
    
    def stop(self):
        """Stop generating traffic"""
        print("[SIMULATOR] Stopping traffic simulation...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2.0)
        
        self.can_if.disconnect()
        print("[SIMULATOR] Traffic simulation stopped")
    
    def _generate_traffic(self, can_id: int, rate: float, data_generator):
        """
        Generate traffic for a specific CAN ID
        
        Args:
            can_id: CAN ID to send
            rate: Messages per second
            data_generator: Function that returns data bytes
        """
        interval = 1.0 / rate
        
        while self.running:
            data = data_generator()
            self.can_if.send_message(can_id, data, log=False)
            time.sleep(interval)
    
    def add_pattern(self, can_id: int, rate: float, data_generator):
        """
        Add a new traffic pattern
        
        Args:
            can_id: CAN ID
            rate: Messages per second
            data_generator: Function that returns data bytes
        """
        self.traffic_patterns[can_id] = (rate, data_generator)
        
        if self.running:
            # Start thread for this pattern
            thread = threading.Thread(
                target=self._generate_traffic,
                args=(can_id, rate, data_generator),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            print(f"[SIMULATOR] Added traffic for CAN ID 0x{can_id:03X} at {rate} Hz")


def generate_normal_traffic(duration: float = 60.0, interface: str = 'vcan0'):
    """
    Generate normal CAN traffic for a specified duration
    
    Args:
        duration: How long to generate traffic (seconds)
        interface: CAN interface name
    """
    simulator = CANTrafficSimulator(interface)
    
    if simulator.start():
        print(f"[SIMULATOR] Generating normal traffic for {duration} seconds...")
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n[SIMULATOR] Interrupted by user")
        finally:
            simulator.stop()


if __name__ == "__main__":
    print("CAN Traffic Simulator - Test Mode")
    print("Generating normal traffic for 30 seconds...")
    print("Press Ctrl+C to stop\n")
    
    generate_normal_traffic(duration=30.0)
