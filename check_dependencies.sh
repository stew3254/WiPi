#!/bin/bash

checkDepends() {
  #Check to make sure the dependencies are installed
  depend="iptables hostapd dnsmasq"

  #Check for each dependency
  for item in $depend; do
    #Check in the installed programs lists
    programList="`dpkg -l | grep $item | sed -e 's/  */ /g' | cut -d ' ' -f 2`"
    realProgram=""

    #Go through each program found in the list and make sure it's actually correct
    for program in $programList; do
      #Check to make sure the program has the exact same name
      if [ $program = $item ]; then
        realProgram="$item"
      fi
    done

    if [ -z $realProgram ]; then
      #Read input
      read -p "$item not installed. Would you like to install it now? (y/n) " input

      #Check to make sure the user agrees
      #If so install it. It not, exit the program. Otherwise, wait for a valid option
      while true; do
        if [ "$input" = "y" ] || [ "$input" = "Y" ]; then
          apt install $item -y
          systemctl stop $item
          break
        elif [ "$input" = "n" ] || [ "$input" = "N" ]; then
          echo "Exiting"
          exit 0
        else
          read -p "Please enter a valid option. (y/n) " input
        fi
      done
    fi
  done
}
