#!/usr/bin/python3

import sys
import subprocess
import os
from exceptions import BadKeyValuePair

def check(key, value):
  """
  Checks the key and value of an input. If it's bad, raise an exception. If it's good
  add it to the environmental variables so the rest of the scripts can use it
  """
  if key == "channel":
    try:
      #Make sure the value is right
      if int(value) < 1 or int(value) > 11:
        raise BadKeyValuePair("Channel must be an integer between 1 and 11")
    except ValueError:
      raise BadKeyValuePair("Channel must be an integer between 1 and 11")
    os.environ["WIPI_CHANNEL"] = str(value)

  elif key == "essid" and len(value) < 1 and len(value) > 32:
    raise BadKeyValuePair("ESSID must be between 1 and 32 characters")
    os.environ["WIPI_ESSID"] = value

  elif key == "interface":
    exists = False
    interfaces = []
    #Get a list of interfaces and split the output by line
    out = subprocess.check_output("ip l", shell=True).decode("utf8").split("\n")
    for new_line in out:
      try:
        parts = new_line.split(":")
        #See if the first part of the line is an integer
        int(parts[0])
        if value == parts[1].strip():
          exists = True
      except ValueError:
        pass
    if not exists:
      raise BadKeyValuePair("Interface does not exist")
    os.environ["WIPI_INTERFACE"] = value

  elif key == "nat":
    octets = value.split(".")
    #Make sure the ip is of proper size
    if len(octets) != 4:
      raise BadKeyValuePair("IPv4 address must contain 4 octets and a CIDR notatation")
    #Check first 3 octets
    for octet in range(3):
      try:
        if int(octets[octet]) < 1 or int(octets[octet]) > 254:
          raise BadKeyValuePair("IPv4 octets must be between 1 and 254")
      except ValueError:
        raise BadKeyValuePair("IPV4 address must use integers between 1 and 254")
    try:
      #Get the last octet and subnet mask
      ip_id, subnet = octets[-1].split("/")
      if int(ip_id) < 1 or int(ip_id) > 254:
        raise BadKeyValuePair("IPV4 address must use integers between 1 and 254")
      elif int(subnet) < 0 or int(subnet) > 31:
        raise BadKeyValuePair("CIDR notation for subnet mask must be between 0 and 31 (24 is recommended)")
    except IndexError:
      raise BadKeyValuePair("IPv4 has an improper CIDR notation specification")
    except ValueError:
      raise BadKeyValuePair("IPv4 address and CIDR notation must use integers")
    os.environ["WIPI_NAT"] = value
    os.environ["WIPI_IP"] = value.split("/")[0]
    os.environ["WIPI_CIDR"] = value.split("/")[1]

  elif key == "password":
    if len(value) < 8 or len(value) > 64:
      raise BadKeyValuePair("Password must be between 8 and 64 characters")
    os.environ["WIPI_PASSWORD"] = value
