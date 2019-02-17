#Used to print verbose statements
verbose() {
  if [ $verbosity = true ]; then
    for i in "$@"; do
      echo $i
    done
  fi
}

#Used to check if two files are the same by grabbing their md5 sums
checkFiles() {
  if [ "`md5sum $1 | cut -d ' ' -f 1`" != "`md5sum $2 | cut -d ' ' -f 1`" ]; then
    echo 1
  else
    echo 0
  fi
}

#Check to see if a service is active
checkActive() {
  echo `systemctl status $1 | grep Active | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
}

#Check to see if a service is running
checkRunning() {
  echo `systemctl status $1 | grep Active | cut -d ':' -f 2 | xargs | cut -d ' ' -f 2 | tr '()' ' ' | xargs`
}

#Check to see if a service is loaded
checkLoaded() {
  echo `systemctl status $1 | grep Loaded | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
}

#Check to see if the interface exists
checkInterface() {
  if [ -z "$1" ]; then
    echo "No interface specified. Please specify a wireless interface"
    exit 1;
  elif [ -z "`ip l | grep $1`" ]; then
    echo "Interface $1 does not exist. Please choose an interface that exists"
    exit 1;
  elif [ -z "`iw dev | grep $1`" ]; then
    echo "Interface $1 isn't a wireless card. Please choose an interface that is"
    exit 1;
  fi
}
