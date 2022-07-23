#!/usr/bin/env python3

from multiprocessing import Process, Queue, JoinableQueue
import cv2
import time
import os
import queue
import numpy as np
import argparse
import utils

def producer(path, use_gpu, frame_queue, result_queue):
    """get images from file and put them in a queue"""

    if use_gpu:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"

    stream = cv2.VideoCapture(path)
    frame_num = 0
        
    while True:
        grabbed, frame = stream.read()
        if not grabbed:
            break
                
        frame_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)        
        frame_num += 1
        frame_queue.put((frame_gray, frame_num))
        
    stream.release()
    result_queue.put(frame_num)
    # Wait until queue is emptied by consumers 
    frame_queue.join()

def consumer(frame_queue, result_queue, process_num, process_fun):
    """process images from the queue """

    while True: 
        try:
            # get frame and frame number from the queue
            frame, frame_num = frame_queue.get(block=False)                                                                                                             
            # do some processing
            process_fun(frame,frame_num)
            
            frame_queue.task_done()
            
        except queue.Empty:
            pass
        
def start(frame_queue, result_queue, videofile, n_consumers,
            process_fun, use_gpu):
    """spawn all the processes"""

    # start consumers and producers                                             
    consumer_process = [];                                                      
    for i in range(n_consumers):                                                
        p = Process(
            target=consumer, 
            args=(frame_queue, result_queue, i, process_fun,),
            daemon=True) # allow consumers to be closed when queue is empty
        consumer_process.append(p)                                              
        p.start()

    producer_process = Process(target=producer, 
                        args=(videofile,use_gpu,frame_queue,result_queue,))    
    producer_process.start()

    # wait for producers to terminate
    try:
        producer_process.join()
    except KeyboardInterrupt:
        producer_process.terminate()
        producer_process.join()

    return result_queue.get()

if __name__ == "__main__":
    
    videofile, gpu, pfun, n_consumers, qsize = utils.parse_arguments()
    
    frame_queue = JoinableQueue(maxsize = qsize)
    result_queue = Queue()
    
    num_frames = 0
    start_time = time.time()
    num_frames = start(
        frame_queue, 
        result_queue, 
        videofile, 
        n_consumers, 
        pfun,
        gpu
    )
    stop_time = time.time()
    duration = stop_time - start_time
    fps = num_frames/duration

    print("num frames : " + str(num_frames) + ", duration : " + str(duration) + ", FPS : " + str(fps))
