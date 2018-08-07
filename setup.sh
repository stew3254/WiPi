#!/bin/bash

euid=$(id -u)
if [ "$euid" -ne 0 ]; then
	echo "You must be root in order to run this program"
	exit 1
fi

# Install hostpad and dnsmasq
echo "Installing hostapd and dnsmasq"
apt-get install hostapd dnsmasq -y &> /dev/null
echo "Stopping services"
systemctl stop hostapd
systemctl stop dnsmasq


