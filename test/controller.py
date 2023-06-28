# Import libraries
import RPi.GPIO as GPIO
import time, os

# Other modules
from ultrasonic import ultrasonic
from readdetection import readdetection
from servo import servoangle
from buzzer import buzzer

### GPIO setup ###
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Motor 
Motor1A = 16
Motor1B = 18
Motor1E = 22
Motor2B = 11
Motor2A = 13
Motor2E = 15

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1E, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2E, GPIO.OUT)
GPIO.output(Motor1E, GPIO.HIGH)
GPIO.output(Motor2E, GPIO.HIGH)

# movement set
def movement_forward():
	pwm1.ChangeDutyCycle(vertical)
	pwm2.ChangeDutyCycle(vertical)
	GPIO.output(Motor1A, GPIO.HIGH)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.HIGH)
	GPIO.output(Motor2B, GPIO.LOW)
def movement_forwardleft():
	pwm1.ChangeDutyCycle(vertical*curve)
	pwm2.ChangeDutyCycle(vertical)
	GPIO.output(Motor1A, GPIO.HIGH)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.HIGH)
	GPIO.output(Motor2B, GPIO.LOW)
def movement_forwardright():
	pwm1.ChangeDutyCycle(vertical)
	pwm2.ChangeDutyCycle(vertical*curve)
	GPIO.output(Motor1A, GPIO.HIGH)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.HIGH)
	GPIO.output(Motor2B, GPIO.LOW)

def movement_backward():
	pwm1.ChangeDutyCycle(vertical)
	pwm2.ChangeDutyCycle(vertical)
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.HIGH)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.HIGH)
def movement_backwardleft():
	pwm1.ChangeDutyCycle(vertical*curve)
	pwm2.ChangeDutyCycle(vertical)
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.HIGH)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.HIGH)
def movement_backwardright():
	pwm1.ChangeDutyCycle(vertical)
	pwm2.ChangeDutyCycle(vertical*curve)
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.HIGH)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.HIGH)

def movement_anticlockwise():
	pwm1.ChangeDutyCycle(horizontal*stand)
	pwm2.ChangeDutyCycle(horizontal)
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.HIGH)
	GPIO.output(Motor2A, GPIO.HIGH)
	GPIO.output(Motor2B, GPIO.LOW)
def movement_clockwise():
	pwm1.ChangeDutyCycle(horizontal)
	pwm2.ChangeDutyCycle(horizontal*stand)
	GPIO.output(Motor1A, GPIO.HIGH)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.HIGH)
def movement_rotate():
	pwm1.ChangeDutyCycle(horizontal)
	pwm2.ChangeDutyCycle(horizontal)
	GPIO.output(Motor1A, GPIO.HIGH)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.HIGH)
def movement_antirotate():
	pwm1.ChangeDutyCycle(horizontal)
	pwm2.ChangeDutyCycle(horizontal)
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.HIGH)
	GPIO.output(Motor2A, GPIO.HIGH)
	GPIO.output(Motor2B, GPIO.LOW)

def movement_stop():
	GPIO.output(Motor1A, GPIO.LOW)
	GPIO.output(Motor1B, GPIO.LOW)
	GPIO.output(Motor2A, GPIO.LOW)
	GPIO.output(Motor2B, GPIO.LOW)

# auto mode
def auto_calibrate():
	movement_stop()
	time.sleep(1)
	movement_antirotate()
	time.sleep(0.9)
	movement_stop()
	time.sleep(1)	
def auto_cameratilt():
	for degree in range(4):
		servoangle(degree)
		time.sleep(5)
		if(auto_personcheck()):
			break
			
def auto_forward():
	movement_forward()
	time.sleep(0.25)
	movement_stop()
	time.sleep(3)
def auto_obstaclecheck():
	if ultrasonic() < mindistancetowall :
		print('Distance to wall less than', mindistancetowall, '... Switching direction')
		auto_calibrate()
		movement_rotate()
		time.sleep(0.3)
		movement_stop()
		time.sleep(3)
		return True
	else:
		return False
def auto_personcheck():
	global automode	
	if(readdetection() == True) and (forceautomode == False):
		buzzer()
		os.system('clear')
		print("Person detected... Switch to Manual mode")
		time.sleep(1)
		automode = not automode	
		return True
def auto_directionchange():
	global scanmode
	print(scanmode)
	if(scanmode == 1):
		auto_calibrate()
		for turn in range(4):
			if(automode == True):
				movement_rotate()
				time.sleep(0.3)
				movement_stop()
				time.sleep(2)
			if(auto_personcheck()):
				print("help")
				break
			else:
				auto_cameratilt()

	elif(scanmode == 2):
		auto_calibrate()
		for turn in range(8):
			if(automode == True):
				movement_rotate()
				time.sleep(0.18)
				movement_stop()
				time.sleep(2)
			if(auto_personcheck()):
				break
			else:
				auto_cameratilt()

degree = 0
automode = False				# auto = True, manual = False
running = True					# running = True, terminated = False
forceautomode = False			# ignore auto_personcheck()
scanmode = 0
vertical = 70.0					# ChangeDutyCycle = speed
horizontal = 65.0
stand = 0.25		
curve = 0.5
mindistancetowall = 10.00		# in cm

pwm1 = GPIO.PWM(Motor1E, 2000)	# frequency
pwm2 = GPIO.PWM(Motor2E, 2000)
pwm1.start(92.0)				# motor start with max speed
pwm2.start(92.0)

# Initial setup
servoangle(degree)				# adjust camera angle to original
movement_stop()					# make sure the robot is stationary

# Main function
def control(input_char):
	degree = 0
	automode = False				# auto = True, manual = False
	running = True					# running = True, terminated = False
	forceautomode = False			# ignore auto_personcheck()
	scanmode = 0

	while(running):
		# mode update
		if input_char == '/':
			automode = not automode
			os.system('clear')
			if(automode == True):
				print("Switch to Auto mode")
			else:
				print("Switch to Manual mode")
			time.sleep(1)
		# switch to auto 
		if(automode == False):			
			if input_char == '.':		# terminate	
				running = False
			elif input_char == '8':	# movement command	
				movement_forward()
			elif input_char == '7':
				movement_forwardleft()
			elif input_char == '9':
				movement_forwardright()
			elif input_char == '2':
				movement_backward()
			elif input_char == '1':
				movement_backwardleft()
			elif input_char == '3':
				movement_backwardright()
			elif input_char == '4':
				movement_anticlockwise()
			elif input_char == '6':
				movement_clockwise()
			elif input_char == '5':
				movement_stop()
			elif input_char == '0':
				movement_rotate()
			elif input_char == '+':
				if(degree < 3) and (degree >= 0):
					degree = degree + 1
					servoangle(degree)
			elif input_char == '-':
				if(degree <= 3) and (degree > 0):
					degree = degree - 1
					servoangle(degree)
			elif input_char == '*':
				forceautomode = not forceautomode
				print("Force Automode is", forceautomode, "Now")
			elif input_char == '\n':
				scanmode = scanmode + 1
				if(scanmode == 3):
					scanmode = 0
				if(scanmode == 0):
					print("Camera is manually tilt by user and robot will not turn")
				elif(scanmode == 1):
					print("Camera automatically tilt and robot will turn in 4 direction")
				else:
					print("Camera automatically tilt and robot will turn in 8 direction")
					
		# switch to manual
		elif(automode == True):							
			if(auto_personcheck()):
				continue
			else:
				if(auto_obstaclecheck()):
					continue
				else:
					auto_forward()
					auto_directionchange()
					
	GPIO.cleanup()								# Clean GPIO at termination
