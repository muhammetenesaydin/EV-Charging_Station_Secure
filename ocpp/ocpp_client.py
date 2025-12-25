"""
OCPP WebSocket Client

Mock OCPP Charge Point client for testing
"""

import asyncio
import websockets
import json
from datetime import datetime
from typing import Optional, Dict
from ocpp.ocpp_messages import OCPPMessageBuilder


class OCPPClient:
    """Mock OCPP 1.6 Charge Point Client"""
    
    def __init__(self, server_url: str = "ws://localhost:9000"):
        """
        Initialize OCPP client
        
        Args:
            server_url: WebSocket server URL
        """
        self.server_url = server_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.builder = OCPPMessageBuilder()
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Connect to OCPP server
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[OCPP CLIENT] [{timestamp}] Connected to {self.server_url}")
            return True
        except Exception as e:
            print(f"[OCPP CLIENT ERROR] Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[OCPP CLIENT] [{timestamp}] Disconnected")
    
    async def send_message(self, message: Dict, message_type: str = "Unknown") -> Optional[Dict]:
        """
        Send message to server
        
        Args:
            message: Message dict
            message_type: Message type for logging
            
        Returns:
            Server response or None
        """
        if not self.connected or not self.websocket:
            print("[OCPP CLIENT ERROR] Not connected to server")
            return None
        
        try:
            message_str = json.dumps(message)
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[OCPP CLIENT] [{timestamp}] Sending {message_type}")
            
            await self.websocket.send(message_str)
            
            # Wait for response
            response_str = await self.websocket.recv()
            response = json.loads(response_str)
            
            print(f"[OCPP CLIENT] [{timestamp}] Response: {response}")
            return response
        
        except Exception as e:
            print(f"[OCPP CLIENT ERROR] Failed to send message: {e}")
            return None
    
    async def send_boot_notification(self, **kwargs) -> Optional[Dict]:
        """Send BootNotification message"""
        message = self.builder.boot_notification(**kwargs)
        return await self.send_message(message, "BootNotification")
    
    async def send_remote_start(self, connector_id: int = 1, id_tag: str = "TEST_TAG") -> Optional[Dict]:
        """Send RemoteStartTransaction message"""
        message = self.builder.remote_start_transaction(connector_id, id_tag)
        return await self.send_message(message, "RemoteStartTransaction")
    
    async def send_remote_stop(self, transaction_id: int) -> Optional[Dict]:
        """Send RemoteStopTransaction message"""
        message = self.builder.remote_stop_transaction(transaction_id)
        return await self.send_message(message, "RemoteStopTransaction")
    
    async def send_meter_values(self, **kwargs) -> Optional[Dict]:
        """Send MeterValues message"""
        message = self.builder.meter_values(**kwargs)
        return await self.send_message(message, "MeterValues")
    
    async def send_heartbeat(self) -> Optional[Dict]:
        """Send Heartbeat message"""
        message = self.builder.heartbeat()
        return await self.send_message(message, "Heartbeat")
    
    async def send_status_notification(self, **kwargs) -> Optional[Dict]:
        """Send StatusNotification message"""
        message = self.builder.status_notification(**kwargs)
        return await self.send_message(message, "StatusNotification")


async def test_client():
    """Test the OCPP client"""
    client = OCPPClient("ws://localhost:9000")
    
    if await client.connect():
        # Send BootNotification
        await client.send_boot_notification(
            charge_point_vendor="TestVendor",
            charge_point_model="TestModel-X",
            firmware_version="v1.6-release"
        )
        
        await asyncio.sleep(1)
        
        # Send Heartbeat
        await client.send_heartbeat()
        
        await asyncio.sleep(1)
        
        # Send MeterValues
        await client.send_meter_values(
            connector_id=1,
            energy_wh=1500,
            power_w=7400,
            current_a=32
        )
        
        await asyncio.sleep(1)
        
        await client.disconnect()


if __name__ == "__main__":
    print("OCPP Mock Client - Test Mode")
    print("Make sure OCPP server is running on ws://localhost:9000\n")
    
    asyncio.run(test_client())
