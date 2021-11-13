import RPi.GPIO as GPIO
import sys
import time

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

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

if flashcount > 0:
    while flashcount > 0:
        GPIO.output(26, red)
        GPIO.output(22, green)
        time.sleep(1)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(22, GPIO.LOW)
        time.sleep(1)
        flashcount -= 1
else:
    GPIO.output(26, red)
    GPIO.output(22, green)