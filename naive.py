#!/usr/bin/env python3

import os
import cv2
import time
import utils

# parse arguments
videofile, use_gpu, pfun = utils.parse_arguments()

# Hardware acceleration on NVIDIA GPU 
if use_gpu:
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"

cap = cv2.VideoCapture(videofile, cv2.CAP_FFMPEG)
frame_num = 0
duration = 0

start = time.time()
while True:
    # Get frames here
    rval, frame = cap.read()
    if not rval:
        break
    
    #frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    frame_num += 1
    
    try:
        pfun(frame,frame_num)
    except KeyboardInterrupt:
        break
stop = time.time()
duration = stop - start
fps = frame_num/duration
print("num frames : " + str(frame_num) + ", duration : " + str(duration) + ", FPS : " + str(fps))

cap.release()
