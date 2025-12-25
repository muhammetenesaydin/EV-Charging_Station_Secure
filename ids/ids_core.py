"""
IDS Core Engine

Unified Intrusion Detection System that monitors CAN and OCPP traffic
"""

import asyncio
import threading
import time
from typing import Optional
from datetime import datetime

# Import CAN utilities
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from can.can_utils import CANInterface
from ids.rules import (
    FrequencySpikeDetector,
    OCPPCANDelayDetector,
    OutOfRangeDetector,
    RateChangeDetector,
    BypassDetector,
    BurstDetector,
    ConnectionFloodDetector,
    ValueDeltaDetector,
    FirmwareValidationDetector,
    ReplayDetector
)
from ids.alerts import AlertLogger, AlertLevel, SecurityResponseHandler


class IDSCore:
    """Core IDS Engine - Monitors CAN and OCPP traffic for anomalies"""
    
    def __init__(self, can_interface: str = 'vcan0'):
        """
        Initialize IDS Core
        
        Args:
            can_interface: CAN interface to monitor
        """
        self.can_interface_name = can_interface
        self.can_if: Optional[CANInterface] = None
        self.running = False
        
        # Initialize alert logger and security response
        self.alert_logger = AlertLogger()
        self.security_handler = SecurityResponseHandler()
        
        # Initialize all detectors
        self._init_detectors()
        
        print("[IDS CORE] Intrusion Detection System initialized")
        print(f"[IDS CORE] CAN Interface: {can_interface}")
        print(f"[IDS CORE] Active Detectors: {len(self.detectors)}")
    
    def _init_detectors(self):
        """Initialize all anomaly detectors"""
        self.detectors = {
            "frequency_spike": FrequencySpikeDetector(threshold_hz=20.0),
            "ocpp_can_delay": OCPPCANDelayDetector(max_delay_seconds=2.0),
            "out_of_range": OutOfRangeDetector(),
            "rate_change": RateChangeDetector(expected_rate_hz=1.0, tolerance=0.2),
            "bypass": BypassDetector(),
            "burst": BurstDetector(max_messages=10, window_seconds=1.0),
            "connection_flood": ConnectionFloodDetector(max_connections=10, window_seconds=5.0),
            "value_delta": ValueDeltaDetector(),
            "firmware": FirmwareValidationDetector(),
            "replay": ReplayDetector(window_seconds=60.0, max_duplicates=3)
        }
    
    def start(self):
        """Start the IDS"""
        print("\n" + "="*60)
        print("🛡️  STARTING INTRUSION DETECTION SYSTEM")
        print("="*60)
        
        # Connect to CAN interface
        self.can_if = CANInterface(self.can_interface_name)
        if not self.can_if.connect():
            print("[IDS ERROR] Failed to connect to CAN interface")
            return False
        
        # Set security handler CAN interface
        self.security_handler.can_interface = self.can_if
        
        self.running = True
        self.alert_logger.log_info("IDS system started", "System")
        
        # Start CAN monitoring thread
        can_thread = threading.Thread(target=self._monitor_can, daemon=True)
        can_thread.start()
        
        print("[IDS CORE] CAN monitoring started")
        print("[IDS CORE] System is now active")
        print("="*60 + "\n")
        
        return True
    
    def stop(self):
        """Stop the IDS"""
        print("\n[IDS CORE] Stopping IDS...")
        self.running = False
        
        if self.can_if:
            self.can_if.disconnect()
        
        self.alert_logger.log_info("IDS system stopped", "System")
        self.alert_logger.print_stats()
        print("[IDS CORE] IDS stopped\n")
    
    def _monitor_can(self):
        """Monitor CAN bus for anomalies"""
        print("[IDS CORE] CAN monitoring thread started")
        
        while self.running:
            msg = self.can_if.receive_message(timeout=0.1)
            
            if msg:
                self._process_can_message(msg)
    
    def _process_can_message(self, msg):
        """
        Process a CAN message through all detectors
        
        Args:
            msg: CAN message
        """
        can_id = msg.arbitration_id
        data = bytes(msg.data)
        timestamp = time.time()
        
        # Anomaly 1: Frequency Spike
        alert = self.detectors["frequency_spike"].detect(can_id, timestamp)
        if alert:
            self.alert_logger.log_warning(alert, "Frequency Spike")
            self.security_handler.trigger_safe_mode("Frequency Spike", f"CAN ID 0x{can_id:03X}")
        
        # Anomaly 6: Message Burst (Error messages)
        if can_id == 0x301:  # Error message ID
            alert = self.detectors["burst"].detect(can_id, timestamp)
            if alert:
                self.alert_logger.log_warning(alert, "Error Burst")
                self.security_handler.trigger_safe_mode("Error Burst", f"CAN ID 0x{can_id:03X}")
        
        # Anomaly 10: Replay Attack
        alert = self.detectors["replay"].detect(can_id, data, timestamp)
        if alert:
            self.alert_logger.log_critical(alert, "Replay Attack")
            self.security_handler.trigger_safe_mode("Replay Attack", f"CAN ID 0x{can_id:03X}")
        
        # Anomaly 5: OCPP Bypass (for start commands)
        if can_id == 0x200:  # Start command ID
            alert = self.detectors["bypass"].detect(can_id, timestamp)
            if alert:
                self.alert_logger.log_critical(alert, "OCPP Bypass")
                self.security_handler.trigger_safe_mode("OCPP Bypass", f"CAN ID 0x{can_id:03X}")
        
        # Anomaly 3: Out-of-Range (check current values)
        if can_id == 0x400 and len(data) >= 2:  # Voltage/Current message
            current = data[1]  # Assume byte 1 is current
            alert = self.detectors["out_of_range"].detect("current", current)
            if alert:
                self.alert_logger.log_warning(alert, "Out-of-Range")
        
        # Anomaly 4: Rate Change (for periodic messages)
        if can_id == 0x300:  # Temperature/periodic message
            alert = self.detectors["rate_change"].detect(f"CAN_0x{can_id:03X}", timestamp)
            if alert:
                self.alert_logger.log_warning(alert, "Rate Change")
    
    def process_ocpp_message(self, message_type: str, message_data: dict):
        """
        Process OCPP message through detectors
        
        Args:
            message_type: Type of OCPP message
            message_data: Message data dict
        """
        timestamp = time.time()
        
        # Anomaly 9: Firmware Mismatch
        if message_type == "BootNotification":
            firmware = message_data.get("firmwareVersion", "unknown")
            alert = self.detectors["firmware"].detect(firmware)
            if alert:
                self.alert_logger.log_critical(alert, "Firmware Mismatch")
                self.security_handler.trigger_safe_mode("Firmware Mismatch", f"Version: {firmware}")
        
        # Anomaly 2: OCPP → CAN Delay
        if message_type == "RemoteStartTransaction":
            # Register OCPP command, expect CAN response
            self.detectors["ocpp_can_delay"].register_ocpp_command("RemoteStart", 0x200)
            self.detectors["bypass"].authorize_can_command(0x200)
        
        # Anomaly 4 & 8: MeterValues rate and delta
        if message_type == "MeterValues":
            # Check rate
            alert = self.detectors["rate_change"].detect("MeterValues", timestamp)
            if alert:
                self.alert_logger.log_warning(alert, "MeterValues Rate")
            
            # Check value deltas
            for meter_value in message_data.get("meterValue", []):
                for sampled_value in meter_value.get("sampledValue", []):
                    measurand = sampled_value.get("measurand", "")
                    value = float(sampled_value.get("value", 0))
                    
                    if "Energy" in measurand:
                        alert = self.detectors["value_delta"].detect("energy", value, timestamp)
                        if alert:
                            self.alert_logger.log_critical(alert, "Ghost Measurement")
                            self.security_handler.trigger_safe_mode("Ghost Measurement", f"Energy: {value}")
    
    def process_websocket_connection(self):
        """Process new WebSocket connection"""
        # Anomaly 7: Connection Flood
        alert = self.detectors["connection_flood"].detect()
        if alert:
            self.alert_logger.log_critical(alert, "WebSocket Flood")
            self.security_handler.trigger_safe_mode("WebSocket Flood", "Too many connections")
    
    def run(self):
        """Run the IDS (blocking)"""
        if self.start():
            try:
                # Keep running
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[IDS CORE] Interrupted by user")
            finally:
                self.stop()


if __name__ == "__main__":
    print("IDS Core Engine - Standalone Mode")
    print("Press Ctrl+C to stop\n")
    
    ids = IDSCore('vcan0')
    ids.run()
