"""
Anomaly 9: Firmware Mismatch Test Scenario
"""

import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ocpp.ocpp_client import OCPPClient
from ocpp.ocpp_server import OCPPServer
import threading
import time


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


async def run_firmware_attack(config):
    """Execute firmware mismatch attack"""
    print("="*60)
    print("ANOMALY 9: FIRMWARE MISMATCH ATTACK")
    print("="*60)
    print(f"Malicious Firmware: {config['malicious_firmware']}")
    print(f"Allowed Versions: {config['allowed_versions']}")
    print("="*60 + "\n")
    
    # Start OCPP server in background
    server = OCPPServer(host="localhost", port=9000)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Wait for server to start
    
    # Connect client with malicious firmware
    client = OCPPClient("ws://localhost:9000")
    
    if await client.connect():
        print(f"[ATTACK] Sending BootNotification with malicious firmware...")
        
        await client.send_boot_notification(
            charge_point_vendor="Hacker",
            charge_point_model="Injector-X",
            firmware_version=config['malicious_firmware']
        )
        
        await asyncio.sleep(2)
        await client.disconnect()
    
    print(f"\n[ATTACK] Attack completed")
    print(f"[ATTACK] Expected IDS alert: Firmware mismatch detected\n")


if __name__ == "__main__":
    print("\n🔴 Anomaly 9: Firmware Mismatch Attack Simulator\n")
    
    config = load_config()
    asyncio.run(run_firmware_attack(config))
    
    print("="*60)
    print("Attack scenario completed")
    print("="*60 + "\n")
