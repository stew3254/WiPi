#!/usr/bin/python3

from configGenerator import *
from exceptions import *
import os
import sys

if len(sys.argv) < 3:
  raise IncorrectArguments("Not enough arguments passed")

if os.path.exists("/etc/wipi") and os.path.isfile("/etc/wipi"):
  os.rename("/etc/wipi", "/etc/wipi.old")
  os.mkdir("/etc/wipi")
elif not os.path.exists("/etc/wipi"):
  os.mkdir("/etc/wipi")

generate = Generate()
if not os.path.isfile("/etc/wipi/wipi.conf"):
  generate.wipi()
if not os.path.isfile("/etc/wipi/env_vars.sh"):
  generate.set_env_vars(sys.argv[1], sys.argv[2])
