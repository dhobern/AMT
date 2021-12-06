#!/usr/bin/env python3
"""
amt_modeselector - Set up autonomous moth trap and watch for user requests

Intended for use on a Raspberry Pi running as an automonous moth trap. For more information see https://amt.hobern.net/.

Configuration is provided via one or more YAML files (see amt_config.py). The following properties are used by amt_modeselector.py:

 - provenance
   - capture
     - gpssensor - Null if no GPS sensor is present, otherwise a model name (free-text)
     - folder - Location of any past or future subfolders documenting trap runs - if any are added during coordinate collection, update the metadata

This module makes calls to other modules which make use of additional properties - see the comments in each module.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import RPi.GPIO as GPIO
import subprocess
from amt_timelapse import timelapse
from amt_transfer import transferfiles
from amt_location import getlocation, savelocation
from amt_util import *
from amt_config import *
import signal
import logging
import threading
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

# Optionally override default runtime configuration file
if len(sys.argv) > 1:
    logging.info("Config file: " + sys.argv[1])
    config = AmtConfiguration(True, sys.argv[1])
else:
    config = AmtConfiguration(True)

config.dump()

# If GPS present, spawn thread to get coordinates
if config.get(CAPTURE_GPSSENSOR, SECTION_PROVENANCE, SUBSECTION_CAPTURE) is not None:
    logging.info("Starting getlocation")
    capturefolder = config.get(CAPTURE_FOLDER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    previousruns = os.listdir(capturefolder)
    savelocation(os.path.join(CONFIGURATION_FOLDER, CONFIG_LOCATION), "NOT RECORDED", "NOT RECORDED")
    gpsthread = threading.Thread(target = getlocation, args = (config, previousruns))
    gpsthread.start()

initboard(config)
originalstatus = initstatus()
showstatus('green', 3)
enablelights(False)

gpiotrigger = config.get(CAPTURE_GPIOMODETRIGGER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)

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
        try:
            timelapse(True)
        except Exception as exc:
            logging.exception("Caught exception in timelapse")
    elif mode == TRANSFER:
        showstatus('red')
        try:
            transferfiles()
        except Exception as exc:
            logging.error("Caught exception in transferfiles")
        showstatus(originalstatus)
    elif mode == SHUTDOWN:
        showstatus('red', 3)
        listening = False

        # Switch off lights
        enablelights(False)
        showstatus('off')

        subprocess.call(['sudo', 'shutdown', '-h', 'now'], shell=False)