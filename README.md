# raspi-netmon-v2

## Create a fresh installation of raspian-lite

- https://www.raspberrypi.org/downloads/raspbian/
- `dd` image to SD-Card and add an empty file `ssh` to boot folder
- boot device add ssh into it (user `pi`, password `raspberry`)  
  `ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no pi@<ip_of_raspi>`
- configure device as needed using `sudo raspi-config`
  - Change timezone

## Download and install netmon
```
wget -O - https://raw.githubusercontent.com/pl31/raspi-netmon-v2/master/installer/installer.sh | sh
```

## Enable pitft

Follow the guide at https://learn.adafruit.com/adafruit-2-2-pitft-hat-320-240-primary-display-for-raspberry-pi/easy-install
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh)"
```
For pitft capacitive 2.8" use [3,4,n,y,y - HDMI mirror on PiTFT]

Finally edit `/boot/config.txt` find the line `hdmi_cvt` and change to 320x240:
```
hdmi_cvt=320 240 60 1 0 0 0
```

## Make readonly

If happy with the result, make SD-Card read-only (install cron+ntp for timesync):
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/read-only-fs.sh)"
```
## Troubleshooting

### Mouse inverted

/usr/share/X11/xorg.conf.d/20-calibration.conf

Section "InputClass"
        Identifier "FocalTech Touchscreen Calibration"
        MatchProduct "EP0110M09"
        MatchDevicePath "/dev/input/event*"
        Driver "libinput"
        Option "TransformationMatrix" "-1 0 1 0 -1 1 0 0 1"
EndSection
