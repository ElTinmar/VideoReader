import os
import cv2
import time 
cv2.__version__

use_gpu = False
prev_frame_time = 0
curr_frame_time = 0

if use_gpu:
	os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
	
cv2.namedWindow('Display')
cap = cv2.VideoCapture("/home/martin/Desktop/forEmi/2021_07_26_B.avi", cv2.CAP_FFMPEG)
while True:
    rval, frame = cap.read()
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    
    if not rval:
        break
    
    cv2.putText(frame,str(int(fps)), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
    cv2.imshow('Display',frame)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
