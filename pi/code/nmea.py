import io
import time
import pynmea2
import serial
import RPi.GPIO as GPIO
import statistics
import math
import os
import termios

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, GPIO.HIGH)
time.sleep(5)

iteration = 0
lats = []
lons = []

while len(lats) < 20 and iteration < 20:
    try:
        with serial.Serial('/dev/ttyS0', 9600, timeout=5.0) as ser:
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            while len(lats) < 20:
                try:
                    line = sio.readline()
                    word = str(line)[0:6]
                    if 'GGA' in word:
                        msg = pynmea2.parse(line)
                        if msg.gps_qual > 0:
                            lats.append(float(msg.latitude))
                            lons.append(float(msg.longitude))
                            print('Latitude: {} Longitude: {}'.format(str(round(msg.latitude, 6)), str(round(msg.longitude, 6))))
                except serial.SerialException as e:
                    iteration += 1
                    print('SerialException: {}'.format(e))
                    break
                except pynmea2.ParseError as e:
                    #print('Parse error: {}'.format(e))
                    continue
                except termios.error as e:
                    #print('Parse error: {}'.format(e))
                    continue
    except Exception as e:
        iteration += 1
        print('Exception: {}'.format(e))
        continue

if len(lats) > 0:
    latitude = statistics.mean(lats)
    longitude = statistics.mean(lons)
    if len(lats > 10):
        sdlatitude = statistics.stdev(lats)
        sdlongitude = statistics.stdev(lons)
        # Accuracy calculated by taking the hypoteneuse of the two standard deviations, multiplying by 1.96 to get ~95% interval and then converting to metres 
        accuracy = math.sqrt(sdlongitude**2 + sdlatitude**2) * 1.96 * 111139
        if accuracy < 1.0:
            accuracy = 1.0
    else:
        accuracy = 100.0

    print('Latitude: {} Longitude: {} Accuracy: {}'.format(str(round(latitude, 6)), str(round(longitude, 6)), str(round(accuracy, 0))))

GPIO.output(24, GPIO.LOW)
