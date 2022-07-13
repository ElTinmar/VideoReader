from multiprocessing import Process
from multiprocessing import Queue
import cv2
import time
import os

def producer(path,use_gpu,Q,timeout,max_retry):
        if use_gpu:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="video_codec;h264_cuvid"

        stream = cv2.VideoCapture(path)
        frame_num = 0
        retry = 0
        
        while True:
            if not Q.full():
                # Queue is not full, grab frames 
                grabbed, frame = stream.read()
                if not grabbed:
                    break
                
                frame_num += 1
                Q.put((frame, frame_num))
            else:
                # Queue is full, wait for consumers
                while Q.full() and retry < max_retry:
                    time.sleep(timeout)
                    retry += 1

                if retry == max_retry:
                    break
                else:
                    retry = 0
        
        # close even if the queue is not empty
        print(Q.get())
        Q.cancel_join_thread()
        stream.release()

def consumer(Q,process_num,timeout,max_retry):
    window_name = 'Display ' + str(process_num)                              
    cv2.namedWindow(window_name)                                            
    prev_frame_time = 0                                                     
    curr_frame_time = 0                                                     
    retry = 0

    while True: 
        if not Q.empty():
            # get frame and frame number from the queue
            frame, frame_num = Q.get()                                                                                                             
        
            # process images here 
            new_frame_time = time.time()                                        
            fps = 1/(new_frame_time - prev_frame_time)                          
            prev_frame_time = new_frame_time                                    
        
            cv2.putText(frame,str(int(fps)), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA) 
            cv2.putText(frame,str(int(Q.qsize())), (7, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame,str(frame_num), (200, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 1, cv2.LINE_AA)
            cv2.imshow(window_name,frame)                                       
            key = cv2.waitKey(1)                                                
            if key == ord('q'):                                                 
                break

        else:
            # Queue is empty, wait for producer
            while Q.empty() and retry < max_retry:
                time.sleep(timeout)
                retry += 1
           
            if retry == max_retry:
                break
            else:
                retry = 0
    
    cv2.destroyWindow(window_name)

# set parameters
use_gpu = False
Q = Queue(maxsize = 2048)
videofile = '/home/martin/Desktop/forEmi/2021_07_26_B.avi'
n_consumers = 1
timeout = 0.01
max_retry = 200

# start consumers and producers
consumer_process = [];
for i in range(n_consumers):
    p = Process(target=consumer, args=(Q,i,timeout,max_retry,))
    consumer_process.append(p)
    p.start()

start = time.time()
producer_process = Process(target=producer, args=(videofile,use_gpu,Q,timeout,max_retry,))
producer_process.start()

# wait for producers and consumers to terminate
producer_process.join()
for i in range(n_consumers):
    consumer_process[i].join()

stop = time.time()
duration = stop - start
print(duration)
