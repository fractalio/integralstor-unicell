#!/bin/bash

# Remove all available network connections
nmcli -t -f name con show | xargs -n1 -r -I '{}' nmcli con del '{}' &>> /tmp/out_first_boot

# Create a new connection on eth0 with IP 172.16.16.16
# This works only if interface eth0 is present
nmcli con add type ethernet con-name eth0 ifname eth0 &>> /tmp/out_first_boot
nmcli con down eth0 &>> /tmp/out_first_boot
nmcli con mod eth0 ipv4.method manual connection.autoconnect yes ipv4.never-default no ipv4.addresses "172.16.16.16/24" ipv4.gateway 172.16.16.1 ipv4.routes "172.16.16.0 172.16.16.1" &>> /tmp/out_first_boot
nmcli con up eth0 &>> /tmp/out_first_boot

# Prevent first-boot systemd service from executing on boot
systemctl disable first-boot &>> /tmp/out_first_boot
