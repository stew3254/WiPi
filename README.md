# WiPi
#### By: stew3254

### Used to turn a Raspberry Pi into a wireless access point

This script allows you to set up a wireless access point with ease. In the matter of one command, an access point can be created and destroyed within mere seconds. It removes the hassle of learning how to configure services like hostapd, dnsmasq and iptables for basic uses. It's also beginner friendly and offers helpful feedback on how to use the command with command examples. The following is an example:

```
# wipi start wlan0
```

Example help command:

```
# wipi -h
Usage: wipi [stop|start|restart] [OPTIONS] <interface>
Used to create wireless access points with ease

OPTIONS:
  -c  --channel  <channel>	Channel the access point is broadcasted on
  -e  --essid  <ESSID>		ESSID of the access point (The default is 'WiPi AP')
  -d  --domain  <domain>	Domain name of the local network created by dnsmasq
  -h  --help			Shows this menu
  -i  --interface  <interface>	The interface used to route traffic out of (default is eth0)
  -n  --nat  <static ip>	The static ip set to the NAT (The subnet mask is a /24)
  -p  --password  <password>	The password of the access point (WPA2/PSK)
  -v  --verbose			Increases verbosity of the output of the program

Examples:
  wipi start -c 1 -d foo.net --essid Foo -p FooBarBaz -n 192.168.0.1 wlan0
  wipi restart -e 'Free WiFi' -c11 -i enp2s0 wlp3s0
  wipi stop --verbose wlan1
```

**Pros:**
* Takes seconds to set up a functioning access point with whatever name you choose
* Can be used as an online or offline access point
* It automatically sets up iptables rules to forward traffic out to the internet
* Automatically installs any software it needs (with user permission)
  * It also configures this software too
* Can detect if it is run as root or not
* Can detect if the interface is a wireless adapter or not
* Can allow for open or password protected WPA2 networks
* You can set your own NAT (only with a /24 netmask though)
* Is pretty resilient if services or assigning ips break. The script generally can tell you what went wrong
* Has a nice interface for command feedback and help
  * Examples are shown as well
* Can be scripted to run on device startup (not easily afaik though, sorry)

**Cons:**
* You can't choose your own netmask 
* Doesn't support bridging straight into a network
* If using several wireless adapters (one for wipi and one for internet), you need to restart wpa_supplicant in order to reconnect to an access point.
* Does not support IPV6 addresses

**Todo:**
* Make a config folder for default configs. Then the user can change the defaults at their will
* Automatically create a file for wipi in /usr/local/bin so it will be in the default PATH
* Split wipi into several files to organize the code better
* More options to the access point such as password protection, and better iptables masquerading
* Bridged access point mode option vs default NAT option
* Maybe check for proper dnsmasq and hostapd syntax
* Maybe allow tab completion for the next reasonable argument
* Make better documentation
  * Add code output examples
  * Add a picture of the access point produced
  * Show the leases table to show the dhcp working and a client is connected
  * Show an output of the ping command from a connected client
