# RUNBOOK: CAN ↔ OCPP Anomaly Testing Framework

Complete step-by-step guide for setting up and running all anomaly tests.

## Prerequisites

### System Requirements
- Linux (Ubuntu 20.04+ or similar)
- Python 3.7+
- sudo access (for vcan setup)

### Required Packages
```bash
# System packages
sudo apt-get update
sudo apt-get install -y can-utils python3-pip

# Python packages
pip install -r requirements.txt
```

---

## Quick Start

### 1. Setup Virtual CAN Interface
```bash
bash scripts/setup_vcan.sh
```

Verify vcan0 is running:
```bash
ip link show vcan0
```

### 2. Test Basic Components

#### Test CAN Interface
```bash
python can/can_utils.py
```

#### Test OCPP Server
```bash
# Terminal 1: Start server
python ocpp/ocpp_server.py

# Terminal 2: Test client
python ocpp/ocpp_client.py
```

#### Test IDS
```bash
python ids/ids_core.py
```

---

## Running Anomaly Tests

Each anomaly can be tested independently. The general pattern is:

1. **Terminal 1**: Start IDS
2. **Terminal 2**: Run anomaly test scenario
3. **Observe**: IDS detects and logs the anomaly

### Anomaly 1: Frequency Spike

**Description**: Floods CAN bus with high-frequency messages

```bash
# Terminal 1
python ids/ids_core.py

# Terminal 2
python anomalies/01_frequency_spike/test_scenario.py
```

**Expected Alert**:
```
⚠️  ANOMALY 1: Frequency spike detected on CAN ID 0x9FF - 100.0 msg/s
```

### Anomaly 2: OCPP → CAN Delay

**Description**: Delays CAN response after OCPP command

```bash
python anomalies/02_ocpp_can_delay/test_scenario.py
```

**Expected Alert**:
```
⚠️  ANOMALY 2: Abnormal delay detected - OCPP → CAN 0x200: 10.0s
```

### Anomaly 3: Out-of-Range Payload

**Description**: Sends physically impossible values

```bash
# Terminal 1
python ids/ids_core.py

# Terminal 2
python anomalies/03_out_of_range_payload/test_scenario.py
```

**Expected Alert**:
```
⚠️  ANOMALY 3: Out-of-range value detected - current: 255
```

### Anomaly 9: Firmware Mismatch

**Description**: Unauthorized firmware version

```bash
python anomalies/09_firmware_mismatch/test_scenario.py
```

**Expected Alert**:
```
⚠️  ANOMALY 9: Firmware mismatch - 'evil-v9' not in whitelist
```

---

## Viewing Logs

### IDS Alert Log
```bash
cat logs/ids_alerts.log
```

### IDS Statistics
```bash
cat logs/ids_stats.json
```

### CAN Traffic Log
```bash
cat logs/can_traffic.log
```

---

## Advanced Usage

### Running Multiple Anomalies

You can run multiple anomaly tests sequentially:

```bash
# Start IDS
python ids/ids_core.py &
IDS_PID=$!

# Run tests
python anomalies/01_frequency_spike/test_scenario.py
sleep 2
python anomalies/03_out_of_range_payload/test_scenario.py
sleep 2
python anomalies/09_firmware_mismatch/test_scenario.py

# Stop IDS
kill $IDS_PID
```

### Customizing Detection Thresholds

Edit detector parameters in `ids/ids_core.py`:

```python
self.detectors = {
    "frequency_spike": FrequencySpikeDetector(threshold_hz=30.0),  # Changed from 20.0
    # ... other detectors
}
```

### Monitoring CAN Traffic

Use `candump` to monitor all CAN traffic:

```bash
candump vcan0
```

Use `cansend` to manually send CAN messages:

```bash
cansend vcan0 123#DEADBEEF
```

---

## Troubleshooting

### vcan0 Not Found

**Problem**: `OSError: [Errno 19] No such device`

**Solution**:
```bash
bash scripts/setup_vcan.sh
```

### Permission Denied

**Problem**: Cannot create vcan0 interface

**Solution**: Run with sudo or add user to appropriate group
```bash
sudo bash scripts/setup_vcan.sh
```

### Port Already in Use

**Problem**: OCPP server port 9000 already in use

**Solution**: Kill existing process or change port
```bash
# Find process
lsof -i :9000

# Kill process
kill -9 <PID>

# Or change port in ocpp/ocpp_server.py
```

### Python Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'websockets'`

**Solution**:
```bash
pip install -r requirements.txt
```

---

## Understanding the Results

### IDS Alert Format

```
[TIMESTAMP] [LEVEL] [ANOMALY_TYPE] Message | Details: {...}
```

Example:
```
[2025-12-15 17:30:45.123] [WARNING] [Frequency Spike] ⚠️  ANOMALY 1: Frequency spike detected on CAN ID 0x9FF - 100.0 msg/s (threshold: 20.0 msg/s)
```

### Security Response

When critical anomalies are detected, IDS triggers security response:

```
🚨 SECURITY RESPONSE TRIGGERED 🚨
Anomaly Type: Frequency Spike
Details: CAN ID 0x9FF
Response #1

[SECURITY] Safe mode command sent to CAN bus (ID: 0x001)
```

---

## Next Steps

1. **Explore Code**: Review the implementation in `can/`, `ocpp/`, and `ids/` directories
2. **Customize**: Modify detection thresholds and add new rules
3. **Extend**: Create additional anomaly scenarios
4. **Integrate**: Connect to real OCPP servers or CAN hardware (with appropriate adapters)

---

## Additional Resources

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Anomaly Details**: See `docs/ANOMALY_DETAILS.md`
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **CAN Documentation**: `can/README.md`
- **OCPP Documentation**: `ocpp/README.md`
- **IDS Documentation**: `ids/README.md`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review individual anomaly README files
3. Check log files in `logs/` directory
4. Review the implementation plan: `implementation_plan.md`
