import numpy as np
import time
import argparse
import cv2
import os
import struct 

def int32_to_uint8x4(n):
    int32 = struct.pack("I", n)
    return struct.unpack("B" * 4, int32)

def uint8x4_to_int32(u0,u1,u2,u3):
    int32 = struct.pack('BBBB',u0,u1,u2,u3)
    return struct.unpack("I", int32)[0]

def busy_wait(dt):
    current_time = time.time()
    while (time.time() < current_time+dt):
        pass

def do_nothing(frame,frame_num):
    #print(frame_num)
    pass

def synthetic_load_light(frame,frame_num):
    time.sleep(0.1) 
    #print(frame_num)
    
def synthetic_load_single_core(frame,frame_num):
    busy_wait(0.1) 
    #print(frame_num)

def synthetic_load_multi_core(frame,frame_num):
     # CPU intensive multithreaded (tune with OMP_NUM_THREADS) 
    if type(frame) == cv2.cuda.GpuMat:
        raise TypeError('frame in GPU mem, use --host option') 
    else:
        try:
            frame32 = np.float32(frame)                                                 
            u, s, vh = np.linalg.svd(frame32)
            #print(frame_num)
        except np.linalg.LinAlgError:
            pass
            #print(str(frame_num) + ' SVD did not converge')

def time_exec(fun):
    startTime = time.time()
    ret = fun()
    stopTime = time.time()
    duration = stopTime - startTime
    return ret, duration

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
        '--gpu',
        action = 'store_true',
        help = 'Use GPU for hardware acceleration'
    )
    parser.add_argument(
        '--cvcuda',
        action = 'store_true',
        help = 'Use GPU via opencv cuda interface'
    )
    parser.add_argument(
        '--host',
        action = 'store_true',
        help = 'Get image data from GPU to host'
    )

    args = parser.parse_args()

    # check that video file exists
    if not os.path.exists(args.videofile):
        raise FileNotFoundError

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

    return (
        args.videofile, 
        args.gpu, 
        pfun, 
        args.cvcuda, 
        args.host, 
        args.n, 
        args.queuesize  
    )
