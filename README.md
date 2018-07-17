# raspi-netmon-v2

Create a fresh installation of raspian-lite:
- https://www.raspberrypi.org/downloads/raspbian/
- `dd` image to SD-Card and add an empty file `ssh` to boot folder
- boot device add ssh into it (user `pi`, password `raspberry`)  
  `ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no pi@<ip_of_raspi>`
- configure device as needed using `sudo raspi-config`
  - Change timezone

Enable pitft:
Follow the guide at https://learn.adafruit.com/adafruit-2-2-pitft-hat-320-240-primary-display-for-raspberry-pi/easy-install
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh)"
```
For pitft capacitive 2.8" use [3,4,y - console on PiTFT]

Download and execute the installer:
```
wget -O - https://raw.githubusercontent.com/pl31/raspi-netmon-v2/master/installer/installer.sh | sh
```

If happy with the result, make SD-Card read-only:
```
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/read-only-fs.sh)"
```
