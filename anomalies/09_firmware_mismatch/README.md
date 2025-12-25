# Anomaly 9: Firmware Mismatch

## Description
Detects when a charge point attempts to connect with an unauthorized firmware version via OCPP BootNotification.

## Security Impact
- **Attack Type**: Unauthorized Device / Compromised Firmware
- **Risk Level**: CRITICAL
- **Impact**: Unauthorized or compromised devices can access the network

## How It Works
1. Attacker sends BootNotification with firmware version "evil-v9"
2. IDS maintains whitelist of allowed firmware versions
3. Alert triggered for unauthorized versions

## Running the Test
```bash
python anomalies/09_firmware_mismatch/test_scenario.py
```

## Expected Output
```
⚠️  ANOMALY 9: Firmware mismatch - 'evil-v9' not in whitelist ['v1.5-stable', 'v1.6-release', 'v2.0.1-prod']
```
