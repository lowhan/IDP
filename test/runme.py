import os, threading

def exe1(): 
    os.system('cd robot/yolo && ./darknet detector demo cfg/coco.data cfg/yolov3-tiny.cfg weights/yolov3-tiny.weights')

def exe2(): 
    os.system('python3 robot/main.py')

def exe3():
	os.system('ffplay -video_size 640x480 -framerate 30 -i /dev/video0')

if __name__ == "__main__": 
    # creating thread 
	t1 = threading.Thread(target=exe1, args=()) 
	t2 = threading.Thread(target=exe2, args=()) 
	# t3 = threading.Thread(target=exe3, args=()) 
	
	# starting thread 1 
	t1.start() 
	# starting thread 2 
	t2.start() 
	# starting thread 3 
	# t3.start() 
	
	# wait until thread 1 is completely executed 
	t1.join() 
	# wait until thread 2 is completely executed 
	t2.join() 
	# wait until thread 3 is completely executed 
	# t3.join() 

	# both threads completely executed 
	print("Done!") 

