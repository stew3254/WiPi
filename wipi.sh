#!/bin/bash

echo 

# Install hostpad and dnsmasq
sudo apt install hostapd dnsmasq -y

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configure dhcpcd.conf
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
echo -e "interface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant" | sudo tee -a /etc/dhcpcd.conf
sudo service dhcpcd restart

# Configuring dnsmasq
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo -e "interface=wlan0\t # Use the require wireless interface - usually wlan0\n\t dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | sudo tee -a /etc/dnsmasq.conf

# Configuring hostapd
wap="interface=wlan0\n
driver=nl80211\n
ssid=NameOfNetwork\n
hw_mode=g\n
channel=7\n
wmm_enabled=0\n
macaddr_acl=0\n
auth_algs=1\n
ignore_broadcast_ssid=0\n
wpa=2\n
wpa_passphrase=AardvarkBadgerHedgehog\n
wpa_key_mgmt=WPA-PSK\n
wpa_pairwise=TKIP\n
rsn_pairwise=CCMP"

echo -e $wap | sudo tee -a /etc/hostapd/hostapd.conf

hostapd_conf=$(grep DAEMON_CONF= /etc/default/hostapd | cut -f 2 -d "="|)

if [ $hostapd_conf = "" ] then
	grep DAEMON_CONF= /etc/default/hostapd | sudo sed -ie 's/""/"/etc/hostapd/hostapd.conf/"/g'
fi

sudo systemctl start hostapd
sudo systemctl start dnsmasq

# Add routing and masquerade
net=$(grep net.ipv4.ip_forward /etc/sysctl.conf)

if [[ $net = *"#"* ]] then
	grep net.ipve.ip_forward /etc/sysctl.conf | sed -ie 's/#//g' /etc/sysctl.conf
fi

sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

sudo sed -ie '/exit 0/i iptables-restore < /etc/iptables.ipv4.nat/' /etc/rc.local
