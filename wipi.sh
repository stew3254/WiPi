#!/bin/bash

euid=$(id -u)
if [$euid -ne 0]; then
	echo "You must be root in order to run this program"
	exit 1
fi

# Install hostpad and dnsmasq
apt install hostapd dnsmasq -y

systemctl stop hostapd
systemctl stop dnsmasq

# Configure dhcpcd.conf
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
echo -e "interface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant" | tee -a /etc/dhcpcd.conf
service dhcpcd restart

# Configuring dnsmasq
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo -e "interface=wlan0\t # Use the require wireless interface - usually wlan0\n\t dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | tee -a /etc/dnsmasq.conf

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

echo -e $wap | tee -a /etc/hostapd/hostapd.conf

hostapd_conf=$(grep DAEMON_CONF= /etc/default/hostapd | cut -f 2 -d "="|)

if [ $hostapd_conf = "" ] then
	grep DAEMON_CONF= /etc/default/hostapd | sed -ie 's/""/"/etc/hostapd/hostapd.conf/"/g'
fi

systemctl start hostapd
systemctl start dnsmasq

# Add routing and masquerade
net=$(grep net.ipv4.ip_forward /etc/sysctl.conf)

if [[ $net = *"#"* ]] then
	grep net.ipve.ip_forward /etc/sysctl.conf | sed -ie 's/#//g' /etc/sysctl.conf
fi

iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"

sed -ie '/exit 0/i iptables-restore < /etc/iptables.ipv4.nat/' /etc/rc.local
