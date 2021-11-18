#!/usr/bin/env python3
"""
amt_util - Utility functions to support autonomous moth trap

 - loadconfig(filename = "amt_config.json") - load amt_config.json or specified JSON config files - returns config data as dictionary
 - selectpin(config, key, default, nullable = False) - return GPIO pin in BCM mode based on config file - returns pin number
 - selectadafruitpin(config, key, default) - return adafruit Pin based on config file - returns Pin object
 - initstatus(config) - set up status light based on config file - returns current state of light
 - showstatus(color, flashcount = 0) - set status light color or flash status light a number of times
 - converttz(time, from_zone, to_zone) - map datetime to specified timezone, returns modified datetime object
 - getsuntimes(latitude, longitude) - get sunrise and sunset for coming/present night from coordinates, returns two datetimes for sunset and sunrise, respectively
 - getlunarphase() - get current lunar phase as string, returns one of "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"

For more information see https://amt.hobern.net/.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.1"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
from dateutil import tz
from board import *
import RPi.GPIO as GPIO
import adafruit_dht
import math
import decimal
import json
import time

"""
Load configuration from a JSON file, with the following elements:

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

The default configuration file is amt_config.json in the current folder. An alternative may be identified as the first command line parameter. 
"""
def loadconfig(filename = None):
    if filename is None:
        filename = "amt_config.json"
    data = {}
    with open(filename) as file:
        data = json.load(file)
    return data 

"""
Validate config value for GPIO pin and return it or the default - if nullable, can return -1 to indicate not set
"""
def selectpin(config, key, default, nullable = False):
    if key in config:
        value = config[key]
        if value >= 2 and value <= 27:
            return value
        elif nullable and value == -1:
            return -1
    return default

"""
Validate config value for GPIO pin and return the adafruit Pin object for it or the default
"""
def selectadafruitpin(config, key, default):
    pin = selectpin(config, key, default)
    # adafruit_dht uses the CircuitPython board library to reference pins - this array is to select the correct board Pin object from a BCM integer
    adafruitpins = [None, None, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D25, D26, D27]
    return adafruitpins[pin]

"""
Default GPIO pins using BCM notation
"""
gpiogreen = 25
gpiored = 7

"""
Set up status light, returning current state as 'red', 'green' or 'off'
"""
def initstatus(config):
    global gpiogreen, gpiored

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    gpiogreen = selectpin(config, 'gpiogreen', gpiogreen)
    gpiored = selectpin(config, 'gpiored', gpiored)
    GPIO.setup(gpiogreen, GPIO.OUT)
    GPIO.setup(gpiored, GPIO.OUT)
    originalgreen = GPIO.input(gpiogreen)
    originalred = GPIO.input(gpiored)

    return 'red' if originalred > originalgreen else 'green' if originalgreen > originalred else 'off'

"""
Set status light color or flash status light in specified color
"""
def showstatus(color, flashcount = 0):
    global gpiogreen, gpiored

    red = GPIO.HIGH if color == 'red' else GPIO.LOW
    green = GPIO.HIGH if color == 'green' else GPIO.LOW

    if flashcount > 0:
        # Remember current setting
        currentred = GPIO.input(gpiored)
        currentgreen = GPIO.input(gpiogreen)

        # Ensure that the first flash is distinct
        if red == currentred and green == currentgreen and color != "off":
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.LOW)
            time.sleep(1)
        while flashcount > 0:
            GPIO.output(gpiored, red)
            GPIO.output(gpiogreen, green)
            time.sleep(1)
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.LOW)
            time.sleep(1)
            flashcount -= 1

        # Reset colour
        GPIO.output(gpiored, currentred)
        GPIO.output(gpiogreen, currentgreen)
    else:
        GPIO.output(gpiored, red)
        GPIO.output(gpiogreen, green)
    
"""
Convert datetime between timezones
"""
def converttz(time, from_zone, to_zone):
    time = time.replace(tzinfo=from_zone)
    return time.astimezone(to_zone)

"""
Return sunset and sunrise times in local timezone

Normally, this function is called after sunset (i.e. when the trap is running), but it
may be called before sunset (if the trap starts during daylight hours).

The key question is when the NEXT sunrise will occur. (If the trap runs and ends 
before sunset, this case can still be measured in relation to the coming night (as a 
negative offset).

The function therefore gets sunrise for the current date. If this time is prior to the 
current time, the function requests the sunrise time for the subsequent day. Ragardless,
it then requests the sunset time for the day before the sunrise time.

Returns sunsettime, sunrisetime
"""
def getsuntimes(latitude, longitude):
    sun = Sun(latitude, longitude)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    now = datetime.today().replace(tzinfo=to_zone)
    sunrise = converttz(sun.get_sunrise_time(), from_zone, to_zone)

    if now > sunrise:
        sunrise = converttz(sun.get_sunrise_time(now + timedelta(days=1)), from_zone, to_zone)

    sunset = converttz(sun.get_sunset_time(sunrise - timedelta(days=1)), from_zone, to_zone)

    return sunset, sunrise

"""
Return lunar phase
Author: Sean B. Palmer, inamidst.com
Cf. http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
"""
def getlunarphase():
    dec = decimal.Decimal
    now = datetime.now()

    diff = now - datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    pos = dec("0.20439731") + (days * dec("0.03386319269")) % dec(1)
    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)
    return {
        0: "New Moon", 
        1: "Waxing Crescent", 
        2: "First Quarter", 
        3: "Waxing Gibbous", 
        4: "Full Moon", 
        5: "Waning Gibbous", 
        6: "Last Quarter", 
        7: "Waning Crescent"
    }[int(index) & 7]

def main():
    sunset, sunrise = getsuntimes(-35.264, 149.084)
    print("Sunset: " + sunset.strftime('%Y%m%d-%H%M%S') + " Sunrise: " + sunrise.strftime('%Y%m%d-%H%M%S') + " Moon: " + getlunarphase())

# Run main
if __name__=="__main__": 
   main()