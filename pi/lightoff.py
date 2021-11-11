import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setup(37, GPIO.OUT)
GPIO.output(37, GPIO.LOW)

