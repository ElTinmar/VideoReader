#!/usr/bin/env python3

import os
import cv2
import time
import numpy as np
import argparse

def parse_arguments():
    
    parser = argparse.ArgumentParser(
        description='Benchmark producer-consumer video reader'
    )
    parser.add_argument(
        'videofile', 
        type = str,
        help = 'Path to the video'
    )
    parser.add_argument(                                                        
        '--load',                                                               
        type = str,                                                             
        default = "MC",                                                         
        help = 'Synthetic load: light L, single core SC, multicore MC'          
    )  
    parser.add_argument(
        '--gpu',
        action = 'store_true',
        help = 'Use GPU for hardware accelerated decoding with FFMPEG'
    )
    args = parser.parse_args()

    # check that video file exists
    videofile = args.videofile
    if not os.path.exists(videofile):
        raise FileNotFoundError

    use_gpu = args.gpu

    if (args.load == "MC"):
        pfun = synthetic_load_multi_core
    elif (args.load == "SC"):
        pfun = synthetic_load_single_core
    elif (args.load == "L"):
        pfun = synthetic_load_light
    elif (args.load == "N"):
        pfun = do_nothing
    else:
        raise ValueError

    return videofile, use_gpu, pfun
        
def busy_wait(dt):
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass

def do_nothing(frame,frame_num):
    pass

def synthetic_load_light(frame,frame_num):
    time.sleep(0.1) 
    print(frame_num)
    
def synthetic_load_single_core(frame,frame_num):
    busy_wait(0.1) 
    print(frame_num)

def synthetic_load_multi_core(frame,frame_num):
     # CPU intensive multithreaded (tune with OMP_NUM_THREADS) 
    try:
        frame32 = np.float32(frame)                                                 
        u, s, vh = np.linalg.svd(frame32)
        print(frame_num)
    except np.linalg.LinAlgError:
        print(str(frame_num) + ' SVD did not converge')


videofile, use_gpu, pfun = parse_arguments()

# Hardware acceleration on NVIDIA GPU if FFMPEG was compiled with CUVID support
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
