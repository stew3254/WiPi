#!/usr/bin/python3

import argparse
import sys
import checkargs
from exceptions import *


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
else:
  args = parser.parse_args()

  #Check arguments
  if args.channel != None:
    checkargs.check("channel", args.channel)
  elif args.domain != None:
    checkargs.check("domain", args.domain)
  elif args.essid != None:
    checkargs.check("essid", args.essid)
  elif args.interface != None:
    checkargs.check("interface", args.interface)
  elif args.nat != None:
    checkargs.check("nat", args.nat)
  elif args.password != None:
    checkargs.check("password", args.password)
