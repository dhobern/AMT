#!/usr/bin/env python3
"""
amt_util - Utility functions to support autonomous moth trap

 - selectpin(config, key, default, nullable = False) - return GPIO pin in BCM mode based on config file - returns pin number
 - initstatus(config) - set up status light based on config file - returns current state of light
 - initboard(config) - set up all GPIO pins
 - getcurrentmode() - get current setting of rotary switch used to indicate current mode
 - enablelights(activate) - switch uv light and ringlight on or off
 - initstatus() - set up status lights
 - showstatus(color, flashcount = 0, flashlength = 0.2) - set colour of status light or flash light one or more times
 - converttz(time, from_zone, to_zone) - asdjust datetime timezone
 - getsuntimes(config, latitude, longitude, querytime = None) - get sunset and sunrise for current night
 - getlunarphase() - get lunar phase as string
 - initlog(name) - start logging messages
 - rotatelogs(name, count = 5) - rotate log files
 - calibratecamera(camera, series, calibrationfolder, config) - capture one or more series of calibration images for different camera settings (all varying from the configured settings)

For more information see https://amt.hobern.net/.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.3"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
from dateutil import tz
from amt_config import *
import RPi.GPIO as GPIO
import math
import decimal
import time
import logging
import subprocess
import os
from picamera import PiCamera

"""
Validate config value for GPIO pin (from PROVENANCE/CAPTURE and return it or the default - if nullable, can return -1 to indicate not set
"""
def selectpin(config, key, default, nullable = False):
    value = config.get(key, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if value is not None:
        if value >= 2 and value <= 27:
            return value
        elif nullable and value == -1:
            return -1
    return default

"""
Default GPIO pins using BCM notation - in case configuration is defective
"""
gpiogreen = 25
gpiored = 7
gpiomanual = 22
gpiotransfer = 27
gpioshutdown = 17
gpiolights = 26
gpioenvsensorpower = 10
gpioenvsensordata = 9
gpiogpssensorpower = 24
gpiotrigger = 16

"""
Modes for operation of unit (managed by amt_modeselector.py)
 - AUTOMATIC - Normal operation awaiting crontab execution of amt_timelapse.py.
 - MANUAL - Push of momentary button will start amt_timelapse.py. Timelapse will end if user switches away from MANUAL.
 - TRANSFER - Push of momentary button will start amt_transfer.py. Control will not return until this is complete.
 - SHUTDOWN - Push of momentary button will trigger shutdown of unit.
"""
AUTOMATIC = 0
MANUAL = 1
TRANSFER = 2
SHUTDOWN = 3

modenames = ["Automatic", "Manual", "Transfer", "Shutdown"]

"""
Set up the pins, using values from configuration or defaults otherwise
"""
def initboard(config):
    global gpiogreen, gpiored, gpiomanual, gpiotransfer, gpioshutdown, gpiolights, gpioenvsensordata, gpioenvsensorpower, gpiogpssensorpower, gpiotrigger

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Pins linked to three posts in rotary switch - each indicates a different mode to trigger via the momentary button
    gpiomanual = selectpin(config, CAPTURE_GPIOMANUALMODE, gpiomanual)
    gpiotransfer = selectpin(config, CAPTURE_GPIOTRANSFERMODE, gpiotransfer)
    gpioshutdown = selectpin(config, CAPTURE_GPIOSHUTDOWNMODE, gpioshutdown)

    GPIO.setup(gpiomanual, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(gpiotransfer, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(gpioshutdown, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Pin linked to momentary button to signal start of selected mode
    gpiotrigger = selectpin(config, CAPTURE_GPIOMODETRIGGER, gpiotrigger)

    GPIO.setup(gpiotrigger, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Pins for two poles of red/green status LED
    gpiogreen = selectpin(config, CAPTURE_GPIOGREEN, gpiogreen)
    gpiored = selectpin(config, CAPTURE_GPIORED, gpiored)

    GPIO.setup(gpiogreen, GPIO.OUT)
    GPIO.setup(gpiored, GPIO.OUT)

    # Pin to turn on uv light and ringlight - activates transistor
    gpiolights = selectpin(config, CAPTURE_GPIOLIGHTS, gpiolights)

    GPIO.setup(gpiolights, GPIO.OUT)

    # Pin to turn on GPS sensor - activates transistor, -1 indicates sensor attached directly to voltage pin
    gpiogpssensorpower = selectpin(config, CAPTURE_GPIOGPSPOWER, gpiogpssensorpower, True)

    if gpiogpssensorpower > 0:
        logging.info("GPS sensor power pin is " + str(gpioenvsensorpower))
        GPIO.setup(gpiogpssensorpower, GPIO.OUT)

    # Pin to turn on temperature/humidity sensor, -1 indicates sensor attached directly to voltage pin
    gpioenvsensorpower = selectpin(config, CAPTURE_GPIOENVPOWER, gpioenvsensorpower, True)

    if gpioenvsensorpower > 0:
        logging.info("Environmental sensor power pin is " + str(gpioenvsensorpower))
        GPIO.setup(gpioenvsensorpower, GPIO.OUT)

    # Pin to receive temperature/humidity readings - pigpio will control
    gpioenvsensordata = selectpin(config, CAPTURE_GPIOENVDATA, gpioenvsensordata)

    logging.info("GPIO pins enabled")


"""
Get current operating mode - defaults to AUTOMATIC
"""
def getcurrentmode():
    global gpiomanual, gpiotransfer, gpioshutdown, AUTOMATIC, MANUAL, TRANSFER, SHUTDOWN
    
    if GPIO.input(gpiomanual) == GPIO.HIGH:
        return MANUAL
    if GPIO.input(gpiotransfer) == GPIO.HIGH:
        return TRANSFER
    if GPIO.input(gpioshutdown) == GPIO.HIGH:
        return SHUTDOWN
    else:
        return AUTOMATIC

"""
Turn lights on or off
"""
def enablelights(activate):
    global gpiolights

    GPIO.output(gpiolights, GPIO.HIGH if activate else GPIO.LOW)
    logging.info("Lights enabled" if activate else "Lights disabled")

"""
Set up status light, returning current state as 'red', 'green' or 'off'
"""
def initstatus():
    global gpiogreen, gpiored, originalgreen, originalred

    originalgreen = GPIO.input(gpiogreen)
    originalred = GPIO.input(gpiored)

    return 'red' if originalred > originalgreen else 'green' if originalgreen > originalred else 'off'

"""
Set status light color or flash status light in specified color
"""
def showstatus(color, flashcount = 0, flashlength = 0.2):
    global gpiogreen, gpiored

    red = GPIO.HIGH if color == 'red' else GPIO.LOW
    green = GPIO.HIGH if color == 'green' else GPIO.LOW

    # Remember current setting
    currentred = GPIO.input(gpiored)
    currentgreen = GPIO.input(gpiogreen)

    if flashcount > 0:

        # Ensure that the first flash is distinct
        if red == currentred and green == currentgreen and color != "off":
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.LOW)
            time.sleep(1)
        while flashcount > 0:
            GPIO.output(gpiored, red)
            GPIO.output(gpiogreen, green)
            time.sleep(flashlength)
            GPIO.output(gpiored, GPIO.LOW)
            GPIO.output(gpiogreen, GPIO.LOW)
            time.sleep(flashlength)
            flashcount -= 1

        # Reset colour
        GPIO.output(gpiored, currentred)
        GPIO.output(gpiogreen, currentgreen)
    else:
        GPIO.output(gpiored, red)
        GPIO.output(gpiogreen, green)

    return 'red' if currentred > currentgreen else 'green' if currentgreen > currentred else 'off'

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

By default, the function therefore gets sunrise for the current date. If this time is 
prior to the current time, the function requests the sunrise time for the subsequent 
day. Ragardless, it then requests the sunset time for the day before the sunrise time.

If querytime is specified, the function behaves as if it were called at the specified
time. Calling the function for 12:00 on a given date will give the expected sunset and 
sunrise for the following night.

Returns sunsettime, sunrisetime
"""
def getsuntimes(config, latitude, longitude, querytime = None):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except:
        logging.error("Invalid coordinates - not a float")
        return None, None

    if latitude < -90 or latitude > 90:
        logging.error("Invalid coordinates - latitude (" + str(latitude) + ") out of range")
        return None, None
    if longitude < -180 or longitude > 180:
        logging.error("Invalid coordinates - longitude (" + str(longitude) + ") out of range")
        return None, None

    sun = Sun(latitude, longitude)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    if querytime is None:   
        querytime = datetime.today().replace(tzinfo=to_zone)
        
    sunrise = converttz(sun.get_sunrise_time(querytime), from_zone, to_zone)

    if querytime > sunrise:
        sunrise = converttz(sun.get_sunrise_time(querytime + timedelta(days=1)), from_zone, to_zone)

    sunset = converttz(sun.get_sunset_time(sunrise - timedelta(days=1)), from_zone, to_zone)

    if config:
        if sunset:
            config.set(EVENT_SUNSETTIME, sunset.isoformat(), SECTION_EVENT)
        if sunrise:
            config.set(EVENT_SUNRISETIME, sunrise.isoformat(), SECTION_EVENT)

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

"""
Initialize logging
"""
def initlog(name):
    logging.basicConfig(filename=name, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level = logging.INFO)

"""
Rotate logs, keeping a maximum of 5 earlier logs, each named <filename>_backup_<N>.log.
"""
def rotatelogs(name, count = 5):
    logging.info("Rotating logs")

    handlers = logging.getLogger().handlers[:]
    for handler in handlers:
        handler.close()
        logging.getLogger().removeHandler(handler)

    prevbackupname = name + ".backup_" + str(count)
    for i in range(count - 1):
        backupname = name + ".backup_" + str(4 - i)
        if os.path.exists(backupname):
            subprocess.call(['cp', backupname, prevbackupname], shell=False)
        prevbackupname = backupname

    if os.path.exists(name):
        subprocess.call(['cp', name, prevbackupname], shell=False)
        subprocess.call(['rm', name], shell=False)
        
    initlog(name)

    logging.info("Rotated logs")

"""
Take series of calibration images for different image aspects
"""
def calibratecamera(camera, series, calibrationfolder, config):
    logging.info("Generating calibration images in " + calibrationfolder)
    currentcolor = showstatus('green')

    if not os.path.isdir(calibrationfolder):
        os.mkdir(calibrationfolder)

    defaultquality = config.get(CAPTURE_QUALITY, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if defaultquality is None:
        defaultquality = 85
    for choice in series:
        if choice == 'quality':
            for i in range(10, 100, 10):
                camera.capture(os.path.join(calibrationfolder, choice + "_" + str(i) + '.jpg'), format = "jpeg", quality = i)
                showstatus('red', 1, 0.05)
        elif choice == 'brightness':
            for i in range(0, 101, 10):
                camera.brightness = i
                camera.capture(os.path.join(calibrationfolder, choice + "_" + str(i) + '.jpg'), format = "jpeg", quality = defaultquality)
                showstatus('red', 1, 0.05)
            brightness = config.get(CAPTURE_BRIGHTNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.brightness = brightness if brightness is not None else 50
        elif choice == 'sharpness':
            for i in range(-100, 101, 10):
                camera.sharpness = i
                camera.capture(os.path.join(calibrationfolder, choice + "_" + str(i) + '.jpg'), format = "jpeg", quality = defaultquality)
                showstatus('red', 1, 0.05)
            sharpness = config.get(CAPTURE_SHARPNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.sharpness = sharpness if sharpness is not None else 0
        elif choice == 'contrast':
            for i in range(-100, 101, 10):
                camera.contrast = i
                camera.capture(os.path.join(calibrationfolder, choice + "_" + str(i) + '.jpg'), format = "jpeg", quality = defaultquality)
                showstatus('red', 1, 0.05)
            contrast = config.get(CAPTURE_CONTRAST, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.contrast = contrast if contrast is not None else 0
        elif choice == 'saturation':
            for i in range(-100, 101, 10):
                camera.saturation = i
                camera.capture(os.path.join(calibrationfolder, choice + "_" + str(i) + '.jpg'), format = "jpeg", quality = defaultquality)
                showstatus('red', 1, 0.05)
            saturation = config.get(CAPTURE_SATURATION, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.saturation = saturation if saturation is not None else 0
        elif choice == 'awb_mode':
            for i in PiCamera.AWB_MODES:
                camera.awb_mode = i
                camera.capture(os.path.join(calibrationfolder, choice + "_" + i + '.jpg'), format = "jpeg", quality = defaultquality)
                showstatus('red', 1, 0.05)
            awb_mode = config.get(CAPTURE_AWBMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.awb_mode = awb_mode if awb_mode is not None else 'auto'
        elif choice == 'awb_gains':
            camera.awb_mode = 'off'
            gains = camera.awb_gains
            awb_gains = config.get(CAPTURE_AWBGAINS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            if awb_gains is not None and isinstance(awb_gains, list) and len(awb_gains) == 2:
                averagegains = (awb_gains[0], awb_gains[1])
                gainstep = 0.1
            else:
                averagegains = (2.0, 2.0)
                gainstep = 0.3
            for i in range(11):
                for j in range(11):
                    camera.awb_mode = 'off'
                    red_gain = averagegains[0] + (i - 5) * gainstep
                    blue_gain = averagegains[1] + (j - 5) * gainstep
                    camera.awb_gains = (red_gain, blue_gain)
                    camera.capture(os.path.join(calibrationfolder, choice + '_R' + '{:4.2f}'.format(red_gain) + '-B' + '{:4.2f}'.format(blue_gain) + '.jpg'), format = "jpeg", quality = defaultquality)
                    showstatus('red', 1, 0.05)
            awb_mode = config.get(CAPTURE_AWBMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
            camera.awb_mode = awb_mode if awb_mode is not None else 'auto'
            camera.awb_gains = gains
    logging.info("Calibration images complete")
    showstatus(currentcolor)