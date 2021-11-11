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
 - quality: Image quality for camera (0-100, PiCamera default is 85)
 - interval: TimeLapse interval in seconds
 - maximages: Maximum number of images to collect (-1 for unlimited)
 - folder: Destination folder for image sets - each run will create a subfolder containing a copy of the configuration file and all images
 - statuslight: Specify whether to use red/green status light (true/false)

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

# Read JSON config file and return as map
def readconfig(path):
    with open(path) as file:
        data = json.load(file)
    return data

# Set status light to red or green - does nothing if statuslight is false
def showstatus(color):
    global statuslight
    if statuslight:
        if color == "red":
            GPIO.output(26, GPIO.HIGH)
            GPIO.output(22, GPIO.LOW)
        elif color == "green":
            GPIO.output(26, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
        else:
            GPIO.output(26, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)

# If statuslight is true, setup GPIO pins for red/green LED and set to green
def initstatus(config):
    global statuslight
    if config['statuslight']:
        statuslight = True
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(26, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        showstatus("green")

# Return camera initialised using properties from config file - note that camera is already in preview
def initcamera(config):
    camera = PiCamera()
    camera.resolution = (config['imagewidth'], config['imageheight'])
    camera.brightness = config['brightness']
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
initstatus(config)
camera = initcamera(config)
foldername = initfolder(config, configfilename)
filesuffix = '-' + config['unitname'] + '-' + config['mode'] + '-' + str(config['interval']) + '.jpg'
interval = config['interval']
imagecount = config['maximages']
jpegquality = config['quality']

# Loop continues until maximum image count is reached or battery fails
print("Time series of " + (str(imagecount) if imagecount >= 0 else "unlimited") + " images at " + str(interval) + " second intervals")
while imagecount != 0:
    showstatus("red")
    camera.capture(os.path.join(foldername, datetime.today().strftime('%Y%m%d%H%M%S') + filesuffix), quality=jpegquality)
    showstatus("green")
    time.sleep(interval)
    imagecount -= 1