#!/bin/bash

# Setup vcan0 virtual CAN interface

echo "Setting up vcan0 virtual CAN interface..."

# Load vcan kernel module
sudo modprobe vcan

# Create vcan0 interface
sudo ip link add dev vcan0 type vcan

# Bring up the interface
sudo ip link set up vcan0

# Verify
if ip link show vcan0 > /dev/null 2>&1; then
    echo "✅ vcan0 interface created successfully"
    ip link show vcan0
else
    echo "❌ Failed to create vcan0 interface"
    exit 1
fi
