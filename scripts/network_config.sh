#!/bin/bash

# Network configuration script for Ubuntu 22.04
# Interface: eno1

# Function to display current IP
show_current_ip() {
    echo "Current IP configuration:"
    ip addr show eno1 | grep "inet "
    echo ""
}

# Function to set static IP
set_static_ip() {
    # Backup existing netplan config
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    sudo cp /etc/netplan/*.yaml /etc/netplan/*.yaml.backup_$TIMESTAMP 2>/dev/null

    # Create new netplan config
    CONFIG_FILE="/etc/netplan/99-static-ip.yaml"
    echo "network:
  version: 2
  renderer: networkd
  ethernets:
    eno1:
      addresses: [10.10.175.200/24]
      routes:
        - to: default
          via: 10.10.175.1
      nameservers:
        addresses: [8.8.8.8]" | sudo tee $CONFIG_FILE > /dev/null

    echo "New static IP configuration created at $CONFIG_FILE"
}

# Function to set DHCP
set_dhcp() {
    # Backup existing netplan config
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    sudo cp /etc/netplan/*.yaml /etc/netplan/*.yaml.backup_$TIMESTAMP 2>/dev/null

    # Create new netplan config
    CONFIG_FILE="/etc/netplan/99-dhcp.yaml"
    echo "network:
  version: 2
  renderer: networkd
  ethernets:
    eno1:
      dhcp4: true" | sudo tee $CONFIG_FILE > /dev/null

    echo "New DHCP configuration created at $CONFIG_FILE"
}

# Main script
show_current_ip

echo "Select network configuration:"
echo "1) DHCP (automatic IP)"
echo "2) Static IP (10.10.175.200)"
read -p "Enter your choice [1-2]: " choice
echo

case $choice in
    1)
        set_dhcp
        ;;
    2)
        set_static_ip
        ;;
    *)
        echo "Invalid choice. Operation cancelled."
        exit 1
        ;;
esac

echo "Applying new network configuration..."
sudo netplan apply
echo "Done. New IP configuration:"
ip addr show eno1 | grep "inet "
