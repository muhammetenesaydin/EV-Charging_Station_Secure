"""
OCPP WebSocket Server

Mock OCPP Central System server for testing
"""

import asyncio
import websockets
import json
from datetime import datetime
from typing import Set, Dict, Optional, Callable
from ocpp.ocpp_messages import OCPPMessageBuilder, validate_boot_notification, validate_firmware_version


class OCPPServer:
    """Mock OCPP 1.6 Central System Server"""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        """
        Initialize OCPP server
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.message_handlers: Dict[str, Callable] = {}
        self.allowed_firmware: list = ["v1.5-stable", "v1.6-release", "v2.0.1-prod"]
        self.connection_count = 0
        self.connection_times = []
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers["BootNotification"] = self._handle_boot_notification
        self.message_handlers["RemoteStartTransaction"] = self._handle_remote_start
        self.message_handlers["RemoteStopTransaction"] = self._handle_remote_stop
        self.message_handlers["MeterValues"] = self._handle_meter_values
        self.message_handlers["Heartbeat"] = self._handle_heartbeat
        self.message_handlers["StatusNotification"] = self._handle_status_notification
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register custom message handler
        
        Args:
            message_type: OCPP message type
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
    
    async def _handle_boot_notification(self, websocket, message: Dict) -> Dict:
        """Handle BootNotification message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Validate message
        is_valid, error = validate_boot_notification(message)
        if not is_valid:
            print(f"[OCPP] [{timestamp}] Invalid BootNotification: {error}")
            return {"status": "Rejected"}
        
        # Check firmware version
        firmware = message.get("firmwareVersion", "unknown")
        if not validate_firmware_version(firmware, self.allowed_firmware):
            print(f"[OCPP] [{timestamp}] ⚠️  FIRMWARE MISMATCH: '{firmware}' not in whitelist")
            print(f"[OCPP] [{timestamp}]    Allowed: {self.allowed_firmware}")
            return {"status": "Rejected", "interval": 0}
        
        print(f"[OCPP] [{timestamp}] BootNotification accepted - Firmware: {firmware}")
        return {
            "status": "Accepted",
            "currentTime": datetime.utcnow().isoformat() + "Z",
            "interval": 300
        }
    
    async def _handle_remote_start(self, websocket, message: Dict) -> Dict:
        """Handle RemoteStartTransaction message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        connector_id = message.get("connectorId", 1)
        id_tag = message.get("idTag", "unknown")
        
        print(f"[OCPP] [{timestamp}] RemoteStartTransaction - Connector: {connector_id}, Tag: {id_tag}")
        
        return {"status": "Accepted"}
    
    async def _handle_remote_stop(self, websocket, message: Dict) -> Dict:
        """Handle RemoteStopTransaction message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        transaction_id = message.get("transactionId", 0)
        
        print(f"[OCPP] [{timestamp}] RemoteStopTransaction - Transaction: {transaction_id}")
        
        return {"status": "Accepted"}
    
    async def _handle_meter_values(self, websocket, message: Dict) -> Dict:
        """Handle MeterValues message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        connector_id = message.get("connectorId", 1)
        
        # Extract values
        values_str = []
        for meter_value in message.get("meterValue", []):
            for sampled_value in meter_value.get("sampledValue", []):
                measurand = sampled_value.get("measurand", "Unknown")
                value = sampled_value.get("value", "0")
                unit = sampled_value.get("unit", "")
                values_str.append(f"{measurand}: {value}{unit}")
        
        print(f"[OCPP] [{timestamp}] MeterValues - Connector: {connector_id}, Values: {', '.join(values_str)}")
        
        return {}
    
    async def _handle_heartbeat(self, websocket, message: Dict) -> Dict:
        """Handle Heartbeat message"""
        return {"currentTime": datetime.utcnow().isoformat() + "Z"}
    
    async def _handle_status_notification(self, websocket, message: Dict) -> Dict:
        """Handle StatusNotification message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        connector_id = message.get("connectorId", 0)
        status = message.get("status", "Unknown")
        error_code = message.get("errorCode", "NoError")
        
        print(f"[OCPP] [{timestamp}] StatusNotification - Connector: {connector_id}, Status: {status}, Error: {error_code}")
        
        return {}
    
    async def _handle_client(self, websocket, path):
        """Handle client connection"""
        client_addr = websocket.remote_address
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.clients.add(websocket)
        self.connection_count += 1
        self.connection_times.append(datetime.now())
        
        print(f"[OCPP] [{timestamp}] Client connected: {client_addr[0]}:{client_addr[1]} (Total: {len(self.clients)})")
        
        try:
            async for message_str in websocket:
                try:
                    # Parse message
                    message_data = json.loads(message_str)
                    
                    # Determine message type
                    message_type = None
                    message_payload = {}
                    
                    # Simple message type detection
                    if "chargePointVendor" in message_data:
                        message_type = "BootNotification"
                        message_payload = message_data
                    elif "connectorId" in message_data and "idTag" in message_data:
                        message_type = "RemoteStartTransaction"
                        message_payload = message_data
                    elif "transactionId" in message_data and "meterStop" not in message_data:
                        message_type = "RemoteStopTransaction"
                        message_payload = message_data
                    elif "meterValue" in message_data:
                        message_type = "MeterValues"
                        message_payload = message_data
                    elif len(message_data) == 0:
                        message_type = "Heartbeat"
                        message_payload = {}
                    elif "status" in message_data and "errorCode" in message_data:
                        message_type = "StatusNotification"
                        message_payload = message_data
                    
                    # Handle message
                    if message_type and message_type in self.message_handlers:
                        response = await self.message_handlers[message_type](websocket, message_payload)
                        await websocket.send(json.dumps(response))
                    else:
                        print(f"[OCPP] [{timestamp}] Unknown message type: {message_str[:100]}")
                        await websocket.send(json.dumps({"error": "Unknown message type"}))
                
                except json.JSONDecodeError:
                    print(f"[OCPP] [{timestamp}] Invalid JSON: {message_str[:100]}")
                except Exception as e:
                    print(f"[OCPP] [{timestamp}] Error handling message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"[OCPP] [{timestamp}] Client disconnected: {client_addr[0]}:{client_addr[1]} (Total: {len(self.clients)})")
    
    async def start(self):
        """Start the OCPP server"""
        print(f"[OCPP] Starting OCPP server on {self.host}:{self.port}")
        print(f"[OCPP] Allowed firmware versions: {self.allowed_firmware}")
        
        async with websockets.serve(self._handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n[OCPP] Server stopped by user")


if __name__ == "__main__":
    server = OCPPServer(host="localhost", port=9000)
    print("OCPP Mock Server")
    print("Press Ctrl+C to stop\n")
    server.run()
