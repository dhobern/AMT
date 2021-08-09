import RPi.GPIO as GPIO

red = GPIO.LOW
green = GPIO.LOW

if len(sys.argv) > 1:
    if sys.argv[1] == 'R':
        red = GPIO.HIGH
    if sys.argv[1] == 'G':
        green = GPIO.HIGH

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

GPIO.output(26, red)
GPIO.output(22, green)
