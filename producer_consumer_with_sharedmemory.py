#!/usr/bin/env python3

from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import RawArray, RawValue
import cv2
import time
import os
import numpy as np
import argparse
import utils
from shared_buffer import SharedRingBuffer
import ctypes 
import cProfile

def producer(videofile, buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz):
    """get images from file and put them in a queue"""
    
    pr = cProfile.Profile()
    pr.enable()

    if use_gpu:
        if cvcuda:
            cap = cv2.cudacodec.createVideoReader(videofile)
            fmt = cap.format()
        else:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"
            cap = cv2.VideoCapture(videofile, cv2.CAP_FFMPEG)
    else:
        cap = cv2.VideoCapture(videofile, cv2.CAP_FFMPEG)
    
    srb = SharedRingBuffer(qsize, itemSz, buf, wlk, rlk, wrtCrsr, rdCrsr)
    frame_num = 0
    tStt = time.time()
    while True:
        # Get frames here
        if use_gpu and cvcuda:
            rval, frame = cap.nextFrame()
            if rval:
                frame_gray = cv2.cuda.cvtColor(frame,cv2.COLOR_RGBA2GRAY)
                if host:
                    frame_gray = frame_gray.download()
        else:
            rval, frame = cap.read()
            if rval:
                frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY) 
        
        if not rval:
            break
        
        frame_num += 1
        ok = srb.push(frame_gray.reshape(itemSz),block=True,timeout=0.00001)

        # Monitqor the state of the queue
        if (frame_num % 100) == 0:
            print("Frame queue usage: " + str(100*srb.size()/srb.totalSize) + "%")

    # Wait for all frames to be consumed
    while not srb.empty():
        time.sleep(0.1)

    # Send poison pill to all workers
    for i in range(n_consumers):
        poison_pill = -1*np.ones(height*width,dtype=int)
        srb.push(poison_pill)
    
    print("Producer time: " +  str(time.time()-tStt))
    pr.disable()
    pr.print_stats(sort='tottime')

def consumer(buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz, process_num, process_fun):
    """process images from the queue """
   
    pr = cProfile.Profile()                                                     
    pr.enable()

    srb = SharedRingBuffer(qsize, itemSz, buf, wlk, rlk, wrtCrsr, rdCrsr)

    while True: 
        # get frame and frame number from the queue
        ok, frame = srb.pop(block=False,timeout=0.000001)                                                                                                             
        if ok:
            if frame[0] == -1: # poison pill
                print("consumer {0}, received poison pill".format(process_num))
                break
            
            frame = np.asarray(frame)
            frame = frame.reshape((height,width))
            
            # do some processing
            process_fun(frame,[])
    
    pr.disable()
    time.sleep(process_num+1)
    pr.print_stats(sort='tottime')

def start(buf, wlk, rlk, wrtCrsr,rdCrsr, videofile, qsize, itemSz, n_consumers, process_fun):
    """spawn all the processes"""

    # start consumers and producers                                             
    consumer_process = [];                                                      
    for i in range(n_consumers):                                                
        p = Process(
            target=consumer, 
            args=(buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz, i, process_fun),
        )
        consumer_process.append(p)                                              
        p.start()

    producer_process = Process(
        target=producer, 
        args=(videofile, buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz)
        )    
    producer_process.start()

    # wait for producers to terminate
    try:
        producer_process.join()
    except KeyboardInterrupt:
        producer_process.terminate()
        producer_process.join()

    return 0

if __name__ == "__main__":
    
    (videofile, 
    use_gpu, 
    pfun, 
    cvcuda, 
    host, 
    n_consumers, 
    qsize) = utils.parse_arguments()
    
    ## Get video info
    cap = cv2.VideoCapture(videofile,cv2.CAP_FFMPEG)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    ## FORCE HOST
    host = True

    print('Allocate buffer')
    itemSize = width*height
    rlk = Lock()
    wlk = Lock()
    buf = RawArray('B',qsize*itemSize) #uint8 data
    wrtCrsr = RawValue('i',0)
    rdCrsr = RawValue('i',0)

    num_frames = 0
    start_time = time.time()
    num_frames = start(
        buf,
        wlk,
        rlk,
        wrtCrsr,
        rdCrsr,
        videofile, 
        qsize,
        itemSize,
        n_consumers, 
        pfun
    )
    stop_time = time.time()
    duration = stop_time - start_time
    fps = num_frames/duration

    print("#frames: {0}, duration: {1}, FPS: {2}".format(
        num_frames, 
        duration, 
        fps
        )
    )
