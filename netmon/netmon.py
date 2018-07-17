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

def get_rx_packets(interface):
  f_name = '/sys/class/net/{}/statistics/rx_packets'.format(interface)
  with open(f_name) as f:
    return int(f.read().strip())

def get_indicator(indicator=None):
  if indicator == '-':
    return '|'
  if indicator == '|':
    return '-'
  else:
    return '-'

def get_ip(interface):
  netifaces.ifaddresses('eth0')
  try:
    return netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
  except:
    return '-.-.-.-'

# Parse arguments
parser = argparse.ArgumentParser(description='Package monitoring')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-s', '--size', help='Display size, e.g. 20x4', required=True)
args = parser.parse_args()

width = int(args.size.split('x')[0])
height = int(args.size.split('x')[1])

# default values
interface = 'eth0'

# create block char array
chars = [ ' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█' ]

# initial values
last_n_rx_packets_delta = [0] * width
last_rx_packets = get_rx_packets(interface)
time.sleep(1)
indicator = get_indicator()

while True:
  rx_packets = get_rx_packets(interface)
  rx_packets_delta = rx_packets - last_rx_packets
  last_rx_packets = rx_packets
  last_n_rx_packets_delta.pop(0)
  last_n_rx_packets_delta.append(rx_packets_delta)

  indicator = get_indicator(indicator)

  lineIP = get_ip(interface).rjust(width)
  linePkts = '{}{}{:9d} pkt/s'.format(indicator, ' ' * (width-16), rx_packets_delta)

  os.system('clear')

  print(lineIP)
  print(linePkts)

  lineNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M").rjust(width)
  print(lineNow)

  lineChart = ''
  for pkts in last_n_rx_packets_delta:
    index = 0 if pkts ==0 else int(min(math.log(pkts,4), 8))  # between 0 - 8
    lineChart += chars[index]
  print(lineChart)

  print()

  time.sleep(1)
