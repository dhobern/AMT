#!/usr/bin/env python3

import RPi.GPIO as GPIO
import subprocess
from amt_timelapse import timelapse
from amt_util import *

GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN)

config = loadconfig()
initmodes(config)
initstatus(config)

listening = True
while listening:

    print("Sleeping")
    GPIO.wait_for_edge(3, GPIO.FALLING)
    print("Woken")

    mode = getcurrentmode()
    print("Mode " + str(mode))

    if mode == AUTOMATIC:
        showstatus('green', 1)
    elif mode == MANUAL:
        showstatus('green', 2)
        timelapse()
    elif mode == TRANSFER:
        showstatus('green', 3)
    elif mode == SHUTDOWN:
        showstatus('red', 3)
        listening = False

        # Switch off lights
        enablelights(false)

        subprocess.call(['shutdown', '-h', 'now'], shell=False)