import os
import cv2
import time 

use_gpu = False

# Hardware acceleration on NVIDIA GPU if FFMPEG was compiled with CUVID support
if use_gpu:
	os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
	
cap = cv2.VideoCapture("jumanji.mp4", cv2.CAP_FFMPEG)
frame_num = 0

def process(frame,frame_num):	
    # simulate long processing
    time.sleep(0.1)
    print(frame_num)

while True:
    # Get frames here
    rval, frame = cap.read()
    if not rval:
        break
    
    frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    frame_num += 1
    
    process(frame_gray,frame_num)

cap.release()
