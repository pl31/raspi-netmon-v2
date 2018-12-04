#!/bin/sh
# $1 is network interface (eth0, wlan0)
if=$1

filter="not ether host $(cat /sys/class/net/$if/address)"
echo "Filter: \"$filter\""

/usr/sbin/tcpdump -n -U -s 0 -i $if -W 4 -C 16M -w '/var/run/tcpdump/tcpdump_'$if'_' "$filter"
