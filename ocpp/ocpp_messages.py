"""
OCPP Message Templates and Builders

Provides templates and builder functions for common OCPP messages
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List


class OCPPMessageBuilder:
    """Builds OCPP 1.6 JSON messages"""
    
    @staticmethod
    def boot_notification(
        charge_point_vendor: str = "TestVendor",
        charge_point_model: str = "TestModel",
        firmware_version: str = "v1.0.0",
        charge_point_serial: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build BootNotification message
        
        Args:
            charge_point_vendor: Vendor name
            charge_point_model: Model name
            firmware_version: Firmware version
            charge_point_serial: Serial number (optional)
            **kwargs: Additional fields
            
        Returns:
            BootNotification message dict
        """
        message = {
            "chargePointVendor": charge_point_vendor,
            "chargePointModel": charge_point_model,
            "firmwareVersion": firmware_version,
        }
        
        if charge_point_serial:
            message["chargePointSerialNumber"] = charge_point_serial
        
        message.update(kwargs)
        return message
    
    @staticmethod
    def remote_start_transaction(
        connector_id: int = 1,
        id_tag: str = "TEST_TAG_001",
        charging_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Build RemoteStartTransaction message
        
        Args:
            connector_id: Connector ID
            id_tag: Authorization ID tag
            charging_profile: Optional charging profile
            
        Returns:
            RemoteStartTransaction message dict
        """
        message = {
            "connectorId": connector_id,
            "idTag": id_tag
        }
        
        if charging_profile:
            message["chargingProfile"] = charging_profile
        
        return message
    
    @staticmethod
    def remote_stop_transaction(transaction_id: int) -> Dict[str, Any]:
        """
        Build RemoteStopTransaction message
        
        Args:
            transaction_id: Transaction ID to stop
            
        Returns:
            RemoteStopTransaction message dict
        """
        return {"transactionId": transaction_id}
    
    @staticmethod
    def meter_values(
        connector_id: int = 1,
        transaction_id: Optional[int] = None,
        energy_wh: float = 0.0,
        power_w: float = 0.0,
        current_a: float = 0.0,
        voltage_v: float = 230.0,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build MeterValues message
        
        Args:
            connector_id: Connector ID
            transaction_id: Transaction ID (optional)
            energy_wh: Energy in Wh
            power_w: Power in W
            current_a: Current in A
            voltage_v: Voltage in V
            timestamp: ISO 8601 timestamp (optional, uses current time if None)
            
        Returns:
            MeterValues message dict
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        sampled_values = []
        
        if energy_wh > 0:
            sampled_values.append({
                "value": str(energy_wh),
                "measurand": "Energy.Active.Import.Register",
                "unit": "Wh"
            })
        
        if power_w > 0:
            sampled_values.append({
                "value": str(power_w),
                "measurand": "Power.Active.Import",
                "unit": "W"
            })
        
        if current_a > 0:
            sampled_values.append({
                "value": str(current_a),
                "measurand": "Current.Import",
                "unit": "A"
            })
        
        if voltage_v > 0:
            sampled_values.append({
                "value": str(voltage_v),
                "measurand": "Voltage",
                "unit": "V"
            })
        
        message = {
            "connectorId": connector_id,
            "meterValue": [{
                "timestamp": timestamp,
                "sampledValue": sampled_values
            }]
        }
        
        if transaction_id is not None:
            message["transactionId"] = transaction_id
        
        return message
    
    @staticmethod
    def start_transaction(
        connector_id: int = 1,
        id_tag: str = "TEST_TAG_001",
        meter_start: int = 0,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build StartTransaction message
        
        Args:
            connector_id: Connector ID
            id_tag: Authorization ID tag
            meter_start: Meter value at start
            timestamp: ISO 8601 timestamp
            
        Returns:
            StartTransaction message dict
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        return {
            "connectorId": connector_id,
            "idTag": id_tag,
            "meterStart": meter_start,
            "timestamp": timestamp
        }
    
    @staticmethod
    def stop_transaction(
        transaction_id: int,
        meter_stop: int,
        timestamp: Optional[str] = None,
        reason: str = "Local"
    ) -> Dict[str, Any]:
        """
        Build StopTransaction message
        
        Args:
            transaction_id: Transaction ID
            meter_stop: Meter value at stop
            timestamp: ISO 8601 timestamp
            reason: Stop reason
            
        Returns:
            StopTransaction message dict
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        return {
            "transactionId": transaction_id,
            "meterStop": meter_stop,
            "timestamp": timestamp,
            "reason": reason
        }
    
    @staticmethod
    def heartbeat() -> Dict[str, Any]:
        """
        Build Heartbeat message
        
        Returns:
            Empty dict (Heartbeat has no payload)
        """
        return {}
    
    @staticmethod
    def status_notification(
        connector_id: int = 0,
        error_code: str = "NoError",
        status: str = "Available",
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build StatusNotification message
        
        Args:
            connector_id: Connector ID (0 for charge point)
            error_code: Error code
            status: Connector status
            timestamp: ISO 8601 timestamp
            
        Returns:
            StatusNotification message dict
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        return {
            "connectorId": connector_id,
            "errorCode": error_code,
            "status": status,
            "timestamp": timestamp
        }


def validate_boot_notification(message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate BootNotification message
    
    Args:
        message: Message to validate
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ["chargePointVendor", "chargePointModel"]
    
    for field in required_fields:
        if field not in message:
            return False, f"Missing required field: {field}"
    
    return True, None


def validate_firmware_version(firmware: str, allowed_list: List[str]) -> bool:
    """
    Validate firmware version against whitelist
    
    Args:
        firmware: Firmware version string
        allowed_list: List of allowed versions
        
    Returns:
        True if valid, False otherwise
    """
    return firmware in allowed_list


def validate_meter_values(message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate MeterValues message
    
    Args:
        message: Message to validate
        
    Returns:
        (is_valid, error_message)
    """
    if "connectorId" not in message:
        return False, "Missing connectorId"
    
    if "meterValue" not in message:
        return False, "Missing meterValue"
    
    # Check for abnormal values
    for meter_value in message.get("meterValue", []):
        for sampled_value in meter_value.get("sampledValue", []):
            value = float(sampled_value.get("value", 0))
            measurand = sampled_value.get("measurand", "")
            
            # Check for out-of-range values
            if "Current" in measurand and value > 80:
                return False, f"Current value out of range: {value}A (max: 80A)"
            
            if "Power" in measurand and value > 22000:
                return False, f"Power value out of range: {value}W (max: 22kW)"
            
            if "Voltage" in measurand and (value < 200 or value > 250):
                return False, f"Voltage value out of range: {value}V (valid: 200-250V)"
    
    return True, None


if __name__ == "__main__":
    # Test message builders
    builder = OCPPMessageBuilder()
    
    print("BootNotification:")
    print(json.dumps(builder.boot_notification(), indent=2))
    
    print("\nRemoteStartTransaction:")
    print(json.dumps(builder.remote_start_transaction(), indent=2))
    
    print("\nMeterValues:")
    print(json.dumps(builder.meter_values(energy_wh=1500, power_w=7400, current_a=32), indent=2))
