# Optimize machine vision processing of video files

TL/DR

- Matlab is slow 
- Using a multiprocessed producer-consumer scheme instead of the naive sequential read-process approach can yield significant improvements 
in overall speed if the processing task is long and not already multithreaded. 
- For short processing tasks, the overhead introduced by the multiprocessing approach results in no clear benefits or even worse performance than the sequential approach 
- If the task is already multithreaded (e.g. SVD from openBLAS), using several consumer thread processes can be worse
- If the task is already multithreaded (e.g. SVD from openBLAS), reducing OMP_NUM_THREADS (controls the number of parrallel threads for openBLAS) and increasing the number of consumers may increase performance
- TO RETEST There is no clear speed gain when using hardware acceleration to decode frames from the video file
- TO TEST Running the consumer processing code on the GPU when possible can yield a significant speed-up 
- TO TEST You may need parallel producers (read several video chunks at the esame time) if you are doing some very light processing (e.g. just counting the number of frames)

General advice

- Keep an eye on `top` or `htop` to see if all cores are in use
- Keep an eye on the size of the producer queue 

## download test video 

```
$ sudo pip install youtube-dl
$ youtube-dl --format "best[ext=mp4][protocol=https]" https://www.youtube.com/watch?v=9eiaiVthVrk -o jumanji.mp4
```

## Naive processing of images

In Matlab

``` matlab
mov = VideoReader('jumanji.mp4');
num_frame = 0;
while mov.hasFrame()
    frame = mov.readFrame();
    frame_gray = frame(:,:,1);
    num_frame = num_frame+1;
    
    pause(0.1);
    disp(num_frame);
end
```

In Python

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

## Multiprocessing producer-consumer scheme

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

## Results

Hardware:  
Intel(R) Core(TM) i5-2500S CPU @ 2.70GHz (4 cores, 4 threads)   
Intel® HD Graphics 2000   
12 GB of 1333 MHz DDR3   

### Using time.sleep as a synthetic load (not CPU intensive)

| Command | Wait duration | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- | --- |
| matlab -nodesktop -r "tic; run('naive.m'); toc; exit;" | 100 ms | NA | No | 7m06,613s |
| time python3 naive.py | 100 ms | NA | No | 6m47,355s |
| time python3 producer_consumer.py | 100 ms | 1 | No | 6m46,246s |
| time python3 producer_consumer.py | 100 ms | 2 | No | 3m23,020s |
| time python3 producer_consumer.py | 100 ms | 3 | No | 2m15,463s |
| time python3 producer_consumer.py | 100 ms | 4 | No | 1m41,924s |
| time python3 producer_consumer.py | 100 ms | 5 | No | 1m21,792s |
| time python3 producer_consumer.py | 100 ms | 10 | No | 0m43,272s |
| time python3 producer_consumer.py | 100 ms | 15 | No | 0m38,774s :heavy_check_mark: |
| time python3 producer_consumer.py | 100 ms | 20 | No | 1m9,684s |
| time python3 naive.py | 10 ms | NA | No | 0m52,553s |
| time python3 producer_consumer.py | 10 ms | 1 | No | 0m51,554s |
| time python3 producer_consumer.py | 10 ms | 2 | No | 0m29,503s |
| time python3 producer_consumer.py | 10 ms | 5 | No | 0m28,546s :heavy_check_mark: |
| time python3 producer_consumer.py | 10 ms | 10 | No | 0m48,809s |
| time python3 naive.py | 1 ms | NA | No | 0m19,729s |
| time python3 producer_consumer.py | 1 ms | 1 | No | 0m24,054s :skull: |
| time python3 producer_consumer.py | 1 ms | 2 | No | 0m22,645s :skull: |
| time python3 producer_consumer.py | 1 ms | 3 | No | 0m26,689s :skull: |


### Using busy_wait as a synthetic load (CPU intensive, single core)

``` python
def busy_wait(dt):   
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass

def process(frame,frame_num):
    """actual image processing code goes here"""
    
    busy_wait(0.1)
    print(frame_num)
```


| Command | Wait duration | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- | --- |
| time python3 naive.py | 100 ms | NA | No | 6m42,774s :skull: |
| time python3 producer_consumer.py | 100 ms | 1 | No | 6m42,629s |
| time python3 producer_consumer.py | 100 ms | 2 | No | 3m24,008s |
| time python3 producer_consumer.py | 100 ms | 5 | No | 1m29,378s |
| time python3 producer_consumer.py | 100 ms | 10 | No | 0m56,405s :heavy_check_mark: |
| time python3 producer_consumer.py | 100 ms | 15 | No | 1m11,180s |

### Using SVD as a synthetic load (CPU intensive, multicore)

Make sure that numpy is using a multi-threaded BLAS library such as openBLAS. On ubuntu

```
sudo apt install libopenblas-base libopenblas-dev
```

``` python
import numpy as np

def process(frame,frame_num):
    """actual image processing code goes here"""
    
    frame32 = np.float32(frame)                                                 
    u, s, vh = np.linalg.svd(frame32)
    print(frame_num)
```

| Command | #Consumers | Hardware acceleration | Real time |
| --- | --- | --- | --- |
| time python3 naive.py | NA | No | 37m22,286s |
| time python3 producer_consumer.py | 1 | No | 37m36,874s |
| time python3 producer_consumer.py | 5 | No | 55m59,641s :skull: |

Hardware:  
2x Intel(R) Xeon(R) Gold 5220 CPU @ 2.20GHz (36 cores, 72 threads)  
NVIDIA GeForce RTX 2080 Ti  
64GB (4x16GB) DDR4 2933 MHz  

| Command | Method | Wait duration | #Consumers | Hardware acceleration | Real time | Comments |
| --- | --- | --- | --- | --- | --- | --- |
| time python3 naive.py | time.sleep | 100 ms | NA | No | 6m48,654s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 15 | No | 0m28,396s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 30 | No | 0m15,574s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 60 | No | 0m13,529s | |
| time python3 producer_consumer.py | time.sleep | 100 ms | 100 | No | 2m9,737s | |
| time python3 naive.py | SVD | NA | NA | No | 9m21,224s | openBLAS is using 36 cores |
| OMP_NUM_THREADS=1 time python3 naive.py | SVD | NA | NA | No | 22m54,347s |  |
| OMP_NUM_THREADS=5 time python3 naive.py | SVD | NA | NA | No | 7m47,355s |  |
| OMP_NUM_THREADS=10 time python3 naive.py | SVD | NA | NA | No | 7m27,554s |  |
| OMP_NUM_THREADS=15 time python3 naive.py | SVD | NA | NA | No | 7m33,004s |  |
| OMP_NUM_THREADS=25 time python3 naive.py | SVD | NA | NA | No | 9m27,125s |  |
| OMP_NUM_THREADS=36 time python3 naive.py | SVD | NA | NA | No | 9m37,050s |  |
| time python3 producer_consumer.py | SVD | NA | 1 | No | x | |
| time python3 producer_consumer.py | SVD | NA | 2 | No | 5m45,433s | |
| OMP_NUM_THREADS=1 time python3 producer_consumer.py | SVD | NA | 40 | No | 4m3,459s | |
| OMP_NUM_THREADS=5 time python3 producer_consumer.py | SVD | NA | 10 | No | 1m37,042s | |
| OMP_NUM_THREADS=5 time python3 producer_consumer.py | SVD | NA | 12 | No | 1m31,409s | |

# Cool stuff

deeplabcut/utils/auxfun_videos.py
