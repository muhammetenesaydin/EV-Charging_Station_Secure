"""
Anomaly 2: OCPP → CAN Delay Test Scenario

Simulates abnormal delay between OCPP command and CAN response
"""

import sys
import os
import time
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from can.can_utils import CANInterface
from ids.ids_core import IDSCore


def load_config():
    """Load configuration"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def run_delay_attack(config):
    """Execute delay attack"""
    can_id = int(config['expected_can_id'], 16)
    delay = config['attack_delay_seconds']
    
    print("="*60)
    print("ANOMALY 2: OCPP → CAN DELAY ATTACK")
    print("="*60)
    print(f"Expected CAN ID: 0x{can_id:03X}")
    print(f"Attack Delay: {delay} seconds")
    print(f"Normal Delay: {config['normal_delay_seconds']} seconds")
    print(f"Detection Threshold: {config['threshold_seconds']} seconds")
    print("="*60 + "\n")
    
    # Connect to CAN
    can_if = CANInterface('vcan0')
    if not can_if.connect():
        print("ERROR: Failed to connect to vcan0")
        return
    
    print("[ATTACK] Simulating OCPP RemoteStartTransaction command...")
    print(f"[ATTACK] Delaying CAN response by {delay} seconds...\n")
    
    # Initialize IDS to register OCPP command
    ids = IDSCore('vcan0')
    ids.start()
    
    # Simulate OCPP command
    ids.process_ocpp_message("RemoteStartTransaction", {
        "connectorId": 1,
        "idTag": "TEST_TAG"
    })
    
    print(f"[ATTACK] Waiting {delay} seconds before sending CAN response...")
    time.sleep(delay)
    
    # Send delayed CAN response
    print(f"[ATTACK] Sending CAN response (ID: 0x{can_id:03X})...")
    can_if.send_message(can_id, [0x01, 0x00, 0x00, 0x00])
    
    time.sleep(1)
    
    print(f"\n[ATTACK] Attack completed")
    print(f"[ATTACK] Expected IDS alert: Delay > {config['threshold_seconds']}s detected\n")
    
    ids.stop()
    can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomaly 2: OCPP → CAN Delay Attack Simulator\n")
    
    config = load_config()
    run_delay_attack(config)
    
    print("="*60)
    print("Attack scenario completed")
    print("="*60 + "\n")
