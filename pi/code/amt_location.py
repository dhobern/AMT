#!/usr/bin/env python3
"""
amt_location - Initiate GPS sensor, read location and log in config files

Intended for use on a Raspberry Pi running as an automonous moth trap. For more information see https://amt.hobern.net/.

Configuration is provided via one or more YAML files (see amt_config.py). The following properties are used by amt_location.py:

 - provenance
   - capture
     - gpiogpspower - GPIO pin number (BCM mode) for switching GPS sensor on (HIGH for on) or null if GPS sensor power source is fixed

This module makes calls to other modules which make use of additional properties - see the comments in each module.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import io
import time
import pynmea2
import serial
import RPi.GPIO as GPIO
import statistics
import math
import os
import termios
from datetime import datetime
from dateutil import tz
from amt_config import *
import amt_util
import logging

"""
Get GPS coordinates (minimising power consumption) and save these in YAML files 
as part of the event metadata.

Since this operation is asynchronous, existingruns is a list of preexisting 
data capture runs in the capture folder. If any new runs are started (adding 
runs to this folder) while coordinates are being collected, ensure that the 
metadata files in these folders are also updated
"""
def getlocation(config, previousruns):

    logging.info("getlocation BEGIN")

    try:
        # Power to GPS may be controlled by setting a GPIO pin to high
        enablepower = False
        gpspowerpin = config.get(CAPTURE_GPIOGPSPOWER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
        if gpspowerpin is not None and gpspowerpin > 0:
            enablepower = True
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gpspowerpin, GPIO.OUT)
            GPIO.output(gpspowerpin, GPIO.HIGH)
            logging.info("GPS power enabled")
            time.sleep(5)

        # Continue until at least maxiteration exceptions have been caught or the target number
        # of readings is achieved. 
        iteration = 0
        maxiterations = 20
        lats = []
        lons = []
        targetreadings = 20

        while len(lats) < targetreadings and iteration < maxiterations:
            try:
                with serial.Serial('/dev/ttyS0', 9600, timeout=5.0) as ser:
                    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
                    while len(lats) < targetreadings:
                        try:
                            line = sio.readline()
                            word = str(line)[0:6]
                            if 'GGA' in word:
                                msg = pynmea2.parse(line)
                                if msg.gps_qual > 0:
                                    lats.append(float(msg.latitude))
                                    lons.append(float(msg.longitude))
                        except serial.SerialException as e:
                            iteration += 1
                            logging.error("getlocation caught SerialException - restarting")
                            break
                        except pynmea2.ParseError as e:
                            logging.error("getlocation caught ParseError")
                            continue
                        except termios.error as e:
                            logging.error("getlocation caught termios.error")
                            continue
            except Exception as e:
                logging.error("getlocation caught unhandled Exception - restarting")
                iteration += 1
                continue

        if enablepower:
            GPIO.output(gpspowerpin, GPIO.LOW)
            logging.info("GPS power disabled")

        if len(lats) > 0:
            latitude = round(statistics.mean(lats), 6)
            longitude = round(statistics.mean(lons), 6)
            if len(lats) > 10:
                sdlatitude = statistics.stdev(lats)
                sdlongitude = statistics.stdev(lons)
                # Accuracy calculated by taking the hypoteneuse of the two standard deviations, multiplying by 1.96 to get ~95% interval and then converting to metres 
                uncertainty = int(math.sqrt(sdlongitude**2 + sdlatitude**2) * 1.96 * 111139)
                if uncertainty < 1:
                    uncertainty = 1
            else:
                uncertainty = 100

            locationfile = os.path.join(CONFIGURATION_FOLDER, CONFIG_LOCATION)
            savelocation(locationfile, latitude, longitude, uncertainty, "WGS84")
            logging.info("Latitude: {} Longitude: {} Uncertainty: {}".format(latitude, longitude, uncertainty))

            if previousruns is not None:
                time.sleep(5)
                capturefolder = config.get(CAPTURE_FOLDER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
                if os.path.isdir(capturefolder):
                    currentruns = os.listdir(capturefolder)
                    if currentruns:
                        for run in currentruns:
                            if run not in previousruns:
                                logging.info("Updating location for run " + run)
                                metadatafile = os.path.join(capturefolder, run, CONFIG_METADATA)
                                if not os.path.isfile(metadatafile):
                                    time.sleep(5)
                                if os.path.isfile(metadatafile):
                                    metadata = AmtConfiguration(metadatafile)
                                    metadata.add(locationfile)
                                    amt_util.getsuntimes(metadata, latitude, longitude)
                                    metadata.dump(metadatafile)
    
        else:
            logging.error("Could not get GPS read ({} reads, {} errors)".format(len(lats), iteration))

    except Exception:
        logging.exception("Caught exception in getlocation") 
        pass

    logging.info("getlocation END")

def savelocation(filename, latitude, longitude, uncertainty = None, datum = None):
    locationvalues = AmtConfiguration()
    locationvalues.set(EVENT_LATITUDE, latitude, SECTION_EVENT)
    locationvalues.set(EVENT_LONGITUDE, longitude, SECTION_EVENT)
    locationvalues.set(EVENT_COORDINATETIMESTAMP, datetime.today().replace(tzinfo=tz.tzlocal()).isoformat(), SECTION_EVENT)
    if uncertainty is not None:
        locationvalues.set(EVENT_COORDINATEUNCERTAINTY, uncertainty, SECTION_EVENT)
    if datum is not None:
        locationvalues.set(EVENT_GEODETICDATUM, datum, SECTION_EVENT)
    locationvalues.dump(filename)
    return locationvalues
