#! python

"""

CaptureTransitions.py

Captures timing information from a key to a file for
later playback and analysis. All transitions are captured.
No contact debounce filter is applied.

Usage: python CaptureTransitions.py >filename.txt

"""

from __future__ import print_function  # in case you want it to work with Python 2.7
import sys
import time
import serial
if sys.platform == 'win32':
    from ctypes import windll
    windll.winmm.timeBeginPeriod(1)  # set clock resoluton to 1 ms (Windows only)

VERSION = '1.1'
PORT = 'COM3'
#PORT = '/dev/ttyUSB0'
N = 50

print('CaptureTransitions {} - {}'.format(VERSION, time.asctime()))
sys.stdout.flush()

port = serial.Serial(PORT)
port.setDTR(True)
s0 = port.getDSR()

t = [0] * N
t[0] = time.time()
n = 1
try:
    while True:
        s1 = port.getDSR()
        if s0 != s1:
            t[n] = time.time()
            n += 1
            if n >= N:
                break
            s0 = s1
except:
    pass
for i in range(1, n):
    dt = t[i] - t[0]
    ddt = t[i] - t[i - 1]
    print('{:8.3f} {:9,.1f}'.format(dt, 1000 * ddt))
