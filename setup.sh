#!/bin/bash

euid=$(id -u)
if [ "$euid" -ne 0 ]; then
	echo "You must be root in order to run this program"
	exit 1
fi

# Install hostpad and dnsmasq
echo "Installing hostapd and dnsmasq"
apt-get install hostapd dnsmasq -y &> /dev/null

systemctl stop hostapd
systemctl stop dnsmasq

# Create dhcpcd.conf files
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.original
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.offline
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.online


echo -e "interface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant" | tee -a /etc/dhcpcd.conf
service dhcpcd restart
