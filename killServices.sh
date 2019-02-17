#Used to kill services
killServices() {
  #What the function returns
  local output=0

  #Check through all of the services
  for service in "$@"; do

    #Check to see if the service is active
    if [ "`checkActive $service`" = "active" ] && [ "`checkRunning $service`" = "running" ]; then
      verbose "Stopping $service"
      systemctl stop $service
    #If the service is a process, kill it
    elif [ -n "`pgrep $service`" ]; then
      verbose "Stopping $service"
      pkill $service
    #Otherwise error
    else
      systemctl stop $service
      output=1
      verbose "Failed to stop $service because it isn't running"
      break
    fi

  done

  #Make sure the services are inactive
  for service in "$@"; do
    if [ $output -eq 1 ]; then
      if [ -n "`pgrep $service`" ]; then
        pkill $service
      fi
    elif [ "`checkActive $service`" = "active" ]; then
      systemctl stop $service
    elif [ -n "`pgrep $service`" ]; then
      pkill $service
    else
      break
    fi
  done

  #Return of the function
  echo $output
}
