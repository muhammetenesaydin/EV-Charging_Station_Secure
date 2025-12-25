"""
Anomaly 1: Frequency Spike Test Scenario

Simulates abnormal frequency spike on CAN bus
"""

import sys
import os
import time
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from can.can_utils import CANInterface


def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def run_frequency_spike_attack(config):
    """
    Execute frequency spike attack
    
    Args:
        config: Configuration dict
    """
    can_id = int(config['can_id'], 16)
    frequency_hz = config['frequency_hz']
    duration = config['duration_seconds']
    
    print("="*60)
    print("ANOMALY 1: FREQUENCY SPIKE ATTACK")
    print("="*60)
    print(f"CAN ID: 0x{can_id:03X}")
    print(f"Frequency: {frequency_hz} Hz")
    print(f"Duration: {duration} seconds")
    print(f"Expected Detection: Frequency > {config['threshold_hz']} Hz")
    print("="*60 + "\n")
    
    # Connect to CAN
    can_if = CANInterface('vcan0')
    if not can_if.connect():
        print("ERROR: Failed to connect to vcan0")
        print("Make sure vcan0 is set up:")
        print("  sudo modprobe vcan")
        print("  sudo ip link add dev vcan0 type vcan")
        print("  sudo ip link set up vcan0")
        return
    
    print(f"[ATTACK] Starting frequency spike attack...")
    print(f"[ATTACK] Sending {frequency_hz} messages/second for {duration} seconds\n")
    
    interval = 1.0 / frequency_hz
    start_time = time.time()
    message_count = 0
    
    try:
        while (time.time() - start_time) < duration:
            # Send CAN message
            can_if.send_message(
                arbitration_id=can_id,
                data=[0xFF, 0xFF, 0xFF, 0xFF],
                log=False  # Don't log each message to avoid spam
            )
            message_count += 1
            time.sleep(interval)
        
        elapsed = time.time() - start_time
        actual_frequency = message_count / elapsed
        
        print(f"\n[ATTACK] Attack completed")
        print(f"[ATTACK] Messages sent: {message_count}")
        print(f"[ATTACK] Actual frequency: {actual_frequency:.1f} Hz")
        print(f"[ATTACK] Expected IDS alert: Frequency spike detected\n")
    
    except KeyboardInterrupt:
        print("\n[ATTACK] Attack interrupted by user")
    
    finally:
        can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomaly 1: Frequency Spike Attack Simulator\n")
    
    # Load configuration
    config = load_config()
    
    # Run attack
    run_frequency_spike_attack(config)
    
    print("="*60)
    print("Attack scenario completed")
    print("Check IDS logs for detection alerts")
    print("="*60 + "\n")
