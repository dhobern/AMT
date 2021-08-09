import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setup(10, GPIO.OUT)
GPIO.output(10, GPIO.LOW)


