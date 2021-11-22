#!/usr/bin/env python3

import RPi.GPIO as GPIO
import subprocess
from amt_timelapse import timelapse
from amt_transfer import transferfiles
from amt_util import *
import signal
import logging
import sys

originalstatus = "off"

# Clean up after exception
def signal_handler(sig, frame):
    enablelights(False)
    logging.info("Caught signal - terminating")
    sys.exit(0)

# Handle errors gracefully
signal.signal(signal.SIGINT, signal_handler)

initlog("/home/pi/amt_modeselector.log")
logging.info("##########################")
logging.info("amt_modeselector.py BEGIN")

# Optionally override default configuration file
if len(sys.argv) > 1:
    logging.info("Config file: " + sys.argv[1])
    config = loadconfig(sys.argv[1])
else:
    config = loadconfig()

initboard(config)
originalstatus = initstatus()
showstatus('green', 3)

listening = True
while listening:

    logging.info("Sleeping")
    GPIO.wait_for_edge(gpiotrigger, GPIO.FALLING)
    logging.info("Woken")

    mode = getcurrentmode()
    logging.info("Mode " + modenames[mode])

    if mode == AUTOMATIC:
        showstatus('green', 1, 1.5)
    elif mode == MANUAL:
        showstatus('green', 2)
        timelapse()
    elif mode == TRANSFER:
        showstatus('red')
        transferfiles()
        showstatus(originalstatus)
    elif mode == SHUTDOWN:
        showstatus('red', 3)
        listening = False

        # Switch off lights
        enablelights(False)
        showstatus('off')

        subprocess.call(['shutdown', '-h', 'now'], shell=False)