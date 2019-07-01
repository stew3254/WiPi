#TODO: Clean this whole thing up
#Used to start the services
startServices() {
  #What the function returns
  local output=0

  #Check through all of the services
  for service in "$@"; do

    #Attempt to start the services
    if [ "`checkActive $service`" != "active" ]; then
      if [ "`checkLoaded $service`" != "masked" ]; then
        verbose "Starting $service"
        systemctl start $service
      else
        #Check to see if service is running as a process
        if [ -n "`pgrep $service`" ]; then
          output=1
          verbose "Failed to start $service because it is already running"
          break
        elif [ "$service" = "dnsmasq" ]; then
          verbose "Starting $service"
          dnsmasq
        elif [ "$service" = "hostapd" ]; then
          verbose "Starting $service"
          hostapd -d /etc/hostapd/hostapd.conf &> /dev/null &
        else
          output=1
          verbose "Failed to start $service"
          break
        fi
      fi
    #Check to see if the service isn't running and isn't actually running as a process
    elif [ "`checkRunning $service`" != "running" ] && [ -z "`pgrep $service`" ]; then
      if [ "$service" = "dnsmasq" ]; then
        verbose "Starting $service"
        dnsmasq
      elif [ "$service" = "hostapd" ]; then
        verbose "Starting $service"
        hostapd -d /etc/hostapd/hostapd.conf &> /dev/null &
      fi
    else
      output=1
      verbose "Failed to start $service because it is already running"
      break
    fi

  done

  #Return of the function
  echo $output
}
