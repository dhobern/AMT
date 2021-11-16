#!/usr/bin/env python
"""
amt_status - Utility to turn on/off or flash red/green status light

Syntax python R|G [flash count]

 - A colour selection, either R for red or G for green
 - An optional count for a number of on/off flashes (one second in each state)

The LED pins are coded as GPIO25 for green and GPIO7 for red (BCM mode).
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.1"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import RPi.GPIO as GPIO
import sys
import time

# GPIO pins using BCM notation
gpiogreen = 25
gpiored = 7

def initstatus(config):
    global gpiogreen, gpiored
    if 

def showstatus(color, flashcount = 0):
    gpiogreen = 25
    gpiored = 7
    red = GPIO.HIGH if color == 'R' else GPIO.LOW
    green = GPIO.HIGH if color == 'G' else GPIO.LOW

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

if __name__ == "__main__":
    color = ''

    if len(sys.argv) > 1:
        color = sys.argv[1]            c

    if len(sys.argv) > 2:
        flashcount = int(sys.argv[2])

    showstatus(color, flashcount)