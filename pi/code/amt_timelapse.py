#!/usr/bin/env python3
"""
amt_timelapse - Collect Autonomous Moth Trap images on time lapse

Captures a series of images and saves these with configuration metadata. Intended for use on a Raspberry Pi running as an automonous moth trap. For more information see https://amt.hobern.net/.

Configuration is provided via a JSON file, with the following elements:

 - unitname: Unique identifier for the current AMT unit - should only include characters that can be used in a filename
 - processor: Purely to document for future users (e.g. "Raspberry Pi Zero W")
 - camera: Purely to document for future users (e.g. "Raspberry Pi HQ + 6mm Wide Angle Lens")
 - operatingdistance: Purely to document the operating distance of the camera from the illuminated surface, in mm
 - mothlight: Purely to document for future users (e.g. "High-power LED tube: 4 UV, 1 green, 1 blue")
 - illumination: Purely to document for future users (e.g. "10-inch ring light")
 - mode: The operating mode, currently only "TimeLapse" is supported
 - imagewidth: Image width for camera resolution in pixels
 - imageheight: Image height for camera resolution in pixels
 - brightness: Image brightness for camera (0-100, PiCamera default is 50)
 - contrast: Image contrast for camera (-100-100, PiCamera default is 0)
 - saturation: Image saturation for camera (-100-100, PiCamera default is 0)
 - sharpness: Image sharpness for camera (-100-100, PiCamera default is 0)
 - quality: Image quality for camera (0-100, PiCamera default is 85)
 - interval: Time lapse interval in seconds
 - initialdelay: Delay in seconds between enabling lights and DHT22 sensor before capturing images
 - maximages: Maximum number of images to collect (-1 for unlimited)
 - folder: Destination folder for image sets - each run will create a subfolder containing a copy of the configuration file and all images
 - statuslight: Specify whether to use red/green status light (true/false, defaults to false)
 - envsensor: Specify whether to use DHT11/DHT22 temperature/humidity sensor (one of "DHT22", "DHT11", "None")
 - gpiogreen = Raspberry Pi GPIO pin for green side of red/green GPIO pin in BCM mode (default 25)
 - gpiored = Raspberry Pi GPIO pin for red side of red/green GPIO pin in BCM mode (default 7)
 - gpiolights = Raspberry Pi GPIO pin for activating lights in BCM mode (default 26)
 - gpioenvsensorpower = Raspberry Pi GPIO pin for enabling 3.3V power to temperature/humidity sensor in BCM mode (default 10) - use -1 for power not from GPIO pin
 - gpioenvsensordata = Raspberry Pi GPIO pin for temperature/humidity sensor data in BCM mode (default 9)

The default configuration file is amt_config.json in the current folder. An alternative may be identified as the first command line parameter. Whichever configuration file is used, a copy is saved with the captured images.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.2"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

from amt_config import *
from amt_util import *
from picamera import PiCamera
import time
from datetime import datetime
from shutil import copyfile
import os
import RPi.GPIO as GPIO
import sys
import signal
import pigpio
import logging
import socket

# Current mode
manual = False

# Only enable status light if specified in configuration file
statuslight = False

# Only enable sensor if specified in configuration file
envsensor = None
dht = None

# Object in pigpio to represent board
pi = None

# To remember state of status light before execution
originalstatus = "off"

# Check whether specified manual setting (still) matches the user selection
def modestillvalid(manual):
    return (manual == (getcurrentmode() == MANUAL))

# Store additional metadata in config dictionary
def addmetadata(config):
    global manual
    unitname = config.get(CAPTURE_UNITNAME, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if unitname is None:
        config.set(CAPTURE_UNITNAME, socket.gethostname(), SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    latitude = config.get(EVENT_LATITUDE, SECTION_EVENT)
    longitude = config.get(EVENT_LONGITUDE, SECTION_EVENT)
    if latitude is not None and longitude is not None:
        getsuntimes(config, latitude, longitude)
    config.set(EVENT_LUNARPHASE, getlunarphase(), SECTION_EVENT)
    config.set(CAPTURE_PROGRAM, " ".join(sys.argv), SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    config.set(CAPTURE_VERSION, __version__, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    config.set(CAPTURE_TRIGGER, "Manual" if manual else "Automatic", SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    return config

# Enable GPIO control and, if appropriate, enable status light, sensor and main lights
def initoperation(config):
    global statuslight, envsensor, gpiogreen, gpiored, gpiolights, gpioenvsensorpower, gpioenvsensordata, originalstatus

    # Set up the mode pins
    initboard(config)

    # Set up status light and store original color
    originalstatus = initstatus()

    statuslight = config.get(CAPTURE_STATUSLIGHT, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if statuslight:
        showstatus("green")

    envsensor = config.get(CAPTURE_ENVSENSOR, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if envsensor not in ["DHT22", "DHT11"]:
        envsensor = None

# Turn sensor on or off if enabled
def enablesensor(activate):
    global envsensor, gpioenvsensorpower, gpioenvsensordata, dht, pi

    if envsensor is not None:
        if activate:
            # Power may be hardwired (gpioenvsensorpower == -1)
            if gpioenvsensorpower > 0:
                logging.info("Enabling " + envsensor + " sensor power")
                GPIO.output(gpioenvsensorpower, GPIO.HIGH)
            pi = pigpio.pi()
            try:
                if envsensor == "DHT22":
                    dht = DHT.sensor(pi, gpioenvsensordata, DHT.DHTXX)
                elif envsensor == "DHT11":
                    dht = DHT.sensor(pi, gpioenvsensordata, DHT.DHT11)
                logging.info("Sensor enabled")
            except:
                logging.error("Could not initialise sensor")
                pi.stop()
                pi = None
                dht = None

        else:
            if dht is not None:
                dht.cancel()
                pi.stop()
            if gpioenvsensorpower > 0:
                GPIO.output(gpioenvsensorpower, GPIO.LOW)
            logging.info("Sensor disabled")

# Return camera initialised using properties from config file - note that camera is already in preview when returned
def initcamera(config):
    camera = PiCamera()
    camera.resolution = (config.get(CAPTURE_IMAGEWIDTH, SECTION_PROVENANCE, SUBSECTION_CAPTURE), config.get(CAPTURE_IMAGEHEIGHT, SECTION_PROVENANCE, SUBSECTION_CAPTURE))
    brightness = config.get(CAPTURE_BRIGHTNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if brightness is not None:
        camera.brightness = brightness
    contrast = config.get(CAPTURE_CONTRAST, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if contrast is not None:
        camera.contrast = contrast
    saturation = config.get(CAPTURE_SATURATION, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if saturation is not None:
        camera.saturation = saturation
    sharpness = config.get(CAPTURE_SHARPNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if sharpness is not None:
        camera.sharpness = sharpness
    awb_mode = config.get(CAPTURE_AWBMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if awb_mode is not None:
        camera.awb_mode = awb_mode
    meter_mode = config.get(CAPTURE_METERMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if meter_mode is not None:
        camera.meter_mode = meter_mode
    awb_gains = config.get(CAPTURE_AWBGAINS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if awb_gains is not None and isinstance(awb_gains, list) and len(awb_gains) == 2:
        camera.awb_gains = awb_gains
    camera.start_preview()
    logging.info("Camera initialised")
    return camera

# Create target folder for this run and make a copy of the current configfile to allow future interpretation
def initfolder(config):
    folder = config.get(CAPTURE_FOLDER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    timestamp = datetime.today().strftime('%Y%m%d-%H%M%S')
    foldername = os.path.join(folder, timestamp)
    os.mkdir(foldername)
    config.dump(os.path.join(foldername, CONFIG_METADATA))
    logging.info("Output folder created: " + foldername)
    return foldername

# Return string with temperature and humidity encoded or empty string otherwise
def readsensor():
    global dht, envsensor

    if dht is not None:
        datum = dht.read()
        if datum[2] == 0:
            return "-TempC_" + str(datum[3]) + "-Humid_" + str(datum[4])
        else:
            logging.error(envsensor + " sensor returned " + ["DHT_GOOD", "DHT_BAD_CHECKSUM", "DHT_BAD_DATA", "DHT_TIMEOUT"][datum[2]])

    return ""

# Clean up after exception
def signal_handler(sig, frame):
    enablelights(False)
    enablesensor(False)
    showstatus(originalstatus)
    logging.error("Caught signal - terminating")
    sys.exit(0)

# Main body - initialise, run and clean up
def timelapse(manuallytriggered = False):
    global manual
    manual = manuallytriggered

    # If triggered as manual, leave logging to the calling module
    if not manual:
        initlog("amt_timelapse.log")

    logging.info("######################")
    logging.info("amt_timelapse.py BEGIN")

    # Handle errors gracefully
    signal.signal(signal.SIGINT, signal_handler)

    # Optionally override default configuration file
    if len(sys.argv) > 1:
        configfilename = sys.argv[1]
        logging.info("Settings file: " + configfilename)
    else:
        configfilename = None

    # Initialise from config settings
    config = addmetadata(AmtConfiguration(True, configfilename))
    interval = config.get(CAPTURE_INTERVAL, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    imagecount = config.get(CAPTURE_MAXIMAGES, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if imagecount is None:
        imagecount = -1
    jpegquality = config.get(CAPTURE_QUALITY, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    labeltext = '-{}-{}-{}'.format(config.get(CAPTURE_UNITNAME, SECTION_PROVENANCE, SUBSECTION_CAPTURE), config.get(CAPTURE_MODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE), str(interval))
    logging.info("Quality: " + str(jpegquality))
    initoperation(config)

    # If mode is manual, the system should already be running. If this is a main execution, the script has been triggered by cron or from a shell - do not operate while manual is set.
    if not modestillvalid(manual):
        logging.info("Execution mode does not match current user setting - terminate immediately")
        exit(0)

    addmetadata(config)
    foldername = initfolder(config)
    enablelights(True)
    if envsensor is not None:
        enablesensor(True)
        logging.info(envsensor + " sensor enabled")

    # If specified, wait before imaging
    initialdelay = config.get(CAPTURE_INITIALDELAY, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if initialdelay is not None:
        logging.info("Initial delay: " + str(initialdelay) + " seconds")
        if modestillvalid(manual):
            for i in range(initialdelay):
                time.sleep(1)
                if not modestillvalid(manual):
                    logging.info("Mode change - aborting timelapse")
                    break
        else:
            time.sleep(initialdelay)

    if modestillvalid(manual):
        camera = initcamera(config)

        # Loop continues until maximum image count is reached or battery fails
        if manual:
            logging.info("Time series of images at " + str(interval) + " second intervals")
        else: 
            logging.info("Time series of " + (str(imagecount) if imagecount >= 0 else "unlimited") + " images at " + str(interval) + " second intervals")

        while modestillvalid(manual) and (manual or (not manual and imagecount > 0)):
            if statuslight:
                showstatus("red")
            camera.capture(os.path.join(foldername, datetime.today().strftime('%Y%m%d%H%M%S') + labeltext + readsensor() + '.jpg'), format = "jpeg", quality = jpegquality)
            if statuslight:
                showstatus("green")
            time.sleep(interval)
            imagecount -= 1

        logging.info("Time series complete")

        calibration = config.get(CAPTURE_CALIBRATION, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
        if calibration is not None:
            calibratecamera(camera, calibration.split(','), os.path.join(foldername, "calibration"), config)

        camera.close()

    # If the loop terminates, power down lights and sensor
    enablelights(False)
    enablesensor(False)
    showstatus(originalstatus)
    logging.info("amt_timelapse.py END")

# Run main
if __name__=="__main__":
   timelapse()
