import RPi.GPIO as GPIO
import time

### GPIO setup ###
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Buzzer
BUZZ = 36
interval = 0.2
GPIO.setup(BUZZ, GPIO.OUT)

def buzzer():
	print("buzzer triggered")
	GPIO.output(BUZZ, GPIO.HIGH)
	time.sleep(0.3)
	GPIO.output(BUZZ, GPIO.LOW)
	time.sleep(0.2)

# tester
#for t in range(3):
#	buzzer()
