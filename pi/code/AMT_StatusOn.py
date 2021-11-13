#!/usr/bin/env python
"""
AMT_StatusOn.py - Utility to turn on/off or flash red/green status light

Syntax python R|G [flash count]

 - A colour selection, either R for red or G for green
 - An optional count for a number of on/off flashes (one second in each state)

The LED pins are coded as GPIO25 for green and GPIO7 for red (BCM mode).
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "1.0.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import RPi.GPIO as GPIO
import sys
import time

gpiogreen = 25
gpiored = 7
red = GPIO.LOW
green = GPIO.LOW
flashcount = -1

if len(sys.argv) > 1:
    if sys.argv[1] == 'R':
        red = GPIO.HIGH
    if sys.argv[1] == 'G':
        green = GPIO.HIGH

if len(sys.argv) > 2:
    flashcount = int(sys.argv[2])

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(gpiored, GPIO.OUT)
GPIO.setup(gpiogreen, GPIO.OUT)

if flashcount > 0:
    while flashcount > 0:
        GPIO.output(gpiored, red)
        GPIO.output(gpiogreen, green)
        time.sleep(1)
        GPIO.output(gpiored, GPIO.LOW)
        GPIO.output(gpiogreen, GPIO.LOW)
        time.sleep(1)S
        flashcount -= 1
else:
    GPIO.output(26, red)
    GPIO.output(gpiogreen, green)