#!/bin/bash

#Make bash exit when it any programs fail
set -e

#Make sure the defaults are set
python3 defaults.py $1 ${@: -1}

#Parse the arguments and save them to a runtime file (I hate using files but don't know how not to)
#Has problems with passing things with spaces in it. MUST FIX
python3 argParser.py $@
#Source the variables
source /etc/wipi/env_vars.sh

#Check to see if the access point should be restarted
if [ "$WIPI_MODE" = "restart" ]; then
  echo "Attempting to restart the access point"
  bash stop.sh
  bash start.sh
  echo "Restarted the access point"
  echo "New name is $name"
#Check to see if the access point should be started
elif [ "$WIPI_MODE" = "start" ]; then
  echo "Attempting to start the access point"
  bash bash start.sh
#Check to see if the access point should be stopped
elif [ "$WIPI_MODE" = "stop" ]; then
  echo "Attempting to stop the access point"
  bash stop.sh
fi
