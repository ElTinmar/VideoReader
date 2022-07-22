#!/usr/bin/env python3

import cv2
import time

startTime = time.time()
cap = cv2.cudacodec.createVideoReader('/home/martin/jumanji.mp4')
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
