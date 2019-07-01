#!/bin/bash

#Source needed functions
source /etc/wipi/env_vars.sh
source checks.sh
source killServices.sh
source startServices.sh
source checkDependencies.sh

#Check to see if the interface exists
echo $WIPI_interface
checkInterface $WIPI_INTERFACE

#Check to make sure the dependencies are installed
checkDepends

#Check to see if the status file exists
if [ -e /etc/wipi/wipi.status ]; then
  #Check if the access point is running via status file
  if [ "`cat /etc/wipi/wipi.status`" = "running" ]; then
    echo "WiPi is already running. If this is a mistake, please remove /etc/wipi/wipi.status"
    exit 1
  #Error if in the wrong format
  elif [ "`cat /etc/wipi/wipi.status`" != "stopped" ]; then
    echo "Error reading /etc/wipi/wipi.status. Please remove it"
    exit 1
  else
    #Proceed
    echo "running" > /etc/wipi/wipi.status
  fi
else
  #Proceed
  echo "running" > /etc/wipi/wipi.status
fi

#Set up iptables rules
verbose "Saving existing iptables rules to /etc/iptables.ipv4.nat"
sh -c "iptables-save" > /etc/iptables.ipv4.nat

verbose "Creating new routing rules"
iptables -F
iptables -t nat -A  POSTROUTING -o $WIPI_TRAFFIC_INTERFACE -j MASQUERADE
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p tcp --dport 443 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p tcp --dport 80 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p udp --dport 67:68 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p udp --dport 53 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p tcp --dport 53 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -p tcp --dport 22 -j ACCEPT
#iptables -i $WIPI_INTERFACE -A INPUT -j DROP

#Enable ip forwarding
if [ "`cat /proc/sys/net/ipv4/ip_forward`" -eq 0 ]; then
  verbose "Enabling ip forwarding"
  echo 1 > /proc/sys/net/ipv4/ip_forward
fi

#Killing conflicting processes
if [ -n "`pgrep NetworkManager`" ]; then
  verbose "Killing Network Manager"
  pkill NetworkManager
fi

if [ -n "`pgrep wpa_supplicant`" ]; then
  verbose "Killing wpa supplicant"
  pkill wpa_supplicant
fi

#Configure hostapd
#hostapdConfigure

#Bring the interface up
verbose "Bringing the interface up"
ip l set $WIPI_INTERFACE up

#Add an ip address
if [ -z "`ip a show $WIPI_INTERFACE | grep $WIPI_NAT`" ]; then
  verbose "Adding static ip $WIPI_STATIC_IP to interface $WIPI_INTERFACE"
  ip a add $WIPI_NAT dev $WIPI_INTERFACE
fi

#sleep 1

#Remove old leases
if [ -e /var/lib/misc/dnsmasq.leases ];then
  rm /var/lib/misc/dnsmasq.leases 
fi

#Try to start services
if [ "`startServices hostapd dnsmasq`" = "1" ]; then
  echo "Failed to start the access point (it's most likely already running)"
  ip a del $WIPI_NAT dev $WIPI_INTERFACE
  echo "stopped" > /etc/wipi/wipi.status
else
  #Start the access point
  if [ "$WIPI_MODE" = "start" ]; then
    echo "Started access point $WIPI_ESSID"
  fi
fi
