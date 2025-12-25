# Environment Setup Guide

Complete guide for setting up the CAN ↔ OCPP anomaly testing environment.

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **Python**: 3.7 or higher
- **Privileges**: sudo access for vcan setup
- **Disk Space**: ~100 MB

## Installation Steps

### 1. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install CAN utilities
sudo apt-get install -y can-utils

# Install Python and pip (if not already installed)
sudo apt-get install -y python3 python3-pip

# Verify installations
which candump  # Should show path to candump
python3 --version  # Should show Python 3.7+
```

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd EV-Charging_Station_Secure

# Install required packages
pip3 install -r requirements.txt

# Verify installations
python3 -c "import can; print('python-can:', can.__version__)"
python3 -c "import websockets; print('websockets installed')"
```

### 3. Setup Virtual CAN Interface

```bash
# Run setup script
bash scripts/setup_vcan.sh

# Verify vcan0 is up
ip link show vcan0
```

Expected output:
```
vcan0: <NOARP,UP,LOWER_UP> mtu 72 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/can
```

### 4. Test Installation

```bash
# Test CAN interface
python3 can/can_utils.py

# Test OCPP components
python3 ocpp/ocpp_messages.py

# Test IDS
python3 ids/rules.py
```

## Manual vcan0 Setup

If the script doesn't work, set up vcan0 manually:

```bash
# Load vcan kernel module
sudo modprobe vcan

# Create vcan0 interface
sudo ip link add dev vcan0 type vcan

# Bring interface up
sudo ip link set up vcan0

# Verify
ip link show vcan0
```

## Persistent vcan0 Setup

To make vcan0 persistent across reboots:

### Option 1: systemd Service

Create `/etc/systemd/system/vcan0.service`:

```ini
[Unit]
Description=Virtual CAN Interface
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/modprobe vcan
ExecStart=/sbin/ip link add dev vcan0 type vcan
ExecStart=/sbin/ip link set up vcan0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vcan0.service
sudo systemctl start vcan0.service
```

### Option 2: Network Interfaces

Add to `/etc/network/interfaces`:

```
auto vcan0
iface vcan0 inet manual
    pre-up /sbin/ip link add dev vcan0 type vcan
    up /sbin/ip link set up vcan0
```

## Verification Checklist

- [ ] `candump` command available
- [ ] Python 3.7+ installed
- [ ] `python-can` package installed
- [ ] `websockets` package installed
- [ ] vcan0 interface created and UP
- [ ] Can run `python3 can/can_utils.py` without errors
- [ ] Can run `python3 ocpp/ocpp_server.py` without errors
- [ ] Can run `python3 ids/ids_core.py` without errors

## Troubleshooting

### vcan Module Not Found

**Error**: `RTNETLINK answers: Operation not supported`

**Solution**: Install kernel modules
```bash
sudo apt-get install linux-modules-extra-$(uname -r)
sudo modprobe vcan
```

### Permission Denied

**Error**: `Operation not permitted`

**Solution**: Run with sudo or add user to appropriate group
```bash
sudo bash scripts/setup_vcan.sh
```

### Python Package Installation Fails

**Error**: `error: externally-managed-environment`

**Solution**: Use virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solution**: Kill process using the port
```bash
# Find process on port 9000
sudo lsof -i :9000

# Kill process
sudo kill -9 <PID>
```

## Next Steps

Once setup is complete, proceed to [RUNBOOK](RUNBOOK.md) to start running tests.
