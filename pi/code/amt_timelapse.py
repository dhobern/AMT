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
 - mode: The operating model, currently only "TimeLapse" is supported
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
 - sensortype: Specify whether to use DHT11/DHT22 temperature/humidity sensor (one of "DHT22", "DHT11", "None")
 - gpiogreen = Raspberry Pi GPIO pin for green side of red/green GPIO pin in BCM mode (default 25)
 - gpiored = Raspberry Pi GPIO pin for red side of red/green GPIO pin in BCM mode (default 7)
 - gpiolights = Raspberry Pi GPIO pin for activating lights in BCM mode (default 26)
 - gpiosensorpower = Raspberry Pi GPIO pin for enabling 3.3V power to temperature/humidity sensor in BCM mode (default 10) - use -1 for power not from GPIO pin
 - gpiosensordata = Raspberry Pi GPIO pin for temperature/humidity sensor data in BCM mode (default 9)

The default configuration file is amt_timelapse.json in the current folder. An alternative may be identified as the first command line parameter. Whichever configuration file is used, a copy is saved with the captured images.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.1"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

from picamera import PiCamera
import time
from datetime import datetime
from shutil import copyfile
import os
import RPi.GPIO as GPIO
import sys
import signal
import json
from board import *
import adafruit_dht
import logging

# Common utility functions
from amt_util import *

# Only enable status light if specified in configuration file
statuslight = False

# Only enable sensor if specified in configuration file
sensortype = None
sensor = None

# GPIO pins - these may be varied within the configuration file - all use BCM notation
gpiolights = 26
gpiosensorpower = 10
gpiosensordata = 9

originalstatus = "off"

# Store additional metadata in config dictionary
def addmetadata(config):
    if "latitude" in config and "longitude" in config and config["latitude"] is not None and config["longitude"] is not None:
        sunset, sunrise = getsuntimes(config["latitude"], config["longitude"])
        config["sunset"] = sunset.isoformat()
        config["sunrise"] = sunrise.isoformat()
    config["lunarphase"] = getlunarphase()
    config["program"] = " ".join(sys.argv)
    config["version"] = __version__
    return config 

# Enable GPIO control and, if appropriate, enable status light, sensor sensor and main lights
def initgpio(config):
    global statuslight, sensortype, gpiogreen, gpiored, gpiolights, gpiosensorpower, gpiosensordata, originalstatus

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Set up status light and store original color
    originalstatus = initstatus(config)

    if 'statuslight' in config and config['statuslight']:
        statuslight = True
        showstatus("green")

    if 'sensortype' in config and config['sensortype'] in ["DHT22", "DHT11"]:
        sensortype = config['sensortype']
        # After this call, gpiosensordata holds an adafruit Pin object
        gpiosensordata = selectadafruitpin(config, 'gpiosensordata', gpiosensordata)
        # Allow -1 for power pin if attached directly to voltage pin
        gpiosensorpower = selectpin(config, 'gpiosensorpower', gpiosensorpower, True)
        if gpiosensorpower > 0:
            GPIO.setup(gpiosensorpower, GPIO.OUT)
        
    gpiolights = selectpin(config, 'gpiolights', gpiolights)
    GPIO.setup(gpiolights, GPIO.OUT)
    logging.info("GPIO pins enabled")

# Turn lights on or off
def enablelights(activate):
    global gpiolights

    GPIO.output(gpiolights, GPIO.HIGH if activate else GPIO.LOW)
    logging.info("Lights enabled" if activate else "Lights disabled")

# Turn sensor sensor on or off if enabled
def enablesensor(activate):
    global sensortype, gpiosensorpower, gpiosensordata, sensor

    if sensortype is not None:
        # Power may be hardwired (gpiosensorpower == -1)
        if gpiosensorpower > 0:
            GPIO.output(gpiosensorpower, GPIO.HIGH if activate else GPIO.LOW)
        if activate:
            if sensortype == "DHT22":
                sensor = adafruit_dht.DHT22(gpiosensordata, use_pulseio=False)
            elif sensortype == "DHT11":
                sensor = adafruit_dht.DHT11(gpiosensordata, use_pulseio=False)
            logging.info("Sensor enabled")
        else:
            logging.info("Sensor disabled")

# Return camera initialised using properties from config file - note that camera is already in preview when returned
def initcamera(config):
    camera = PiCamera()
    camera.resolution = (config['imagewidth'], config['imageheight'])
    if 'brightness' in config:
        camera.brightness = config['brightness']
    if 'contrast' in config:
        camera.contrast = config['contrast']
    if 'saturation' in config:
        camera.saturation = config['saturation']
    if 'sharpness' in config:
        camera.sharpness = config['sharpness']
    camera.start_preview()
    logging.info("Camera initialised")
    return camera

# Create target folder for this run and make a copy of the current configfile to allow future interpretation
def initfolder(config):
    if not os.path.isdir(config['folder']):
        os.mkdir(config['folder'])
    timestamp = datetime.today().strftime('%Y%m%d-%H%M%S')
    foldername = os.path.join(config['folder'], timestamp)
    os.mkdir(foldername)
    json.dump(config, open(os.path.join(foldername, "amt_metadata.json"), "w"), indent = 4)
    logging.info("Output folder created: " + foldername)
    return foldername

def readsensor():
    global sensor

    if sensor is not None:
        try:
            temperature = sensor.temperature
            humidity = sensor.humidity
            if temperature is not None and humidity is not None:
                return "-TempC_" + str(temperature) + "-Humid_" + str(humidity)
        except RuntimeError:
            print("Failed to read sensor")

    return ""

# Clean up after exception
def signal_handler(sig, frame):
    enablelights(False)
    enablesensor(False)
    showstatus(originalstatus)
    logging.error("Caught signal - terminating")
    sys.exit(0)

# Main body - initialise, run and clean up
def main():
    global configfilename

    # Initalise log
    logging.basicConfig(filename="amt_timelapse.log", format='%(asctime)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S', level = logging.INFO)
    logging.info("######################")
    logging.info("amt_timelapse.py BEGIN")

    # Handle errors gracefully
    signal.signal(signal.SIGINT, signal_handler)

    # Optionally override default configuration file
    if len(sys.argv) > 1:
        configfilename = sys.argv[1]
    logging.info("Config file: " + configfilename)

    # Initialise from config settings
    config = loadconfig(configfilename)
    addmetadata(config)
    labeltext = '-' + config['unitname'] + '-' + config['mode'] + '-' + str(config['interval'])
    interval = config['interval']
    imagecount = config['maximages']
    jpegquality = config['quality']
    foldername = initfolder(config)
    initgpio(config)
    enablelights(True)
    if sensortype is not None:
        enablesensor(True)
        logging.info(sensortype + " sensor enabled")

    # If specified, wait before imaging
    if config['initialdelay'] is not None:
        logging.info("Initial delay: " + str(config['initialdelay']) + " seconds")
        time.sleep(config['initialdelay'])

    camera = initcamera(config)

    # Loop continues until maximum image count is reached or battery fails
    logging.info("Time series of " + (str(imagecount) if imagecount >= 0 else "unlimited") + " images at " + str(interval) + " second intervals")

    while imagecount != 0:
        if statuslight:
            showstatus("red")
        camera.capture(os.path.join(foldername, datetime.today().strftime('%Y%m%d%H%M%S') + labeltext + readsensor() + '.jpg'), quality=jpegquality)
        if statuslight:
            showstatus("green")
        time.sleep(interval)
        imagecount -= 1

    logging.info("Time series complete")

    # If the loop terminates, power down lights and sensor
    enablelights(False)
    enablesensor(False)
    showstatus(originalstatus)
    logging.info("amt_timelapse.py END")

# Run main
if __name__=="__main__": 
   main()