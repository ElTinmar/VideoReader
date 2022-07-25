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

def producer(videofile, buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz):
    """get images from file and put them in a queue"""
    
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
                    # weird, frame returned has extra columns
                    frame_gray = frame_gray[0:height,0:width]
        else:
            rval, frame = cap.read()
            if rval:
                frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY) 
        
        if not rval:
            break
        
        frame_num += 1
        h0,h1,h2,h3 = utils.int32_to_uint8x4(frame_num)
        header = np.array([h0,h1,h2,h3], dtype=np.uint8)
        data = np.concatenate((header,frame_gray.reshape(width*height)),axis=None)
        ok = srb.push(data,block=True,timeout=0.00001)

        # Monitor the state of the queue
        if (frame_num % 100) == 0:
            print("Frame queue usage: " + str(100*srb.size()/srb.totalSize) + "%")

    # Wait for all frames to be consumed
    while not srb.empty():
        time.sleep(0.1)

    # Send poison pill to all workers
    for i in range(n_consumers):
        header = np.array([255,255,255,255], dtype=np.uint8)
        dummy = np.zeros(height*width,dtype=np.uint8)
        poison_pill = np.concatenate((header,dummy),axis=None)
        srb.push(poison_pill)
    
    print("Producer time: " +  str(time.time()-tStt))

def consumer(buf, wlk, rlk, wrtCrsr, rdCrsr, qsize, itemSz, process_num, process_fun):
    """process images from the queue """

    srb = SharedRingBuffer(qsize, itemSz, buf, wlk, rlk, wrtCrsr, rdCrsr)
    
    tStt = time.time()
    while True: 
        # get frame and frame number from the queue
        ok, data = srb.pop(block=False,timeout=0.000001)                                                                                                             
        if ok:
            data = np.asarray(data)
            header, frame = np.split(data,[4])
            if all(header == 255): # poison pill
                print("consumer {0}, received poison pill".format(process_num))
                break
            
            frame_num = utils.uint8x4_to_int32(header[0],header[1],header[2],header[3])
            frame = frame.reshape((height,width))
            
            # do some processing
            process_fun(frame,[])

    print("Consumer {0} time: {1}".format(process_num,time.time()-tStt))

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
    itemSize = width*height+4 # image + 4 bytes header 
    rlk = Lock()
    wlk = Lock()
    buf = RawArray('B',qsize*itemSize) #uint8 frame data + 4 bytes header
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
