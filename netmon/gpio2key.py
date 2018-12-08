#!/usr/bin/python3

import time
import uinput
import RPi.GPIO as GPIO

gpios = [
	{ "channel": 17, "key": uinput.KEY_X },
	{ "channel": 22, "key": uinput.KEY_H },
	{ "channel": 23, "key": uinput.KEY_E },
	{ "channel": 27, "key": uinput.KEY_L }
]

# initialize gpios
GPIO.setmode(GPIO.BCM)
for gpio in gpios:
	GPIO.setup(gpio["channel"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# extract events
events = [gpio["key"] for gpio in gpios]

# initialize uinput
with uinput.Device(events) as device:
	# main loop
	while True:
		for gpio in gpios:
			if GPIO.input(gpio["channel"]) == False:
				if ("pressed" not in gpio or not gpio["pressed"]):
					device.emit(gpio["key"], 1)
					gpio["pressed"] = True
#				print(gpio["channel"])
			else:
				if ("pressed" in gpio and gpio["pressed"]):
					gpio["pressed"] = False
					device.emit(gpio["key"], 0)
#					print("Reset")
		time.sleep(0.05)
