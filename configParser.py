#!/usr/bin/python3

from exceptions import *
import checkargs


class Config_Parser:
  """
  WiPi Config Parser
  """
  def __init__(self):
    self._keywords = ["channel", "domain", "essid", "interface", "nat", "password"]
    self._used_keywords = []

  #Do a rough parse of the file
  def get_pairs(self):
    pairs = {}
    with open("wipi.conf", "r") as f:
      for line in f.readlines():
        line = line.strip()
        #Check that the line isn't empty
        if line != "":
          #Set the key of the line
          pair = line.split("=")
          key = pair[0].strip()

          #Find invalid config options
          if key[0] != "#" and key not in self._keywords:
            raise _BadKeyValuePair("_Bad key value")

          #Find reused config options
          elif key[0] != "#" and key in self._used_keywords:
            raise KeyReuse("Tried to redeclare a key and value pair")

          #Find good config keys
          elif key[0] != "#" and key in self._keywords:
            if len(pair) != 2:
              raise _BadKeyValuePair("There must only be 1 value")
            else:
              value = pair[1].strip()
              pairs.update({key: value})
    return pairs

  def parse(self):
    #Get the possible config options to parse
    pairs = self.get_pairs()
    #Look through all keys and get their values
    for key in pairs.keys():
      value = pairs[key]
      checkargs.check(key, value)
