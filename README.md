# WiPi
#### By: stew3254

### Used to turn a Raspberry Pi into a wireless access point

This script allows you to set up a wireless access point with ease. In the matter of one command, an access point can be created and destroyed within mere seconds. It removes the hassle of learning how to configure services like hostapd, dnsmasq and iptables for basic uses. It's also beginner friendly and offers helpful feedback on how to use the command with command examples. The following is an example:

```
# wipi start wlan0
```

Help:

```
# wipi -h
Usage: wipi [start|stop] [OPTIONS] <interface>
Used to create wireless access points with ease

OPTIONS:
  -h  --help			Shows this menu
  -e  --essid	<ESSID>		ESSID of the access point
  -c  --channel	<channel>	Channel the access point is broadcasted on

Examples:
  wipi start -e 'Free WiFi' -c11 wlan0
  wipi stop wlan0
```

**Pros:**
* Takes seconds to set up a functioning access point with whatever name you choose
* It automatically sets up iptables rules to forward traffic out to the internet
* Automatically installs any software it needs (with user permission)
  * It also configures this software too
* Can detect if it is run as root or not
* Has a nice interface for command feedback and help
  * Examples are shown as well

**Cons:**
* It only does password-less WiFi access points
* You can't choose your own ip address range to have people to connect to
* If you break dnsmasq.conf and don't remove the file, this tool won't work
* If you don't have interface eth0 as your route for internet traffic, then you're SOL for internet access on the access point

**Todo:**
* Verbose option to print more helpful output and then print almost none if not invoked
* More options to the access point such as password protection, and better iptables masquerading
* More examples of how the command is used
* Bridged access point mode option vs default NAT option
