#!/usr/bin/env python
"""
TimeLapse.py - Collect Autonomous Moth Trap images on time lapse

Captures a series of images and saves these with configuration metadata. Intended for use on a Raspberry Pi running as an automonous moth trap. For more information see https://amt.hobern.net/.

Configuration is provided via a JSON file, with the following elements:

 - unitname: Unique identifier for the current AMT unit - should only include characters that can be used in a filename
 - processor: Purely to document for future users (e.g. "Raspberry Pi Zero W")
 - camera: Purely to document for future users (e.g. "Raspberry Pi HQ + 6mm Wide Angle Lens")
 - operatingdistance: Purely to document the operating distance of the camera from the illuminated surface, in mm
 - mothlight: Purely to document for future users (e.g. "High-power LED tube: 4 UV, 1 green, 1 blue")
 - illumination: Purely to document for future users (e.g. "10-inch ring light")
 - mode: The operating model, one of "TimeLapse" or "Motion" (at present this script only supports TimeLapse)
 - imagewidth: Image width for camera resolution in pixels
 - imageheight: Image height for camera resolution in pixels
 - brightness: Image brightness for camera (0-100, PiCamera default is 50)
 - contrast: Image contrast for camera (-100-100, PiCamera default is 0)
 - saturation: Image saturation for camera (-100-100, PiCamera default is 0)
 - sharpness: Image sharpness for camera (-100-100, PiCamera default is 0)
 - quality: Image quality for camera (0-100, PiCamera default is 85)
 - interval: TimeLapse interval in seconds
 - initialdelay: Delay in seconds between enabling lights and DHT22 sensor before capturing images
 - maximages: Maximum number of images to collect (-1 for unlimited)
 - folder: Destination folder for image sets - each run will create a subfolder containing a copy of the configuration file and all images
 - statuslight: Specify whether to use red/green status light (true/false, defaults to false)
 - dht22: Specify whether to use DHT22 temperature/humidity sensor (true/false, defaults to false)
 - gpiogreen = Raspberry Pi GPIO pin for green side of red/green GPIO pin in BOARD mode (default 22)
 - gpiored = Raspberry Pi GPIO pin for red side of red/green GPIO pin in BOARD mode (default 26)
 - gpiolights = Raspberry Pi GPIO pin for activating lights in BOARD mode (default 37)
 - gpiodht22power = Raspberry Pi GPIO pin for enabling 3.3V power to DHT22 temperature/humidity sensor in BOARD mode (default 19)
 - gpiodht22data = Raspberry Pi GPIO pin for DHT22 temperature/humidity sensor data in BOARD mode (default 21)
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "1.0.0"
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
import json

# Default configuration file location - can be overridden on command line
configfilename = "/home/pi/AMT_config.json"

# Only enable status light if specified in configuration file
statuslight = False

# Only enable dht22 sensor if specified in configuration file
dht22 = False

# GPIO pins
gpiogreen = 22
gpiored = 26
gpiolights = 37
gpiodht22power = 19
gpiodht22data = 21

# Read JSON config file and return as map
def readconfig(path):
    with open(path) as file:
        data = json.load(file)
    return data

# Enable GPIO control and, if appropriate, enable status light, dht22 sensor and main lights
def initgpio(config):
    global statuslight, dht22, gpiogreen, gpiored, gpiolights, gpiodht22power, gpiodht22data

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    if 'statuslight' in config:
        statuslight = True
        if 'gpiogreen' in config:
            gpiogreen = config['gpiogreen']
        if 'gpiored' in config:
            gpiored = config['gpiored']
        GPIO.setup(gpiogreen, GPIO.OUT)
        GPIO.setup(gpiored, GPIO.OUT)
        showstatus("green")

    if 'dht22' in config:
        dht22 = True
        if 'gpiodht22power' in config:
            gpiodht22power = config['gpiodht22power']
        if 'gpiodht22data' in config:
            gpiodht22data = config['gpiodht22data']
        GPIO.setup(gpiodht22power, GPIO.OUT)
        # TODO setup data
        
    if 'gpiolights' in config:
        gpiolights = config['gpiolights']
    GPIO.setup(gpiolights, GPIO.OUT)

# Set status light to red or green - does nothing if statuslight is false
def showstatus(color):
    global statuslight, gpiogreen, gpiored

    if statuslight:
        if color == "red":
            GPIO.output(gpiored, GPIO.HIGH)
            GPIO.output(gpiogreen, GPIO.LOW)
        elif color == "green":
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.HIGH)
        else:
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.LOW)

# Turn lights on or off
def initlights(activate):
    global gpiolights

    GPIO.output(gpiolights, GPIO.HIGH if activate else GPIO.LOW)

# Turn dht22 sensor on or off if enabled
def initdht22(activate):
    global dht22, gpiodht22power

    if dht22:
        GPIO.output(gpiodht22power, GPIO.HIGH if activate else GPIO.LOW)

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
    return camera

# Create target folder for this run and make a copy of the current configfile to allow future interpretation
def initfolder(config, configfile):
    if not os.path.isdir(config['folder']):
        os.mkdir(config['folder'])
    timestamp = datetime.today().strftime('%Y%m%d-%H%M%S')
    foldername = os.path.join(config['folder'], timestamp)
    os.mkdir(foldername)
    slashoffset = configfile.rfind("/")
    if slashoffset >= 0:
        filename = configfile[slashoffset + 1:]
    else:
        filename = configfile
    extensionoffset = filename.rfind(".")
    if extensionoffset >= 0:
        configcopy = os.path.join(foldername, filename[0:extensionoffset] + "-" + timestamp + filename[extensionoffset:])
    else:
        configcopy = os.path.join(foldername, filename + "-" + timestamp)
    print("Copying configuration to " + configcopy)
    copyfile(configfile, configcopy)
    return foldername

### Main body ###

# Optionally override default configuration file
if len(sys.argv) > 1:
    configfilename = sys.argv[1]

# Initialise from config settings
config = readconfig(configfilename)
filesuffix = '-' + config['unitname'] + '-' + config['mode'] + '-' + str(config['interval']) + '.jpg'
interval = config['interval']
imagecount = config['maximages']
jpegquality = config['quality']
foldername = initfolder(config, configfilename)
initgpio(config)
initlights(True)
initdht22(True)

# If specified, wait before imaging
if config['initialdelay'] is not None:
    time.sleep(config['initialdelay'])

camera = initcamera(config)

# Loop continues until maximum image count is reached or battery fails
print("Time series of " + (str(imagecount) if imagecount >= 0 else "unlimited") + " images at " + str(interval) + " second intervals")
while imagecount != 0:
    showstatus("red")
    camera.capture(os.path.join(foldername, datetime.today().strftime('%Y%m%d%H%M%S') + filesuffix), quality=jpegquality)
    showstatus("green")
    time.sleep(interval)
    imagecount -= 1

# If the loop terminates, power down lights and dht22
initlights(False)
initdht22(False)

exit(0)