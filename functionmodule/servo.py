import RPi.GPIO as GPIO
import time

### GPIO setup ###
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Servo motor
SERV = 32

GPIO.setup(SERV, GPIO.OUT)
cycle = [6, 7, 7.8, 8.5]

def servoangle(degree):
	if (degree >= 0) and (degree <= 3):
		servo1 = GPIO.PWM(SERV, 50)
		servo1.start(cycle[degree])
		time.sleep(0.1)
		servo1.stop()
		time.sleep(0.3)

# tester
#servoangle(3)
