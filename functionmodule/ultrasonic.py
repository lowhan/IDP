import RPi.GPIO as GPIO
import time

### GPIO setup ###
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Ultrasonic sensor
TRIG = 3
ECHO = 5

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def ultrasonic():
	GPIO.output(TRIG, True)
	time.sleep(0.0001)
	GPIO.output(TRIG, False)
	while GPIO.input(ECHO) == 0:
		pulse_start = time.time()
	while GPIO.input(ECHO) == 1:
		pulse_end = time.time()
	duration = pulse_end - pulse_start
	distance = duration*17150
	distance = round(distance, 2)
	time.sleep(0.2)
	return distance

# tester
# print(ultrasonic())
