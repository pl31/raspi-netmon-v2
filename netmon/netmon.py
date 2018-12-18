#!/usr/bin/env python3

import argparse
import time
import datetime
import sys
import os
import subprocess
import re
import math
import netifaces
import pygubu
from tkinter import ttk
from ttkthemes import ThemedStyle

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

class Application:
    def __init__(self, if1, if2, fullscreen):
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()
        # 2: Load an ui file
        builder.add_from_file(os.path.join(CURRENT_DIR, 'netmon.ui'))
        # 3: Create the toplevel widget.
        self.mainwindow = builder.get_object('mainwindow')
        #4: connect callbacks
        self.builder.connect_callbacks(self)
        # 5: optional fullscreen
        if (fullscreen):
            self.mainwindow.attributes("-fullscreen", True)

        # 6: prepare styling
        self.style = ThemedStyle(self.mainwindow)
        self.current_style = 'radiance'
        self.alarm = False

        # set interface vars & update ui
        self.if1 = if1
        self.builder.get_object('if1_labelframe').config(text=if1)
        self.if2 = if2
        self.builder.get_object('if2_labelframe').config(text=if2)
        # bind ui-vars to local-vars
        self.dateVar = self.builder.get_variable('dateVar')
        self.timeVar = self.builder.get_variable('timeVar')
        self.if1ipVar = self.builder.get_variable('if1ipVar')
        self.if1rxVar = self.builder.get_variable('if1rxVar')
        self.if1TputVar = self.builder.get_variable('if1TputVar')
        self.if2ipVar = self.builder.get_variable('if2ipVar')
        self.if2rxVar = self.builder.get_variable('if2rxVar')
        self.if2TputVar = self.builder.get_variable('if2TputVar')

    def get_rx_packets_delta(self, interface):
        f_name = '/sys/class/net/{}/statistics/rx_packets'.format(interface)
        try:
            with open(f_name) as f:
                rx_packets = int(f.read().strip())
            if (not self.last_rx_packets[interface]):
                self.last_rx_packets[interface] = rx_packets
            rx_packets_delta = rx_packets - self.last_rx_packets[interface]
            self.last_rx_packets[interface] = rx_packets
            return rx_packets_delta
        except:
            return '-'

    def get_bytes_delta(self, interface):
        r_name = '/sys/class/net/{}/statistics/rx_bytes'.format(interface)
        t_name = '/sys/class/net/{}/statistics/tx_bytes'.format(interface)
        try:
            with open(r_name) as r:
                rx_bytes = int(r.read().strip())
            with open(t_name) as t:
                tx_bytes = int(t.read().strip())
            if (not self.last_rx_bytes[interface]):
                self.last_rx_bytes[interface] = rx_bytes
            if (not self.last_tx_bytes[interface]):
                self.last_tx_bytes[interface] = tx_bytes
            rx_bytes_delta = rx_bytes - self.last_rx_bytes[interface]
            tx_bytes_delta = tx_bytes - self.last_tx_bytes[interface]
            self.last_rx_bytes[interface] = rx_bytes
            self.last_tx_bytes[interface] = tx_bytes
            bytes_delta = rx_bytes_delta + tx_bytes_delta
            return bytes_delta
        except:
            return '-'


    def get_ip(self, interface):
        try:
            netifaces.ifaddresses(interface)
            return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        except:
            return '-.-.-.-/-'

    def quit(self, event=None):
        self.mainwindow.quit()

    def update_values(self):
        # date/time
        now = datetime.datetime.now()
        self.dateVar.set(now.date().isoformat())
        self.timeVar.set(now.strftime('%H:%M:%S'))
        # if1
        delta_if1 = self.get_rx_packets_delta(self.if1)
        self.if1ipVar.set(self.get_ip(self.if1))
        self.if1rxVar.set('{} pkts/s'.format(delta_if1))
        # if2
        delta_if2 = self.get_rx_packets_delta(self.if2)
        self.if2ipVar.set(self.get_ip(self.if2))
        self.if2rxVar.set('{} pkts/s'.format(delta_if2))

        # if1 bytes
        delta_if1_bytes = self.get_bytes_delta(self.if1)
        # change unit bit/s
        delta_if1_bit = delta_if1_bytes * 8
        # convert to human readable based on load
        if (delta_if1_bit / 1024) < 1024:
            self.if1TputVar.set('{0:.2f} Kbit/s'.format(delta_if1_bit / 1024))
        else:
            self.if1TputVar.set('{0:.2f} Mbit/s'.format((delta_if1_bit / 1024) / 1024))
        
        # if2 bytes
        delta_if2_bytes = self.get_bytes_delta(self.if2)
        # change unit bit/s
        delta_if2_bit = delta_if2_bytes * 8
        # convert to human readable based on load
        if (delta_if2_bit / 1024) < 1024:
            self.if2TputVar.set('{0:.2f} Kbit/s'.format(delta_if2_bit / 1024))
        else:
            self.if2TputVar.set('{0:.2f} Mbit/s'.format((delta_if2_bit / 1024) / 1024))

        # check alarmstate, and set style accordingly
        alarm = delta_if1 > 1000 or delta_if2 > 1000
        if alarm != self.alarm:
            if alarm:
                self.style.theme_use('kroc')
            else:
                self.style.theme_use(self.current_style)
            self.alarm = alarm

        # wait to update, always to "full" second
        self.mainwindow.after(
            1000 - (datetime.datetime.now().microsecond // 1000),
            self.update_values)

    def change_style(self):
        now = datetime.datetime.now()
        # sync color change - even to radiance - odd to equilux
        if now.minute // 10 % 2:
            self.current_style = 'equilux'
        else:
            self.current_style = 'radiance'

        if not self.alarm:
            self.style.theme_use(self.current_style)

        # calculate time to next full 10 min (10, 20, 30, ...)
        deltatime = ((now.minute % 10) * (60 * 1000)) + (now.second * 1000) + now.microsecond // 1000
        waittime = (10 * 60 * 1000) - deltatime

        # wait to change style
        self.mainwindow.after(waittime,
            self.change_style)

    def run(self):
        self.last_rx_packets = {
            self.if1: None,
            self.if2: None
            }
        self.last_rx_bytes = {
            self.if1: None,
            self.if2: None
            }
        self.last_tx_bytes = {
            self.if1: None,
            self.if2: None
            }
        self.update_values()
        self.change_style()
        self.mainwindow.mainloop()


if __name__ == '__main__':
    # Parse arguments
    # parser = argparse.ArgumentParser(description='Package monitoring')
    # requiredNamed = parser.add_argument_group('required named arguments')
    # requiredNamed.add_argument('-s', '--size', help='Display size, e.g. 20x4', required=True)
    # args = parser.parse_args()

    fullscreen = True
    app = Application('eth0', 'wlan0', fullscreen)
    #app = Application('enp3s0', 'lo', fullscreen)
    app.run()


# def main():
#     # initial values
#     last_n_rx_packets_delta = [0] * width
#     last_rx_packets = get_rx_packets(interface)
#
#     while True:
#         rx_packets = get_rx_packets(interface)
#         rx_packets_delta = rx_packets - last_rx_packets
#         last_rx_packets = rx_packets
#         last_n_rx_packets_delta.pop(0)
#         last_n_rx_packets_delta.append(rx_packets_delta)
#
#         lineNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M").rjust(width)
#         print(lineNow)
#
#         lineChart = ''
#         for pkts in last_n_rx_packets_delta:
#             index = 0 if pkts == 0 else int(min(math.log(pkts, 4), 8))  # between 0 - 8
#             lineChart += chars[index]
#         print(lineChart)
#
#         print()
#
#         time.sleep(1)
