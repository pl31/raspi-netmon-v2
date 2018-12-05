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

        self.style = ThemedStyle(self.mainwindow)
        self.style.theme_use('radiance')
        # equilux, radiance, (arc)

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
        self.if2ipVar = self.builder.get_variable('if2ipVar')
        self.if2rxVar = self.builder.get_variable('if2rxVar')

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
        self.if1ipVar.set(self.get_ip(self.if1))
        self.if1rxVar.set('{} pkts/s'.format(self.get_rx_packets_delta(self.if1)))
        # if2
        self.if2ipVar.set(self.get_ip(self.if2))
        self.if2rxVar.set('{} pkts/s'.format(self.get_rx_packets_delta(self.if2)))

        # wait to update, always to "full" second
        self.mainwindow.after(
            1000 - (datetime.datetime.now().microsecond // 1000),
            self.update_values)

    def run(self):
        self.last_rx_packets = {
            self.if1: None,
            self.if2: None
            }
        self.update_values()
        self.mainwindow.mainloop()


if __name__ == '__main__':
    # Parse arguments
    # parser = argparse.ArgumentParser(description='Package monitoring')
    # requiredNamed = parser.add_argument_group('required named arguments')
    # requiredNamed.add_argument('-s', '--size', help='Display size, e.g. 20x4', required=True)
    # args = parser.parse_args()

    fullscreen = True
    app = Application('eth0', 'wlan0', fullscreen)
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
