#!/usr/bin/env python3

# Export a list of cam objects

import sys, subprocess, cv2

# Cam can be passed as command line argument 
nCamsToTry = 20
if len(sys.argv) > 1:
  nCamsToTry = int(sys.argv[1])

# Iterate through 0 to nCamsToTry to check if cameras device are present
def getCams(nCamsToTry):
  i: int = 0
  camList = []
  while True:
    cap = cv2.VideoCapture(i)
    if not cap.isOpened():
      a = 1
    else:
      while True:
        ret, frame = cap.read()
        if not ret:
          break
        else:
          camList.append(i)
          break
    cap.release()
    i += 1
    if i > nCamsToTry:
      break
  return camList

if __name__ == "__main__":
    print('\n----------------------------\n\nList of cams with pixel formats supported by openCV : \n',getCams(nCamsToTry),'\n')



### 
######  

import subprocess, json
from multiprocessing.dummy import Pool as ThreadPool  # This uses threading, not multiprocessing

listCams = []

def getCams(cam):
  global listCams 
  out = subprocess.Popen(['v4l2-ctl', '--device', f'/dev/video{cam}', '--get-input'],
             stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT)
  stdout,stderr = out.communicate()

  linesOut = stdout.decode('UTF-8').split()[3]

  if linesOut == '0':
    listCams.append(cam)

  return listCams

def main():
  pool = ThreadPool(16)  
  pool.map(getCams, range(0,49)) # Increase upper range to check more cams
  pool.close()
  pool.join()
  return sorted(listCams)

if __name__ == "__main__":
  print('List cams with pixel formats supported by ffmpeg : \n',main(),'\n')