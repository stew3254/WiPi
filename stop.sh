#!/bin/bash

#Source needed functions
source derp.sh
source kill_services.sh
source check_dependencies.sh

#Check to see if the interface exists
checkInterface

#Check to make sure the dependencies are installed
checkDepends

#Check to see if the status file exists
if [ -e /etc/wipi.status ]; then
  #Check if the access point is running via status file
  if [ "`cat /etc/wipi.status`" = "stopped" ] && [ "$WIPI_MODE" = "stop" ]; then
    echo "WiPi is not running. If this is a mistake, please remove /etc/wipi.status"
    exit 1
  #Error if in the wrong format
  elif [ "`cat /etc/wipi.status`" != "running" ] && [ "`cat /etc/wipi.status`" != "stopped" ]; then
    echo "Error reading /etc/wipi.status. Please remove it"
    exit 1
  else
    #Proceed
    echo "stopped" > /etc/wipi.status
  fi
else
  #Proceed
  echo "stopped" > /etc/wipi.status
fi

verbose "Removing static ip"
#Remove static IP
for ip in "`ip a show $WIPI_INTERFACE | grep inet | grep [.] | sed 's/\ \ */\ /g' | cut -d ' ' -f 3`"; do
  ip a del $ip dev $WIPI_INTERFACE
done

local output=`killServices hostapd dnsmasq`
#Kill services
if [ "$output" = "1" ] && [ "$WIPI_MODE" = "stop" ]; then
  echo "Couldn't stop access point (it wasn't running)"
  exit 1
fi

#Restore iptables rules
verbose "Restoring old iptables rules"
iptables-restore < /etc/iptables.ipv4.nat

#Print access point stopped if the mode was told to stop
#This is here so if you restart it doesn't print the access point is stopped
if [ "$WIPI_MODE" = "stop" ]; then
  echo "Access point stopped"
fi
