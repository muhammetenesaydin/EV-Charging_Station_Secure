"""
Alert and Logging System for IDS

Handles alert generation, logging, and statistics tracking
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertLogger:
    """Manages alert logging and statistics"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize alert logger
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = log_dir
        self.alert_log_file = os.path.join(log_dir, "ids_alerts.log")
        self.stats_file = os.path.join(log_dir, "ids_stats.json")
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_alerts": 0,
            "alerts_by_level": {level.value: 0 for level in AlertLevel},
            "alerts_by_type": {},
            "session_start": datetime.now().isoformat()
        }
        
        # Load existing stats if available
        self._load_stats()
    
    def _load_stats(self):
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    # Merge with current stats
                    self.stats["alerts_by_type"] = saved_stats.get("alerts_by_type", {})
            except Exception as e:
                print(f"[ALERT LOGGER] Warning: Could not load stats: {e}")
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"[ALERT LOGGER] Warning: Could not save stats: {e}")
    
    def log_alert(self, 
                  message: str, 
                  level: AlertLevel = AlertLevel.WARNING,
                  anomaly_type: str = "Unknown",
                  details: Optional[Dict] = None):
        """
        Log an alert
        
        Args:
            message: Alert message
            level: Alert severity level
            anomaly_type: Type of anomaly detected
            details: Additional details dict
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Format alert
        alert_line = f"[{timestamp}] [{level.value}] [{anomaly_type}] {message}"
        
        if details:
            alert_line += f" | Details: {json.dumps(details)}"
        
        alert_line += "\n"
        
        # Write to file
        try:
            with open(self.alert_log_file, 'a') as f:
                f.write(alert_line)
        except Exception as e:
            print(f"[ALERT LOGGER ERROR] Failed to write to log: {e}")
        
        # Print to console
        self._print_alert(message, level, timestamp)
        
        # Update statistics
        self.stats["total_alerts"] += 1
        self.stats["alerts_by_level"][level.value] += 1
        
        if anomaly_type not in self.stats["alerts_by_type"]:
            self.stats["alerts_by_type"][anomaly_type] = 0
        self.stats["alerts_by_type"][anomaly_type] += 1
        
        self._save_stats()
    
    def _print_alert(self, message: str, level: AlertLevel, timestamp: str):
        """Print formatted alert to console"""
        # Color codes for different levels
        colors = {
            AlertLevel.INFO: "\033[94m",      # Blue
            AlertLevel.WARNING: "\033[93m",   # Yellow
            AlertLevel.CRITICAL: "\033[91m",  # Red
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] {message}{reset}")
    
    def log_info(self, message: str, anomaly_type: str = "Info"):
        """Log info level alert"""
        self.log_alert(message, AlertLevel.INFO, anomaly_type)
    
    def log_warning(self, message: str, anomaly_type: str = "Warning"):
        """Log warning level alert"""
        self.log_alert(message, AlertLevel.WARNING, anomaly_type)
    
    def log_critical(self, message: str, anomaly_type: str = "Critical"):
        """Log critical level alert"""
        self.log_alert(message, AlertLevel.CRITICAL, anomaly_type)
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return self.stats.copy()
    
    def print_stats(self):
        """Print statistics summary"""
        print("\n" + "="*60)
        print("IDS STATISTICS SUMMARY")
        print("="*60)
        print(f"Session Start: {self.stats['session_start']}")
        print(f"Total Alerts: {self.stats['total_alerts']}")
        print("\nAlerts by Level:")
        for level, count in self.stats['alerts_by_level'].items():
            print(f"  {level}: {count}")
        print("\nAlerts by Type:")
        for anomaly_type, count in sorted(self.stats['alerts_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {anomaly_type}: {count}")
        print("="*60 + "\n")
    
    def clear_logs(self):
        """Clear log files"""
        try:
            if os.path.exists(self.alert_log_file):
                os.remove(self.alert_log_file)
            print("[ALERT LOGGER] Alert log cleared")
        except Exception as e:
            print(f"[ALERT LOGGER ERROR] Failed to clear logs: {e}")
    
    def get_recent_alerts(self, count: int = 10) -> List[str]:
        """
        Get recent alerts from log file
        
        Args:
            count: Number of recent alerts to retrieve
            
        Returns:
            List of alert lines
        """
        if not os.path.exists(self.alert_log_file):
            return []
        
        try:
            with open(self.alert_log_file, 'r') as f:
                lines = f.readlines()
                return lines[-count:] if len(lines) > count else lines
        except Exception as e:
            print(f"[ALERT LOGGER ERROR] Failed to read alerts: {e}")
            return []


class SecurityResponseHandler:
    """Handles security responses to detected anomalies"""
    
    def __init__(self, can_interface=None):
        """
        Initialize security response handler
        
        Args:
            can_interface: CAN interface for sending safe mode commands
        """
        self.can_interface = can_interface
        self.response_count = 0
    
    def trigger_safe_mode(self, anomaly_type: str, details: str = ""):
        """
        Trigger safe mode response
        
        Args:
            anomaly_type: Type of anomaly that triggered response
            details: Additional details
        """
        self.response_count += 1
        
        print("\n" + "!"*60)
        print(f"🚨 SECURITY RESPONSE TRIGGERED 🚨")
        print(f"Anomaly Type: {anomaly_type}")
        if details:
            print(f"Details: {details}")
        print(f"Response #{self.response_count}")
        print("!"*60 + "\n")
        
        # Send safe mode command to CAN bus if available
        if self.can_interface:
            try:
                # Send safe mode command (CAN ID 0x001)
                self.can_interface.send_message(
                    arbitration_id=0x001,
                    data=[0xDE, 0xAD, 0x01],  # Safe mode command
                    log=True
                )
                print("[SECURITY] Safe mode command sent to CAN bus (ID: 0x001)")
            except Exception as e:
                print(f"[SECURITY ERROR] Failed to send safe mode command: {e}")
        else:
            print("[SECURITY] Simulated: Safe mode command would be sent to CAN bus")
    
    def block_connection(self, ip_address: str, reason: str = ""):
        """
        Block a connection (simulated)
        
        Args:
            ip_address: IP address to block
            reason: Reason for blocking
        """
        print(f"\n🚫 CONNECTION BLOCKED: {ip_address}")
        if reason:
            print(f"   Reason: {reason}")
        print()


if __name__ == "__main__":
    # Test alert logger
    print("Testing Alert Logger\n")
    
    logger = AlertLogger()
    
    # Test different alert levels
    logger.log_info("IDS system started", "System")
    logger.log_warning("Frequency spike detected on CAN ID 0x9FF", "Frequency Spike")
    logger.log_critical("Replay attack detected", "Replay Attack")
    logger.log_warning("Out-of-range current value: 255A", "Out-of-Range")
    
    # Print statistics
    logger.print_stats()
    
    # Test security response
    print("\nTesting Security Response Handler\n")
    handler = SecurityResponseHandler()
    handler.trigger_safe_mode("Frequency Spike", "CAN ID 0x9FF at 100 msg/s")
    handler.block_connection("192.168.1.100", "WebSocket flood detected")
