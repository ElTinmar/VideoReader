# Optimize machine vision processing of video files

Using a multiprocessed producer-consumer scheme instead of the naive sequential read-process approach can yield significant improvements 
in overall speed if the processing task is long. For shorter processing tasks, the overhead introduced by the multiprocessing approach 
results in no benefits or even worse performance than the sequential approach

* download test video 

```
$ sudo pip install youtube-dl
$ youtube-dl --format "best[ext=mp4][protocol=https]" https://www.youtube.com/watch?v=9eiaiVthVrk -o jumanji.mp4
```

* Naive processing of images

``` python
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
```

* Multiprocessing producer-consumer scheme

``` python
from multiprocessing import Process, Queue, JoinableQueue
import cv2
import time
import os
import queue

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
        
def start(frame_queue, result_queue, videofile, n_consumers=1, use_gpu=False):
    """spawn all the processes"""

    # start consumers and producers                                             
    consumer_process = [];                                                      
    for i in range(n_consumers):                                                
        p = Process(
            target=consumer, 
            args=(frame_queue, result_queue, i, process,),
            daemon=True) # allow consumers to be closed when queue is empty
        consumer_process.append(p)                                              
        p.start()

    producer_process = Process(target=producer, 
                        args=(videofile,use_gpu,frame_queue,))    
    producer_process.start()

    # wait for producers to terminate                             
    producer_process.join()

def process(frame,frame_num,frame_queue,result_queue):
    """actual image processing code goes here"""
    
    # simulate long processing task
    time.sleep(0.1)
    print((frame_queue.qsize(), frame_num))

if __name__ == "__main__":
    
    # set parameters
    frame_queue = JoinableQueue(maxsize = 2048)
    result_queue = Queue()
    videofile = '/home/martin/jumanji.mp4'
    n_consumers = 1

    start(frame_queue, result_queue, videofile, n_consumers, use_gpu=False)
```

* Results

Using time.sleep as a synthetic load (not CPU intensive)

Hardware:
Intel(R) Core(TM) i5-2500S CPU @ 2.70GHz (4 cores, 4 threads)  
Intel® HD Graphics 2000  
12 GB of 1333 MHz DDR3  

Execution times were collected using:

| Command | Processing time per frame | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- | --- |
| time python3 naive.py | 100 ms | NA | No | 6m47,355s |
| time python3 producer_consumer.py | 100 ms | 1 | No | 6m46,246s |
| time python3 producer_consumer.py | 100 ms | 2 | No | 3m23,020s |
| time python3 producer_consumer.py | 100 ms | 3 | No | 2m15,463s |
| time python3 producer_consumer.py | 100 ms | 4 | No | 1m41,924s |
| time python3 producer_consumer.py | 100 ms | 5 | No | 1m21,792s |
| time python3 producer_consumer.py | 100 ms | 10 | No | 0m43,272s |
| time python3 producer_consumer.py | 100 ms | 15 | No | 0m38,774s |
| time python3 producer_consumer.py | 100 ms | 20 | No | 1m9,684s |
| time python3 naive.py | 10 ms | NA | No | 0m52,553s |
| time python3 producer_consumer.py | 10 ms | 1 | No | 0m51,554s |
| time python3 producer_consumer.py | 10 ms | 2 | No | 0m29,503s |
| time python3 producer_consumer.py | 10 ms | 5 | No | 0m28,546s |
| time python3 producer_consumer.py | 10 ms | 10 | No | 0m48,809s |
| time python3 naive.py | 1 ms | NA | No | 0m19,729s |
| time python3 producer_consumer.py | 1 ms | 1 | No | 0m24,054s |
| time python3 producer_consumer.py | 1 ms | 2 | No | 0m22,645s |
| time python3 producer_consumer.py | 1 ms | 3 | No | 0m26,689s |

