#!/usr/bin/python3

import argparse
import checkArgs
import filecmp
import subprocess
import sys
import os
from exceptions import *
from configGenerator import Generate


#Weird hacks to make argparse look pretty
class HelpFormatter(argparse.RawTextHelpFormatter):

  #Print in a pretty format
  def _format_action_invocation(self, action):
    ret = ''
    for item in list(action.option_strings) + ['<{}>'.format(action.dest)]:
      if len(item) < 4:
        ret += f'{item:4}'
      else:
        ret += f'{item:12}'
    return ret

  #Formats the text in help
  def _format_action(self, action):
    width = 24
    return f"  {self._format_action_invocation(action):{width}} {action.help}\n"

  #Reset usage name and strip extra newline character
  def _format_usage(self, usage, actions, groups, prefix):
    return super()._format_usage(usage, actions, groups, "Usage: ")[:-1]


#Help the program displays
description = 'Used to create a wireless access point with ease'
program = "wipi"
usage = "{} [start|restart|stop] [OPTIONS] <interface>".format(program)
epilog = """Examples:
  wipi start -c 1 -d foo.net --essid Foo -p Bar wlan0
  wipi restart -e 'Free WiFi' -c11 -i enp2s0 wlp3s0
  wipi stop wlan1"""

#Create the parser
parser = argparse.ArgumentParser(add_help=False, description=description,
                                 usage=usage, prog=program, epilog=epilog,
                                 formatter_class=HelpFormatter)

#Add a new group to the parser and then add the subsequent arguments to it
group = parser.add_argument_group("OPTIONS")
group.add_argument("[start|restart|stop]", help=argparse.SUPPRESS)
group.add_argument("<interface>", help=argparse.SUPPRESS)

#Add optional arguemnts
group.add_argument('-c', '--channel', help="Sets the channel of the access point",
                    type=int)
group.add_argument('-d', '--domain', help="Sets the domain of the DHCP range",
                    type=str)
group.add_argument('-e', '--essid', help="Sets the name of the access point",
                    type=str)
group.add_argument('-h', '--help', help="Used to display this page", action="help")
group.add_argument('-i', '--interface', help="Sets which interface to route traffic out of",
                    type=str)
group.add_argument('-n', '--nat', help="Sets the static IP of the device",
                    type=str)
group.add_argument('-p', '--password', help="Sets the password of the access point (WPA2/PSK)",
                    type=str)
group.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

#If no parameters are invoked, run the help command
if len(sys.argv) == 1:
  parser.print_help()
  sys.exit(1)
else:
  args = parser.parse_args()

  #Environmental variables to add to a dictionary
  env = {"WIPI_MODE" : sys.argv[1]}

  if sys.argv[1] != "start" and sys.argv[1]  != "restart" and sys.argv[1] != "stop":
    raise BadAPMode("Tried to use a value other than stop, start, or restart")
  if sys.argv[-1] not in subprocess.check_output("ip l", stderr=subprocess.STDOUT, shell=True).decode():
    raise BadInterface("Bad interface option. This interface doesn't exist or is invalid")

  #Check arguments
  if args.channel != None:
    checkArgs.check("channel", args.channel)
    env.update({"WIPI_CHANNEL": args.channel})
  if args.domain != None:
    checkArgs.check("domain", args.domain)
    env.update({"WIPI_DOMAIN": args.domain})
  if args.essid != None:
    checkArgs.check("essid", args.essid)
    env.update({"WIPI_ESSID": args.essid})
  if args.interface != None:
    checkArgs.check("traffic_interface", args.interface)
    env.update({"WIPI_TRAFFIC_INTERFACE": args.interface})
  if args.nat != None:
    checkArgs.check("nat", args.nat)
    env.update({"WIPI_NAT": args.nat})
  if args.password != None:
    checkArgs.check("password", args.password)
    env.update({"WIPI_PASSWORD": args.password})

  interface = sys.argv[-1]
  checkArgs.check("interface", interface)

  #Used to format the environmental variables in a format bash can use
#  with open("env_vars.sh", "w") as f:
#    with open("/etc/wipi/env_vars.sh", "r") as fo:
#      for line in fo.readlines():
#        written = False
#        for key in env.keys():
#          if key in line:
#            value = line.split("=")[1].strip(' \t\n"')
#            if env[key] in value:
#              f.write(line.replace(value, env[key]) + "\n")
#              written = True
#        if not written:
#          f.write(line + "\n")
#        else:
#          written = False

  generator = Generate()
  generator.set_env_vars(sys.argv[1], interface, env)

  if "env_vars.sh" in os.listdir():
    if not filecmp.cmp("env_vars.sh", "/etc/wipi/env_vars.sh"):
      os.rename("env_vars.sh", "/etc/wipi/env_vars.sh")
