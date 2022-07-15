#!/usr/bin/env python3

from multiprocessing import Process, Queue, JoinableQueue
import cv2
import time
import os
import queue
import numpy as np
import argparse

def producer(path, use_gpu, frame_queue):
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
    # Wait until queue is emptied by consumers 
    frame_queue.join()

def consumer(frame_queue, result_queue, process_num, process_fun):
    """process images from the queue """

    while True: 
        try:
            # get frame and frame number from the queue
            frame, frame_num = frame_queue.get(block=False)                                                                                                             
            # do some processing
            process_fun(frame,frame_num,frame_queue,result_queue)
            
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
                        args=(videofile,use_gpu,frame_queue,))    
    producer_process.start()

    # wait for producers to terminate
    try:
        producer_process.join()
    except KeyboardInterrupt:
        producer_process.terminate()
        producer_process.join()
   
def busy_wait(dt):   
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass    

def synthetic_load_light(frame,frame_num,frame_queue,result_queue):
    time.sleep(0.1) 
    print((frame_queue.qsize(), frame_num))
    
def synthetic_load_single_core(frame,frame_num,frame_queue,result_queue):
    busy_wait(0.1) 
    print((frame_queue.qsize(), frame_num))

def synthetic_load_multi_core(frame,frame_num,frame_queue,result_queue):
     # CPU intensive multithreaded (tune with OMP_NUM_THREADS) 
    try:
        frame32 = np.float32(frame)                                                 
        u, s, vh = np.linalg.svd(frame32)
        print((frame_queue.qsize(), frame_num))
    except np.linalg.LinAlgError: 
        print(str(frame_num) + ' SVD did not converge')

def process(frame,frame_num,frame_queue,result_queue):
    """actual image processing code goes here"""
    print((frame_queue.qsize(), frame_num))

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Benchmark producer-consumer video reader'
    )
    parser.add_argument(
        'videofile', 
        type = str,
        help = 'Path to the video'
    )
    parser.add_argument(
        '-n',
        type = int,
        default = 1,
        help = 'number of consumer processes'
    )
    parser.add_argument(
        '--queuesize',
        '-q',
        default = 2048,
        type = int,
        help = 'Max size of the frame buffer'
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

    qsize = args.queuesize
    n_consumers = args.n

    frame_queue = JoinableQueue(maxsize = qsize)
    result_queue = Queue()
    n_consumers = args.n
    gpu = args.gpu
    
    if (args.load == "MC"):
        pfun = synthetic_load_multi_core
    elif (args.load == "SC"):
        pfun = synthetic_load_single_core
    elif (args.load == "L"):                                                
        pfun = synthetic_load_light
    else:
        raise ValueError

    start(
        frame_queue, 
        result_queue, 
        videofile, 
        n_consumers, 
        pfun,
        gpu
    )
