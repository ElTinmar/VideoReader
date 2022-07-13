from multiprocessing import Process, Queue, Lock
import cv2
import time
import os

def producer(path, use_gpu, frame_queue, timeout, max_retry):
    """get images from file and put them in a queue"""

    if use_gpu:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"

    stream = cv2.VideoCapture(path)
    frame_num = 0
    retry = 0
        
    while True:
        if not frame_queue.full():
            # Queue is not full, grab frames 
            grabbed, frame = stream.read()
            if not grabbed:
                break
                
            frame_num += 1
            frame_queue.put((frame, frame_num))
        else:
            # Queue is full, wait for consumers
            while frame_queue.full() and retry < max_retry:
                time.sleep(timeout)
                retry += 1

            if retry == max_retry:
                break
            else:
                retry = 0
        
    # close even if the queue is not empty
    frame_queue.cancel_join_thread()
    stream.release()

def consumer(frame_queue, result_queue, lock, process_num, timeout, max_retry, 
            process_fun):
    """process images from the queue """

    retry = 0

    while True:
        lock.acquire()
        if not frame_queue.empty():
            # get frame and frame number from the queue
            frame, frame_num = frame_queue.get_nowait()
            lock.release()

            # do some processing
            process_fun(frame,frame_num,frame_queue,result_queue)

        else:
            lock.release()

            # Queue is empty, wait for producer
            while frame_queue.empty() and retry < max_retry:
                time.sleep(timeout)
                retry += 1
           
            if retry == max_retry:
                break
            else:
                retry = 0
    
def start(frame_queue, result_queue, lock, videofile, n_consumers=1, 
          timeout=0.01, max_retry=200, use_gpu=False):
    """spawn all the processes"""

    # start consumers and producers                                             
    consumer_process = [];                                                      
    for i in range(n_consumers):                                                
        p = Process(
        target=consumer, 
        args=(frame_queue, result_queue, lock, i, timeout, max_retry, process)
        )
        consumer_process.append(p)                                              
        p.start()

    producer_process = Process(target=producer, 
                        args=(videofile,use_gpu,frame_queue,timeout,max_retry,))    
    producer_process.start()

    # wait for producers and consumers to terminate                             
    for i in range(n_consumers):                                                
        consumer_process[i].join()                                              
    producer_process.join()

def process(frame,frame_num,frame_queue,result_queue):
    """actual image processing code goes here"""
    
    print((frame_queue.qsize(), frame_num))

if __name__ == "__main__":
    
    # set parameters
    lock = Lock()
    frame_queue = Queue(maxsize = 2048)
    result_queue = Queue()
    videofile = '/home/martin/jumanji.mp4'
    n_consumers = 10

    start(frame_queue, result_queue, lock, videofile, 
        n_consumers, use_gpu=False)
