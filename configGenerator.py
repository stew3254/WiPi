#!/usr/bin/python3

from configParser import ConfigParser
import filecmp
import sys
import os
from exceptions import *


class Generate:
  """
  Used to generate the various config files
  """
  def __init__(self):
    self.wipi()

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

  def _to_netmask(self, cidr):
    """
    Takes a cidr notated ip address and returns the ip and the netmask
    """
    pair = cidr.split("/")
    ip = pair[0]
    mask = int(pair[1])

    #This code is a bunch of bit shifting in order to generate a netmask from CIDR notation.
    #It first starts with finding the integer of 2**(32-mask)-1. This is used to find how
    #many bits are left open in the range. Then, you subract one to get it in even byte sizes.
    #It then nots all of the bits in that integer so that it will flop the bits from ones
    #to zeros. This allows it to be in proper for like 255.255.255.0, not 0.0.0.255
    #Next, it gets the remainder of it mod 2**32 so that it stays in the appropriate range.
    #After that, it used bit shifting to grab each byte, one at a time, in the number.
    #It does this by using a bitwise and with 255, which is a byte containing all ones.
    #This all occurs in a for loop and grabs the bytes in order from most significant, to least.
    #It uses this byte to and with the other bytes in the string to produce a copy of them
    #which it stores in a list that gets joined together in a string using periods.
    #Then it strips the last period on the right and returns the netmask.

    return ip, "".join([str((((~(2**(32-mask)-1))%(2**32))&(255<<8*(3-i)))>>(8*(3-i)))+"." for i in range(4)]).rstrip(".")

  def _to_cidr(self, ip, netmask):
    """
    Takes an ip and a netmask and returns a cidr notated ip address
    """
    #Returns a sum of all of the bits
    return ip + "/" + str(sum([bin(int(x)).count("1") for x in netmask.split(".")]))

  def _dhcp_range(self, ip, netmask):
    """
    Used to create a dhcp range out of an ip and a netmask
    """
    #start = "".join([ip.split(".")[i]+"." if i != 3 else "2" for i in range(4)])
    start = []
    end = []
    
    c = 1
    #Iterate over each byte in the ip and netmask
    for s_byte, n_byte in zip(ip.split("."), netmask.split(".")):
      if c != 4:
        #And the bytes to know where to properly start the range
        start.append(str(int(s_byte) & int(n_byte)%2**8) + ".")
        if start[c-1] < s_byte:
          raise MalformedDHCP("Gateway shows up in dhcp range")
        #Nor the bytes to know where to properly end the range
        end.append(str((int(s_byte) | ~(int(n_byte))%2**8)) + ".")
      else:
        #Always have the last byte 2, because the id must be a 1
        start.append("2")
        end.append(str((int(s_byte) | ~(int(n_byte))%2**8) - 1))
        print(n_byte)
      c += 1

    return "".join(start), "".join(end)

  def hostapd(self, interface="wlan0", essid="WiPi AP", channel=1, password=None):
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
  def dnsmasq(self, interface="wlan0", domain="mydomain.net", cidr = "192.168.4.1/24"):
    """
    Used to configure the dnsmasq.conf, backup the old one if it's different and replace it
    """
    ip, netmask = self._to_netmask(cidr)
    start_ip, end_ip = self._dhcp_range(ip, netmask)
    with open("dnsmasq.conf", "w") as f:
      f.write("domain-needed\n") #Blocks incomplete requests from leaving the network
      f.write("bogus-priv\n") #Prevents private addresses from being forwarded
      f.write("no-resolv\n") #Don't read /etc/resolv.conf for DNS servers
      f.write("domain={}\n".format(domain)) #Set the local domain
      f.write("expand-hosts\n") #Allow hosts to use this domain
      f.write("local=/{}/\n".format(domain)) #Ensures the domain is private
      f.write("listen-address=127.0.0.1\n") #Make sure dnsmasq listens on the right networks
      f.write("listen-address={}\n".format(ip)) #Make sure dnsmasq listens on the right networks
      f.write("\n")
      f.write("interface={}\n".format(interface)) #Set the interface to route on 
      f.write("  dhcp-range={},{},{},5m\n".format(start_ip, end_ip, netmask))  #Set the ip range #Set the router IP
      f.write("  dhcp-option=3,{}\n".format(ip)) #Set the DHCP server IP
      f.write("  dhcp-option=6,{}\n".format(ip)) #Set upstream DNS server to Google
      f.write("  server=8.8.8.8\n") #Set upstream DNS server to Google
      f.write("  server=8.8.4.4\n") #Set upstream DNS server to Google
      f.write("\n")
      f.write("bind-interfaces\n") #Makes sure dnsmasq only listens on specified interfaces
      f.write("log-facility=/var/log/dnsmasq.log\n") #Set the logs file
      f.write("log-queries\n") #Logs queries
      f.write("log-dhcp\n") #Logs dhcp

    self._backup("dnsmasq.conf", "/etc/dnsmasq.conf")

  def wipi(self):
    if not os.path.isfile("/etc/wipi/wipi.conf") and os.path.exits("/etc/wipi/wipi.conf"):
      os.rename("/etc/wipi/wipi.conf", "/etc/wipi/wipi.conf.bad")
    if not os.path.exists("/etc/wipi/wipi.conf"):
      with open("/etc/wipi/wipi.conf", "w") as f:
        f.write("#This is the default config file. Any values stored here will be used as the defaults for wipi\n")
        f.write("#Hashtags are used for inline comments\n")
        f.write("#Values come in the following format:\n")
        f.write("#   key = value\n")
        f.write("# (Whitespace around the space gets ignored. Phrases also DO NOT use quotes)\n\n")
        f.write("#This number must be between 1 and 11\n")
        f.write("channel = 1\n")
        f.write("#Do not use quotes around the name if it is multiple words\n")
        f.write("#If don't use a '#' or '=' in your name\n")
        f.write("essid = WiPi AP\n")
        f.write("#Domain can be any thing you choose\n")
        f.write("domain = mydomain.local\n")
        f.write("#This interface must actually exist\n")
        f.write("interface = eth0\n")
        f.write("#Please include a correct IPv4 address with a proper CIDR subnet mask\n")
        f.write("nat = 192.168.4.1/24\n")
        f.write("#Comment password out if you do not want a password on your access point (Open)\n")
        f.write("#password = password\n")

  def set_env_vars(self, mode, interface, passed_vars={}):
    parser = ConfigParser()
    env_vars = parser.parse()
    env_vars.update({"static_ip": env_vars["nat"].split("/")[0]})
    if "password" not in env_vars.keys():
      env_vars.update({"password": "None"})
    for var in passed_vars.keys():
      if var in env_vars.keys():
        env_vars[var] = passed_vars[var]
    print(env_vars)

    with open("/etc/wipi/env_vars.sh", "w") as f:
      try:
        f.write("WIPI_CHANNEL={}\n".format(env_vars["channel"]))
        f.write("WIPI_DOMAIN={}\n".format(env_vars["domain"]))
        f.write("WIPI_ESSID=\"{}\"\n".format(env_vars["essid"]))
        f.write("WIPI_INTERFACE={}\n".format(interface))
        f.write("WIPI_NAT={}\n".format(env_vars["nat"]))
        f.write("WIPI_MODE={}\n".format(mode))
        f.write("WIPI_TRAFFIC_INTERFACE={}\n".format(env_vars["traffic_interface"]))
        f.write("WIPI_STATIC_IP={}\n".format(env_vars["static_ip"]))
        f.write("WIPI_PASSWORD=\"{}\"\n".format(env_vars["password"]))
      except KeyError:
        f.write("WIPI_CHANNEL={}\n".format(env_vars["channel"]))
        f.write("WIPI_DOMAIN={}\n".format(env_vars["domain"]))
        f.write("WIPI_ESSID=\"{}\"\n".format(env_vars["essid"]))
        f.write("WIPI_INTERFACE={}\n".format(interface))
        f.write("WIPI_NAT={}\n".format(env_vars["nat"]))
        f.write("WIPI_MODE={}\n".format(mode))
        #TODO see if this needs to be fixed
        #f.write("WIPI_TRAFFIC_INTERFACE={}".format(env_vars["traffic_interface"]))
        f.write("WIPI_TRAFFIC_INTERFACE={}\n".format("eth0"))
        f.write("WIPI_STATIC_IP={}\n".format(env_vars["static_ip"]))
        f.write("WIPI_PASSWORD=\"{}\"\n".format(env_vars["password"]))
