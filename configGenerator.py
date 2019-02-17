#!/usr/bin/python3

import filecmp
import sys
import os.path
from exceptions import *


class Generate:

  def _backup(self, new_file, old_file):
    """
    Compare files and backs up the old one if it is different
    """
    try:
      if not filecmp.cmp(new_file, old_file):
        os.rename(old_file, old_file + ".bkp")
    except FileNotFoundError:
      pass
    finally:
      os.rename(new_file, old_file)

  #A more readable version explaining what the one above does in easier terms (doesn't get used)
  def _to_netmask1(self, cidr):
    """
    Takes a cidr notated ip address and returns the ip and the netmask
    """
    netmask = ""
    ip = cidr.split("/")[0]
    mask = int(cidr.split("/")[1])

    #Starts by subtracting each full byte
    while mask >= 8:
      netmask += "255."
      mask -= 8
    netmask = netmask.strip(".")

    #Then while the length is too short (inputs into this will already be sanitized)
    #Add the remaining bits
    while len(netmask.strip(".").split(".")) != 4:
      if mask > 0:
        netmask += "." + str(2**8-2**(8-mask))
        mask = 0
      else:
        netmask += ".0"

    return ip, netmask.strip(".")

  def netmask(self, cidr):
    ip = cidr.split("/")[0]
    mask = int(cidr.split("/")[1])

    #Could also do this
    #return lambda c:(c.split("/")[0],"".join([str((((~(2**(32-int(c.split("/")[1]))-1))%(2**32))&(255<<8*(3-i)))>>(8*(3-i)))+"." for i in range(4)]).rstrip("."))

    return ip, "".join([str((((~(2**(32-mask)-1))%(2**32))&(255<<8*(3-i)))>>(8*(3-i)))+"." for i in range(4)]).rstrip(".")

  def _to_cidr(self, ip, netmask):
    """
    Takes an ip and a netmask and returns a cidr notated ip address
    """
    #Returns a sum of all of the bits
    return ip + "/" + str(sum([bin(int(x)).count("1") for x in netmask.split(".")]))

  def gen_hostapd(self, interface="wlan0", essid="WiPi AP", channel=1, password=None):
    """
    Used to configure the hostapd.conf, backup the old one if it's different and replace it
    """
    with open("hostapd.conf", "w") as f:
      f.write("interface={}\n".format(interface)) #Interface to host the AP on
      f.write("driver=nl80211\n") #Required WiFi driver
      f.write("ssid={}\n".format(essid)) #The name of the device
      f.write("hw_mode=g\n") #Not sure what this is for
      f.write("channel={}\n".format(channel)) #The channel of the access point
      f.write("wmm_enabled=0\n") #Not sure what this is for
      f.write("macaddr_acl=0\n") #Not sure what this is for
      f.write("auth_algs=1\n") #Not sure what this is for
      f.write("ignore_broadcast_ssid=0\n")

      #If access point requires a password or not
      if password is not None:
        f.write("wpa=2\n") #AP encryption algorithm
        f.write("wpa_passphrase={}\n".format(password)) #The password to the AP
        f.write("wpa_key_mgmt=WPA-PSK\n") #Use preshared keys
        f.write("wpa_pairwise=TKIP\n") #Not sure what this is for
        f.write("rsn_pairwise=CCMP\n") #Not sure what this is for

    #Backup the configs
    self._backup("hostapd.conf", "/etc/hostapd/hostapd.conf")

    #Make sure the file gets loaded into hostapd daemon conf
    #Check to see if the file exists
    if os.path.isfile("/etc/default/hostapd"):
      lines = []
      with open("/etc/default/hostapd", "r") as f:
        lines = f.readlines()
      #Make sure the file isn't empty
      if lines == [""] or len(lines) < 1:
        with open("/etc/default/hostapd", "w") as f:
          f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')
          f.write('DAEMON_OPTS=""\n')
      else:
        #Check through all of the read lines
        for line in lines:
          #Put options where necessary
          if 'DAEMON_OPTS=""\n' not in lines:
            lines.append('DAEMON_OPTS=""\n')
          #Replace anything that isn't our config
          if "DAEMON_CONF=" in line and line.strip() != 'DAEMON_CONF="/etc/hostapd/hostapd.conf"':
            index = lines.index(line)
            line = 'DAEMON_CONF="/etc/hostapd/hostapd.conf"\n'
            lines.insert(index, line)
            lines.pop(index + 1)
          elif line.strip() == 'DAEMON_CONF="/etc/hostapd/hostapd.conf"':
            break
        #Write the changes
        with open("/etc/default/hostapd", "w") as f:
          for line in lines:
            f.write(line)
    #If file doesn't exist, create it
    else:
      with open("/etc/default/hostapd", "w") as f:
        f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')
        f.write('DAEMON_OPTS=""\n')

  #Configure the dnsamq.conf, backup the old one if it's different and replace it
  def gen_dnsmasq(self, interface="wlan0", domain="mydomain.net", static_ip="192.168.4.1",
              static_ip_range="255.255.255"):
    """
    Used to configure the dnsmasq.conf, backup the old one if it's different and replace it
    """
    with open("dnsmasq.conf", "w") as f:
      f.write("domain-needed\n") #Blocks incomplete requests from leaving the network
      f.write("bogus-priv\n") #Prevents private addresses from being forwarded
      f.write("no-resolv\n") #Don't read /etc/resolv.conf for DNS servers
      f.write("domain={}\n".format(domain)) #Set the local domain
      f.write("expand-hosts\n") #Allow hosts to use this domain
      f.write("local=/{}/\n".format(domain)) #Ensures the domain is private
      f.write("listen-address=127.0.0.1\n") #Make sure dnsmasq listens on the right networks
      f.write("listen-address={}\n".format(static_ip)) #Make sure dnsmasq listens on the right networks
      f.write("\n")
      f.write("interface={}\n".format(interface)) #Set the interface to route on 
      f.write("  dhcp-range={}.2,{}.254,255.255.255.0,5m\n".format(static_ip_range, static_ip_range))  #Set the ip range #Set the router IP
      f.write("  dhcp-option=3,{}\n".format(static_ip)) #Set the DHCP server IP
      f.write("  dhcp-option=6,{}\n".format(static_ip)) #Set upstream DNS server to Google
      f.write("  server=8.8.8.8\n") #Set upstream DNS server to Google
      f.write("  server=8.8.4.4\n") #Set upstream DNS server to Google
      f.write("\n")
      f.write("bind-interfaces\n") #Makes sure dnsmasq only listens on specified interfaces
      f.write("log-facility=/var/log/dnsmasq.log\n") #Set the logs file
      f.write("log-queries\n") #Logs queries
      f.write("log-dhcp\n") #Logs dhcp

    self._backup("dnsmasq.conf", "/etc/dnsmasq.conf")
