########################################################################################
# Main application / support Mobile apps							   				   #
########################################################################################

# Import libraries
import RPi.GPIO as GPIO
import time, os
import socket
import cv2
import imutils
import numpy as np
import base64
from threading import Thread

# Import Other modules
from functionmodule.ultrasonic import ultrasonic
from functionmodule.servo import servoangle
from functionmodule.buzzer import buzzer

########################################################################################

#GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

########################################################################################

# Motor setup
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
pwm1 = GPIO.PWM(Motor1E, 2000)				# frequency
pwm2 = GPIO.PWM(Motor2E, 2000)
pwm1.start(92.0)							# motor start with max speed
pwm2.start(92.0)

########################################################################################

# Initial Parameter / setup
degree = 0						# degree of camera at start
vertical = 70.0					# ChangeDutyCycle = speed 70, 65
horizontal = 65.0
stand = 0.25		
curve = 0.5
automode = False				# auto = True, manual = False
scanmode = 0					# 0 = one direction scan with no rotation
input_char = ''
detected = False				# Reset detection to False
running = True					# Keep program run on start
 
# Detection setup	(Yolov4)
classes_file = "traineddata/v4-tiny/classes.names" 			
weights_path ="traineddata/v4-tiny/yolov4-tiny_last.weights"  	
config_path = "traineddata/v4-tiny/yolov4-tiny.cfg" 			# add -yolo after tiny to use pretrained data

# Server setup
host_ip = '10.42.0.1' #'192.168.1.156'
port = 5000

# LiveStream setup
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FPS, 1)
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),50]

########################################################################################

# Movement set/functions
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

########################################################################################

# Auto mode functions
def auto_calibrate():
	movement_stop()
	time.sleep(1)
	movement_antirotate()
	time.sleep(0.9)
	movement_stop()
	time.sleep(1)				
def auto_forward():
	movement_forward()
	time.sleep(0.25)
	movement_stop()
	time.sleep(3)        
def auto_obstaclecheck():							# change minimal distance to change direction
	mindistancetowall = 10.00		# in cm
	distance = ultrasonic()
	print("Distance to obstacle:", distance, "cm")
	if (distance < mindistancetowall):
		print('Distance to wall less than', mindistancetowall, '... Switching direction')
		auto_calibrate()
		movement_rotate()
		time.sleep(0.3)
		movement_stop()
		time.sleep(3)
		return True
	else:
		return False
def auto_cameratilt():								# change auto tilt delay
	global detected 
	for degree in range(4):
		servoangle(degree)
		print("Scanning with degree of", degree)
		time.sleep(4)
		if(detected):
			auto_modechange()
			break				
def auto_modechange():								# change buzz times
	global automode
	if(automode == True):
		automode = False
		for i in range(5):
			buzzer()
		print("Person detected... Switch to Manual mode")

def auto_directionchange():							
	global automode
	global scanmode
	global input_char
	global detected 
	
	time.sleep(0.5)									#print(detected)
	if(scanmode == 0):
		if(detected):
			auto_modechange()
		elif(input_char == "/"):
			automode = False
			print("Switch to Manual mode")
		else:
			auto_cameratilt()
	
	elif(scanmode == 1):
		auto_calibrate()
		for turn in range(4):
			print("Facing at direction", turn)
			if(automode == True):
				movement_rotate()
				time.sleep(0.3)
				movement_stop()
				time.sleep(2)
			if(detected):
				auto_modechange()
				break
			elif(input_char == "/"):
				automode = False
				print("Switch to Manual mode")
				break
			else:
				auto_cameratilt()
				
	elif(scanmode == 2):
		auto_calibrate()
		for turn in range(8):
			print("Facing at direction", turn)
			if(automode == True):
				movement_rotate()
				time.sleep(0.18)
				movement_stop()
				time.sleep(2)
			if(detected):
				auto_modechange()
				break
			elif(input_char == "/"):
				automode = False
				print("Switch to Manual mode")
				break
			else:
				auto_cameratilt()

########################################################################################

# Detection Thread (yolo function that do object/image detection)
def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

classes = None
with open(classes_file, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
net = cv2.dnn.readNet(weights_path, config_path)
conf_threshold = 0.5
nms_threshold = 0.4

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)   
    
def detection():
	global detected 
	global automode
	counter = 0
	
	while(client_socket): 
		ret, image = vid.read()
		
		if ret:
			Width = image.shape[1]
			Height = image.shape[0]
			scale = 1/255
			blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
			net.setInput(blob)
			outs = net.forward(get_output_layers(net))
			
			class_ids = []
			confidences = []
			boxes = []

			for out in outs:
				for detection in out:
					scores = detection[5:]
					class_id = np.argmax(scores)
					confidence = scores[class_id]
					if(confidence > 0.3):			# print detected class name if confidence > 0.3
						print(classes[class_id], ": ", confidence) 	# if got detect person will print on the terminal also
						center_x = int(detection[0] * Width)
						center_y = int(detection[1] * Height)
						w = int(detection[2] * Width)
						h = int(detection[3] * Height)
						x = center_x - w / 2
						y = center_y - h / 2
						class_ids.append(class_id)
						confidences.append(float(confidence))
						boxes.append([x, y, w, h])
						counter = counter + 1
			if(counter > 0):
				if(automode == False):
					buzzer()
				detected = True
				counter = 0
			else:
				detected = False
				
			indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
			for i in indices:
				try:
					box = boxes[i]
				except:
					i = i[0]
					box = boxes[i]
				
				x = box[0]
				y = box[1]
				w = box[2]
				h = box[3]
				draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
				
			cv2.imshow("object detection", image)
			cv2.waitKey(1)

########################################################################################

# Server socket (create an INET, STREAMing socket)
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('HOST IP:',host_ip)
print('HOST PORT:',port)
socket_address = (host_ip,port)
print('Socket created')

# bind the socket to the host. 
#The values passed to bind() depend on the address family of the socket
server_socket.bind(socket_address)
print('Socket bind complete')

#listen() enables a server to accept() connections
#listen() has a backlog parameter. 
#It specifies the number of unaccepted connections that the system will allow before refusing new connections.
server_socket.listen(5)
print('Socket now listening')
client_socket,addr = server_socket.accept()
print("Accepted connection from: ",addr)

########################################################################################

# Live Stream Thread (function to capture and process images)
def liveStream():
	while(client_socket):
		ret, image = vid.read()
		image = imutils.resize(image,width=416)
		encoded,buffer = cv2.imencode('.jpeg',image,[cv2.IMWRITE_JPEG_QUALITY,50])
		message = base64.b64encode(buffer)
		size = len(message)
		#print(size) # value print from her
		strSize = str(size) + "\n"
		client_socket.sendto(strSize.encode('utf-8'),addr)
		client_socket.sendto(message,addr)
		#this is my idea to separate the next size with the base64 string
		client_socket.sendto(("\nhappy face\n").encode('utf-8'),addr)

########################################################################################

# Controller Thread (Main function used to control robot)
def controller():
	global input_char
	global automode
	global degree
	global scanmode
	global running 
	
	print("Booting ...")
	servoangle(degree)									# adjust camera angle to original
	time.sleep(12)										# Remove this for testing
	print("Done !")
	
	while(running):
		if input_char == "b":							# Terminate	
			running = False
			exit()
		if input_char == "/":							# mode change
			automode = not automode
			os.system('clear')
			if(automode == True):
				print("Switch to Auto mode")
				time.sleep(1)
			else:
				print("Switch to Manual mode")
				time.sleep(2)
		if(automode == False):							# manual mode (free to use movement command)
			if input_char == '8':						# move forward
				print("forward")
				movement_forward()						
			elif input_char == '7':						# move left forward
				print("forwardleft")
				movement_forwardleft()					
			elif input_char == '9':						# move right forward
				print("forwardright")
				movement_forwardright()					
			elif input_char == '2':						# move backward
				print("backward")
				movement_backward()						
			elif input_char == '1':						# move left backward
				print("leftbackward")
				movement_backwardleft()							
			elif input_char == '3':						# move right backward
				print("rightbackward")
				movement_backwardright()				
			elif input_char == '4':						# rotate in anticlockwise
				print("turn in anticlockwise")
				movement_anticlockwise()				
			elif input_char == '6':						# rotate in clockwise
				print("turn in clockwise")
				movement_clockwise()					
			elif input_char == '5':						# stop	
				movement_stop()											
			elif input_char == '+':						# camera tilt up
				print("camera tilt up")
				if(degree < 3) and (degree >= 0):
					degree = degree + 1
				servoangle(degree)
				time.sleep(1)
			elif input_char == '-':						# camera tilt down
				print("camera tilt down")
				if(degree <= 3) and (degree > 0):
					degree = degree - 1
				servoangle(degree)
				time.sleep(1)
			elif input_char == '*':						# scanning mode change (0 - default | 1 - 4 direction | 2 - 8 direction)
				scanmode = scanmode + 1
				if(scanmode == 3):
					scanmode = 0
				if(scanmode == 0):
					print("Camera automatically tilt but robot will not turn")
				elif(scanmode == 1):
					print("Camera automatically tilt and robot will turn in 4 direction")
				else:
					print("Camera automatically tilt and robot will turn in 8 direction")
				time.sleep(1)						
		elif(automode == True):							# Auto mode (can't movement manually or change camera tilt angle/scanning mode)
			if(auto_obstaclecheck()):					# distance check
				continue
			else:
				auto_forward()							# move forward
				auto_directionchange()					# scanning

	GPIO.cleanup()		

########################################################################################

# Input Thread (Function to receive input from mobile UI)
def receive_data():
	global input_char
	global running 
	
	while(running):
		input_char = client_socket.recv(1).decode("utf-8")	#print(input_char)

########################################################################################

# Initial Threads
t1 = Thread(target=liveStream)
t2 = Thread(target=controller)
t3 = Thread(target=detection)
t4 = Thread(target=receive_data)

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

vid.close()
