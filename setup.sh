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
echo "Creating dhcpcd configuration files"
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.original
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.offline

echo -e "interface wlan0\n
\tstatic ip_address=192.168.4.1/24\n
\tnohook wpa_supplicant" | tee -a /etc/dhcpcd.conf.offline
cp /etc/dhcpdc.conf.offline /etc/dhcpcd.conf.online
sed -ie '/interface/i denyinterfaces wlan0' /etc/dhcpcd.conf.online
sed -ie '/denyinterfaces wlan0/a denyinterfaces eth0' /etc/dhcpcd.conf.online

# Create dnsmasq.conf files
echo "Creating dnsmasq configuration files"
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.original
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.wap
echo -e "interface=wlan0\t # Use the require wireless interface - usually wlan0\n
\t dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | tee -a /etc/dnsmasq.conf.offline

# Create create hostapd.conf files
echo "Creating hostapd configuration files"
wap="interface=wlan0\n
#bridge=br0
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

echo -e $wap | tee -a /etc/hostapd/hostapd.conf.offline
cp /etc/hostapd/hostapd.conf.offline /etc/hostapd/hostapd.conf.online
sed -ie 's/#bridge/bridge/g' /etc/hostapd/hostapd.conf.online
sed -ie 's/driver/#driver/g' /etc/hostapd/hostapd.conf.online

hostapd_conf=$(grep DAEMON_CONF= /etc/default/hostapd | cut -f 2 -d "="|)

if [ $hostapd_conf = "" ] then
	grep DAEMON_CONF= /etc/default/hostapd | sed -ie 's/""/"/etc/hostapd/hostapd.conf/"/g'
fi

# Add Routing and Masquerade
echo "Adding Routing and Masquerade"
cp /etc/sysctl.conf /etc/sysctl.conf.original
cp /etc/sysctl.conf /etc/sysctl.conf.wap

net=$(grep net.ipv4.ip_forward /etc/sysctl.conf)

if [[ $net = *"#"* ]] then
	grep net.ipve.ip_forward /etc/sysctl.conf | sed -ie 's/#//g' /etc/sysctl.conf.wap
fi

iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"
cp /etc/rc.local /etc/rc.local.original
cp /etc/rc.local /etc/rc.local.wap

# Creating interface configuration files
cp /etc/network/interfaces /etc/network/interfaces.original
cp /etc/network/interfaces /etc/network/interfaces.online

echo -e "\n# Bridge setup\n
auto br0\n
iface br0 inet manual\n
bridge_ports eth0 wlan0\n" | tee -a /etc/network/interfaces.online
