#!/bin/sh

# "not ((port 22 or port 80) and ether host $(cat /sys/class/net/eth0/address))"
/usr/sbin/tcpdump -n -U -s 0 -i eth0 -W 4 -C 32M -w /var/run/tcpdump_eth0/tcpdump_eth0_ "not ether host $(cat /sys/class/net/eth0/address)"
