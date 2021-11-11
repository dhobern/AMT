#!/usr/bin/env python


import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(3, GPIO.FALLING)

# Switch off lights
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, GPIO.LOW)

subprocess.call(['shutdown', '-h', 'now'], shell=False)