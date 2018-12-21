# WiPi
Used to turn a Raspberry Pi into an offline, or online wireless access point.

Flaws:
* Requires aircrack-ng to kill conflicting processes
* Very inflexible
  * It doesn't allow you to choose the interface to use
  * It doesn't let you choose a channel to use
  * It only does unlocked WiFi access points
  * You can't choose your own ip address range to have people to connect to
  * If you break dnsmasq.conf and don't remove the file, this tool won't work
  * Doesn't forward network traffic yet
