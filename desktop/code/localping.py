#!/usr/bin/env python3

import os
import sys
import subprocess
import signal

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

start = 0
end = 255

if len(sys.argv) < 2:
    print("localping.py partialIP [start [end]]")

if len(sys.argv) > 2:
    start = int(sys.argv[2])

if len(sys.argv) > 3:
    end = int(sys.argv[2])

for i in range(start, end):
    ip = sys.argv[1] + '.' + str(i)
    exists = False
    try:
        subprocess.check_output('ping -n 1 -w 500 ' + ip, shell=True)
        exists = True
    except:
        pass
    finally:
        if exists:
            print(ip + ' exists')