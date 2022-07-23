#!/usr/bin/env python3

import os
import cv2
import time
import utils

# parse arguments
videofile, use_gpu, pfun, cvcuda, host, _, _ = utils.parse_arguments()

# Hardware acceleration on NVIDIA GPU 
if use_gpu:
    if cvcuda:
        cap = cv2.cudacodec.createVideoReader(videofile)
    else:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
        cap = cv2.VideoCapture(videofile, cv2.CAP_FFMPEG)
else:
    cap = cv2.VideoCapture(videofile, cv2.CAP_FFMPEG)

frame_num = 0
duration = 0
start = time.time()
while True:

    # Get frames here
    if use_gpu and cvcuda:
        rval, frame = cap.nextFrame()
        if rval and host:
            frame = frame.download()
    else:
        rval, frame = cap.read()
        #frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY) 
    
    if not rval:
        break
    
    frame_num += 1
    
    try:
        pfun(frame,frame_num)
    except KeyboardInterrupt:
        break

stop = time.time()
duration = stop - start
fps = frame_num/duration
print("num frames : " + str(frame_num) + ", duration : " + str(duration) + ", FPS : " + str(fps))

if not cvcuda:
    cap.release()
