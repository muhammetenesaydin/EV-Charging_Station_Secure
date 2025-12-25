"""
Anomaly 3: Out-of-Range Payload Test Scenario

Sends CAN messages with out-of-range values
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from can.can_utils import CANInterface
from ids.ids_core import IDSCore


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def run_out_of_range_attack(config):
    """Execute out-of-range attack"""
    can_id = int(config['can_id'], 16)
    attack_value = config['attack_value']
    valid_range = config['valid_range']
    
    print("="*60)
    print("ANOMALY 3: OUT-OF-RANGE PAYLOAD ATTACK")
    print("="*60)
    print(f"CAN ID: 0x{can_id:03X}")
    print(f"Parameter: {config['parameter']}")
    print(f"Attack Value: {attack_value}")
    print(f"Valid Range: {valid_range[0]}-{valid_range[1]}")
    print("="*60 + "\n")
    
    # Connect to CAN
    can_if = CANInterface('vcan0')
    if not can_if.connect():
        print("ERROR: Failed to connect to vcan0")
        return
    
    # Start IDS
    ids = IDSCore('vcan0')
    ids.start()
    
    print(f"[ATTACK] Sending out-of-range {config['parameter']} value: {attack_value}...")
    
    # Send CAN message with out-of-range value
    # Format: [command_byte, current_value, voltage_high, voltage_low]
    can_if.send_message(
        arbitration_id=can_id,
        data=[0x04, attack_value, 0x00, 0xE6],  # 230V = 0x00E6
        log=True
    )
    
    time.sleep(2)
    
    print(f"\n[ATTACK] Attack completed")
    print(f"[ATTACK] Expected IDS alert: Out-of-range {config['parameter']} detected\n")
    
    ids.stop()
    can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomaly 3: Out-of-Range Payload Attack Simulator\n")
    
    config = load_config()
    run_out_of_range_attack(config)
    
    print("="*60)
    print("Attack scenario completed")
    print("="*60 + "\n")
