#!/usr/bin/env python3

import cv2
import time
import os

videofile = '/home/martin/Desktop/forEmi/2021_07_26_B.avi'
if not os.path.exists(videofile):
	raise FileNotFoundError

startTime = time.time()
cap = cv2.cudacodec.createVideoReader(videofile)
ret, gpuFrame = cap.nextFrame()
frame_num = 1
while ret:
	ret, gpuFrame = cap.nextFrame()
	frame_num = frame_num + 1
	frame = gpuFrame.download()
stopTime = time.time()
elapsed = stopTime  - startTime
fps = frame_num/elapsed
print("#Frames: " + str(frame_num) + ", Time elapsed: " + str(elapsed) + ", FPS: " + str(fps))
