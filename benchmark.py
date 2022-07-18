#!/usr/bin/env python3

import time
import subprocess
import os

my_env = os.environ.copy()

videofile = '../jumanji_short.mp4'

for omp in range(1,17):
    
    # MATLAB naive
    start = time.time()
    subprocess.run(
         ['matlab',
         '-nodesktop',
         '-nosplash',
         '-r',
         "naive('../jumanji_short.mp4'," + str(omp) + "); exit"],
         capture_output=True
    )
    stop = time.time()
    duration = (stop-start)                                             
    print("naive('../jumanji_short.mp4'," + str(omp) + "); exit : " + str(duration))

    # Python naive 
    for gpu in [True, False]:
        my_env['OMP_NUM_THREADS'] = str(omp)
        start = time.time()
        if gpu:
            subprocess.run(
                ['./naive.py','../jumanji_short.mp4','--gpu'],
                env=my_env,
                capture_output=True
            )
            stop = time.time()
            duration = (stop-start)
            print('OMP_NUM_THREADS=' + str(omp) + ' ./naive.py ../jumanji_short.mp4 --gpu : ' + str(duration))
        else:
            subprocess.run(
                ['./naive.py','../jumanji_short.mp4'],
                env=my_env,
                capture_output=True
            ) 
            stop = time.time()
            duration = (stop-start)
            print('OMP_NUM_THREADS=' + str(omp) + ' ./naive.py ../jumanji_short.mp4 : ' + str(duration))


for n_consumers in range(1,17):
    for omp in range(1 ,17):
        my_env['OMP_NUM_THREADS'] = str(omp)
        for gpu in [True, False]:
            start = time.time()
            if gpu:
                subprocess.run(
                    ['./producer_consumer.py',
                    '../jumanji_short.mp4',
                    '-n ' + str(n_consumers),
                    '--gpu'],
                    env=my_env,
                    capture_output=True
                )
                stop = time.time()
                duration = stop-start
                print('OMP_NUM_THREADS=' + str(omp) + ' ./producer_consumer.py ../jumanji_short.mp4 -n ' + str(n_consumers) + ' --gpu : ' + str(duration))
            else:
                subprocess.run(
                    ['./producer_consumer.py', 
                    '../jumanji_short.mp4',
                    '-n ' + str(n_consumers)],
                    env=my_env,
                    capture_output=True
                )
                stop = time.time()
                duration = stop-start
                print('OMP_NUM_THREADS=' + str(omp) + './producer_consumer.py ../jumanji_short.mp4 -n ' + str(n_consumers) + ' : ' + str(duration))
