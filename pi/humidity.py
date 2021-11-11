import requests
import time
import psutil
import adafruit_dht
from board import *
import RPi.GPIO as GPIO
import sys

GPIO.setwarnings(False)

# GPIO10
SENSOR_PIN = D10

# GPIO7
GREEN_PIN = 25

# GPIO25
RED_PIN = 7

temperature = 'Unknown'
humidity = 'Unknown'
motion_running = False

GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(RED_PIN, GPIO.OUT)

while True:

    if "motion" in (p.name() for p in psutil.process_iter()):
        if not motion_running:
            motion_running = True
            # Green light
            GPIO.output(RED_PIN, GPIO.LOW)
            GPIO.output(GREEN_PIN, GPIO.HIGH)

        try:
            dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
            temperature = dht22.temperature
            humidity = dht22.humidity
        except RuntimeError:
            print("Failed to read sensor")
        
        requests.get('http://localhost:8080/0/config/set?text_event=TempC_'+str(temperature)+'-Humid_'+str(humidity))

    else:
        if motion_running:
            motion_running = False
            # Red light
            GPIO.output(RED_PIN, GPIO.HIGH)
            GPIO.output(GREEN_PIN, GPIO.LOW)

    time.sleep(10)
