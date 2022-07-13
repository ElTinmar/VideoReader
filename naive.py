import os
import cv2
import time 

use_gpu = False

# Hardware acceleration on NVIDIA GPU if FFMPEG was compiled with CUVID support
if use_gpu:
	os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
	
cap = cv2.VideoCapture("input.avi", cv2.CAP_FFMPEG)
cv2.namedWindow('Display')

prev_frame_time = 0
curr_frame_time = 0
while True:
    # Get frames here
    rval, frame = cap.read()
    if not rval:
        break
    
    # Do image processing here 
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    cv2.putText(frame,str(int(fps)), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
    cv2.imshow('Display',frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
