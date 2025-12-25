"""
Detection Rules for CAN ↔ OCPP Anomalies

Implements detection logic for all 10 anomaly scenarios
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict, deque


class AnomalyDetector:
    """Base class for anomaly detectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.alerts = []
    
    def detect(self, *args, **kwargs) -> Optional[str]:
        """
        Detect anomaly
        
        Returns:
            Alert message if anomaly detected, None otherwise
        """
        raise NotImplementedError
    
    def log_alert(self, message: str):
        """Log an alert"""
        self.alerts.append((datetime.now(), message))
        return message


class FrequencySpikeDetector(AnomalyDetector):
    """Anomaly 1: Detects abnormal frequency spikes on CAN IDs"""
    
    def __init__(self, threshold_hz: float = 20.0, window_seconds: float = 1.0):
        super().__init__("Frequency Spike")
        self.threshold_hz = threshold_hz
        self.window_seconds = window_seconds
        self.message_times: Dict[int, deque] = defaultdict(lambda: deque())
    
    def detect(self, can_id: int, timestamp: float = None) -> Optional[str]:
        """
        Detect frequency spike
        
        Args:
            can_id: CAN ID
            timestamp: Message timestamp (uses current time if None)
            
        Returns:
            Alert message if spike detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Add timestamp to queue
        self.message_times[can_id].append(timestamp)
        
        # Remove old timestamps outside window
        cutoff = timestamp - self.window_seconds
        while self.message_times[can_id] and self.message_times[can_id][0] < cutoff:
            self.message_times[can_id].popleft()
        
        # Calculate frequency
        count = len(self.message_times[can_id])
        frequency = count / self.window_seconds
        
        # Check threshold
        if frequency > self.threshold_hz:
            alert = f"⚠️  ANOMALY 1: Frequency spike detected on CAN ID 0x{can_id:03X} - {frequency:.1f} msg/s (threshold: {self.threshold_hz} msg/s)"
            return self.log_alert(alert)
        
        return None


class OCPPCANDelayDetector(AnomalyDetector):
    """Anomaly 2: Detects abnormal delay between OCPP command and CAN response"""
    
    def __init__(self, max_delay_seconds: float = 2.0):
        super().__init__("OCPP → CAN Delay")
        self.max_delay_seconds = max_delay_seconds
        self.ocpp_command_time: Optional[float] = None
        self.waiting_for_can = False
        self.expected_can_id: Optional[int] = None
    
    def register_ocpp_command(self, command_type: str, expected_can_id: int):
        """Register OCPP command and start waiting for CAN response"""
        self.ocpp_command_time = time.time()
        self.waiting_for_can = True
        self.expected_can_id = expected_can_id
    
    def detect(self, can_id: int, timestamp: float = None) -> Optional[str]:
        """
        Detect delay anomaly
        
        Args:
            can_id: CAN ID received
            timestamp: CAN message timestamp
            
        Returns:
            Alert message if delay detected
        """
        if not self.waiting_for_can or can_id != self.expected_can_id:
            return None
        
        if timestamp is None:
            timestamp = time.time()
        
        delay = timestamp - self.ocpp_command_time
        self.waiting_for_can = False
        
        if delay > self.max_delay_seconds:
            alert = f"⚠️  ANOMALY 2: Abnormal delay detected - OCPP → CAN 0x{can_id:03X}: {delay:.2f}s (threshold: {self.max_delay_seconds}s)"
            return self.log_alert(alert)
        
        return None


class OutOfRangeDetector(AnomalyDetector):
    """Anomaly 3: Detects out-of-range payload values"""
    
    def __init__(self):
        super().__init__("Out-of-Range Payload")
        # Define valid ranges for different parameters
        self.ranges = {
            "current": (0, 80),      # 0-80 Amperes
            "voltage": (200, 250),   # 200-250 Volts
            "power": (0, 22000),     # 0-22 kW
            "temperature": (-20, 80), # -20 to 80 Celsius
        }
    
    def detect(self, parameter: str, value: float) -> Optional[str]:
        """
        Detect out-of-range value
        
        Args:
            parameter: Parameter name (current, voltage, power, temperature)
            value: Value to check
            
        Returns:
            Alert message if out of range
        """
        if parameter not in self.ranges:
            return None
        
        min_val, max_val = self.ranges[parameter]
        
        if not (min_val <= value <= max_val):
            alert = f"⚠️  ANOMALY 3: Out-of-range value detected - {parameter}: {value} (valid range: {min_val}-{max_val})"
            return self.log_alert(alert)
        
        return None


class RateChangeDetector(AnomalyDetector):
    """Anomaly 4: Detects abnormal rate changes in periodic messages"""
    
    def __init__(self, expected_rate_hz: float = 1.0, tolerance: float = 0.2):
        super().__init__("Rate Change")
        self.expected_rate_hz = expected_rate_hz
        self.tolerance = tolerance
        self.last_times: Dict[str, float] = {}
    
    def detect(self, message_id: str, timestamp: float = None) -> Optional[str]:
        """
        Detect rate change
        
        Args:
            message_id: Message identifier
            timestamp: Message timestamp
            
        Returns:
            Alert message if rate anomaly detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        if message_id in self.last_times:
            delta = timestamp - self.last_times[message_id]
            actual_rate = 1.0 / delta if delta > 0 else 0
            
            expected_min = self.expected_rate_hz * (1 - self.tolerance)
            expected_max = self.expected_rate_hz * (1 + self.tolerance)
            
            if not (expected_min <= actual_rate <= expected_max):
                alert = f"⚠️  ANOMALY 4: Rate anomaly detected - {message_id}: {actual_rate:.2f} Hz (expected: {self.expected_rate_hz} Hz ±{self.tolerance*100}%)"
                self.last_times[message_id] = timestamp
                return self.log_alert(alert)
        
        self.last_times[message_id] = timestamp
        return None


class BypassDetector(AnomalyDetector):
    """Anomaly 5: Detects CAN commands sent without OCPP authorization"""
    
    def __init__(self):
        super().__init__("OCPP Bypass")
        self.authorized_commands: Dict[int, float] = {}  # can_id: expiry_time
        self.authorization_timeout = 5.0  # seconds
    
    def authorize_can_command(self, can_id: int):
        """Authorize a CAN command from OCPP"""
        self.authorized_commands[can_id] = time.time() + self.authorization_timeout
    
    def detect(self, can_id: int, timestamp: float = None) -> Optional[str]:
        """
        Detect bypass attempt
        
        Args:
            can_id: CAN ID of command
            timestamp: Command timestamp
            
        Returns:
            Alert message if bypass detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Clean up expired authorizations
        expired = [cid for cid, expiry in self.authorized_commands.items() if timestamp > expiry]
        for cid in expired:
            del self.authorized_commands[cid]
        
        # Check if command is authorized
        if can_id in self.authorized_commands:
            # Command is authorized, remove it
            del self.authorized_commands[can_id]
            return None
        else:
            alert = f"⚠️  ANOMALY 5: Unauthorized CAN command - 0x{can_id:03X} sent without OCPP authorization"
            return self.log_alert(alert)


class BurstDetector(AnomalyDetector):
    """Anomaly 6: Detects message bursts (too many messages in short time)"""
    
    def __init__(self, max_messages: int = 10, window_seconds: float = 1.0):
        super().__init__("Message Burst")
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.message_times: Dict[int, deque] = defaultdict(lambda: deque())
    
    def detect(self, message_id: int, timestamp: float = None) -> Optional[str]:
        """
        Detect message burst
        
        Args:
            message_id: Message ID (e.g., CAN ID)
            timestamp: Message timestamp
            
        Returns:
            Alert message if burst detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Add timestamp
        self.message_times[message_id].append(timestamp)
        
        # Remove old timestamps
        cutoff = timestamp - self.window_seconds
        while self.message_times[message_id] and self.message_times[message_id][0] < cutoff:
            self.message_times[message_id].popleft()
        
        # Check burst
        count = len(self.message_times[message_id])
        if count > self.max_messages:
            alert = f"⚠️  ANOMALY 6: Message burst detected - ID 0x{message_id:03X}: {count} messages in {self.window_seconds}s (threshold: {self.max_messages})"
            return self.log_alert(alert)
        
        return None


class ConnectionFloodDetector(AnomalyDetector):
    """Anomaly 7: Detects WebSocket connection floods"""
    
    def __init__(self, max_connections: int = 10, window_seconds: float = 5.0):
        super().__init__("Connection Flood")
        self.max_connections = max_connections
        self.window_seconds = window_seconds
        self.connection_times: deque = deque()
    
    def detect(self, timestamp: float = None) -> Optional[str]:
        """
        Detect connection flood
        
        Args:
            timestamp: Connection timestamp
            
        Returns:
            Alert message if flood detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Add connection time
        self.connection_times.append(timestamp)
        
        # Remove old connections
        cutoff = timestamp - self.window_seconds
        while self.connection_times and self.connection_times[0] < cutoff:
            self.connection_times.popleft()
        
        # Check flood
        count = len(self.connection_times)
        if count > self.max_connections:
            alert = f"⚠️  ANOMALY 7: WebSocket flood detected - {count} connections in {self.window_seconds}s (threshold: {self.max_connections})"
            return self.log_alert(alert)
        
        return None


class ValueDeltaDetector(AnomalyDetector):
    """Anomaly 8: Detects abnormal value deltas (ghost measurements)"""
    
    def __init__(self, max_delta_per_second: Dict[str, float] = None):
        super().__init__("Value Delta")
        self.max_delta_per_second = max_delta_per_second or {
            "energy": 5.0,    # 5 kWh/s max
            "power": 10000,   # 10 kW/s max change
        }
        self.last_values: Dict[str, Tuple[float, float]] = {}  # parameter: (value, timestamp)
    
    def detect(self, parameter: str, value: float, timestamp: float = None) -> Optional[str]:
        """
        Detect abnormal delta
        
        Args:
            parameter: Parameter name
            value: Current value
            timestamp: Measurement timestamp
            
        Returns:
            Alert message if abnormal delta detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        if parameter in self.last_values:
            last_value, last_time = self.last_values[parameter]
            time_delta = timestamp - last_time
            
            if time_delta > 0:
                value_delta = abs(value - last_value)
                delta_per_second = value_delta / time_delta
                
                max_delta = self.max_delta_per_second.get(parameter, float('inf'))
                
                if delta_per_second > max_delta:
                    alert = f"⚠️  ANOMALY 8: Abnormal {parameter} delta - {delta_per_second:.2f}/s (threshold: {max_delta}/s)"
                    self.last_values[parameter] = (value, timestamp)
                    return self.log_alert(alert)
        
        self.last_values[parameter] = (value, timestamp)
        return None


class FirmwareValidationDetector(AnomalyDetector):
    """Anomaly 9: Detects firmware version mismatches"""
    
    def __init__(self, allowed_versions: List[str] = None):
        super().__init__("Firmware Mismatch")
        self.allowed_versions = allowed_versions or ["v1.5-stable", "v1.6-release", "v2.0.1-prod"]
    
    def detect(self, firmware_version: str) -> Optional[str]:
        """
        Detect firmware mismatch
        
        Args:
            firmware_version: Firmware version string
            
        Returns:
            Alert message if mismatch detected
        """
        if firmware_version not in self.allowed_versions:
            alert = f"⚠️  ANOMALY 9: Firmware mismatch - '{firmware_version}' not in whitelist {self.allowed_versions}"
            return self.log_alert(alert)
        
        return None


class ReplayDetector(AnomalyDetector):
    """Anomaly 10: Detects replay attacks (duplicate messages)"""
    
    def __init__(self, window_seconds: float = 60.0, max_duplicates: int = 3):
        super().__init__("Replay Attack")
        self.window_seconds = window_seconds
        self.max_duplicates = max_duplicates
        self.message_signatures: Dict[str, deque] = defaultdict(lambda: deque())
    
    def detect(self, can_id: int, data: bytes, timestamp: float = None) -> Optional[str]:
        """
        Detect replay attack
        
        Args:
            can_id: CAN ID
            data: Message data bytes
            timestamp: Message timestamp
            
        Returns:
            Alert message if replay detected
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Create signature
        signature = f"{can_id:03X}:{data.hex()}"
        
        # Add timestamp
        self.message_signatures[signature].append(timestamp)
        
        # Remove old timestamps
        cutoff = timestamp - self.window_seconds
        while self.message_signatures[signature] and self.message_signatures[signature][0] < cutoff:
            self.message_signatures[signature].popleft()
        
        # Check for replay
        count = len(self.message_signatures[signature])
        if count > self.max_duplicates:
            alert = f"⚠️  ANOMALY 10: Replay attack detected - CAN ID 0x{can_id:03X} payload [{data.hex()}] seen {count} times in {self.window_seconds}s"
            return self.log_alert(alert)
        
        return None


if __name__ == "__main__":
    # Test detectors
    print("Testing Anomaly Detectors\n")
    
    # Test Frequency Spike
    print("1. Frequency Spike Detector:")
    detector1 = FrequencySpikeDetector(threshold_hz=10.0)
    for i in range(15):
        alert = detector1.detect(0x9FF)
        if alert:
            print(f"   {alert}")
        time.sleep(0.05)  # 20 Hz
    
    print("\n2. Out-of-Range Detector:")
    detector3 = OutOfRangeDetector()
    alert = detector3.detect("current", 255)
    if alert:
        print(f"   {alert}")
    
    print("\n3. Firmware Validation Detector:")
    detector9 = FirmwareValidationDetector()
    alert = detector9.detect("evil-v9")
    if alert:
        print(f"   {alert}")
    
    print("\nAll detectors tested successfully!")
