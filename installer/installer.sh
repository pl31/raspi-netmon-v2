#!/bin/bash

# Fail fast
set -e

echo "---> Running netmon installer"

echo "---> Install required packages"
sudo apt install -y git fbterm lighttpd tcpdump python3-setuptools python3-setuptools-git python3-netifaces

echo "---> Configure webserver"
sudo rm -f /var/www/html/index.lighttpd.html
sudo lighttpd-enable-mod dir-listing || true
# disable logging for ro filesystem
sudo sed '/^server.errorlog/s/^/#/g' -i /etc/lighttpd/lighttpd.conf

echo "---> Freshly clone repository to home folder"
rm -rf ~/raspi-netmon/
git clone --depth=1 https://github.com/pl31/raspi-netmon-v2.git ~/raspi-netmon-v2/

echo "---> Set promiscuous mode for eth0"
sudo cp ~/raspi-netmon-v2/installer/promiscuous@.service /etc/systemd/system
sudo systemctl enable promiscuous@eth0.service

echo "---> Add netmon to .bash_login"
echo >> ~/.profile
echo "clear; fbterm -r 3 -s 54 -- python3 ~/raspi-netmon-v2/netmon/netmon.py -s 20x13" >> ~/.profile

echo "---> Enable tmpfs for tcpdump"
sudo cp ~/raspi-netmon-v2/installer/var-run-tcpdump_eth0.mount /etc/systemd/system
sudo systemctl enable var-run-tcpdump_eth0.mount
sudo systemctl start var-run-tcpdump_eth0.mount
echo "---> Create symbolic links for tcpdump"
sudo sh -c 'for i in `seq 0 3`; do ln -s /var/run/tcpdump_eth0/tcpdump_eth0_$i /var/www/html/tcpdump_eth0_$i.pcap; done' || true
echo "---> Enable tcpdump service"
sudo cp ~/raspi-netmon-v2/installer/tcpdump_eth0.service /etc/systemd/system
sudo systemctl enable tcpdump_eth0.service

echo
echo "PLEASE REBOOT DEVICE"
