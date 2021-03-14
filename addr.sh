#!/bin/sh

#need sudo
ifconfig wlan0 down
#macchanger -m 01:23:45:67:aa:ff wlan0
ifconfig wlan0hw ether 02:17:25:7A:D2:75

ifconfig wlan0 10.188.190.54 netmask 255.255.0.0
route add default gw 10.188.0.1
#echo "nameserver 8.8.8.8" > /etc/resolv.conf

ifconfig wlan0 up
