#!/bin/bash

# Fail fast
set -e

echo "---> Running netmon installer"

echo "---> Upgrade installation"
sudo apt update
sudo apt -y upgrade

echo "---> Install required packages"
sudo apt install -y git lighttpd tcpdump \
  python3-setuptools python3-setuptools-git python3-pip python3-netifaces python3-tk \
  xorg openbox lightdm unclutter uinput

echo "---> Install required python packages"
sudo pip3 install python-uinput RPi.GPIO pygubu ttkthemes
sudo pip3 install

echo "---> Freshly clone repository to home folder"
rm -rf ~/raspi-netmon-v2/
git clone --depth=1 https://github.com/pl31/raspi-netmon-v2.git ~/raspi-netmon-v2/

echo "---> Copy modules-load.d"
sudo cp ~/raspi-netmon-v2/installer/etc/modules-load.d/* /etc/modules-load.d/

echo "---> Configure autologin"
sudo mkdir -p /etc/lightdm/lightdm.conf.d
sudo cp ~/raspi-netmon-v2/installer/etc/lightdm/lightdm.conf.d/autologin.conf \
  /etc/lightdm/lightdm.conf.d

echo "---> Configure webserver"
sudo rm -f /var/www/html/index.lighttpd.html
sudo lighttpd-enable-mod dir-listing || true
# disable logging for ro filesystem
sudo sed '/^server.errorlog/s/^/#/g' -i /etc/lighttpd/lighttpd.conf

echo "---> Set promiscuous mode for eth0 and wlan0"
sudo cp ~/raspi-netmon-v2/installer/promiscuous@.service /etc/systemd/system
sudo systemctl enable promiscuous@eth0.service
sudo systemctl enable promiscuous@wlan0.service

echo "---> Add netmon to autostart"
mkdir -p ~/.config/openbox
cp ~/raspi-netmon-v2/installer/.config/openbox/autostart ~/.config/openbox

echo "---> Enable tmpfs for tcpdump"
sudo cp ~/raspi-netmon-v2/installer/var-run-tcpdump.mount /etc/systemd/system
sudo systemctl enable var-run-tcpdump.mount
sudo systemctl start var-run-tcpdump.mount
echo "---> Create symbolic links for tcpdump"
sudo sh -c 'for i in `seq 0 3`; do ln -s /var/run/tcpdump/tcpdump_eth0_$i /var/www/html/tcpdump_eth0_$i.pcap; done' || true
sudo sh -c 'for i in `seq 0 3`; do ln -s /var/run/tcpdump/tcpdump_wlan0_$i /var/www/html/tcpdump_wlan0_$i.pcap; done' || true
echo "---> Enable tcpdump service"
sudo cp ~/raspi-netmon-v2/installer/tcpdump@.service /etc/systemd/system
sudo systemctl enable tcpdump@eth0.service
sudo systemctl enable tcpdump@wlan0.service

echo
echo "PLEASE REBOOT DEVICE"
