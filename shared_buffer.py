from threading import Thread
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import RawArray, RawValue
from ctypes import c_int
import time
import numpy as np
import cProfile

class SharedRingBuffer:
    
    def __init__(
        self, 
        maxNumItems, 
        itemSize, 
        shared_array, 
        shared_wlock,
        shared_rlock,
        write_cursor,
        read_cursor
    ):
        ''' Allocate shared array '''
        
        self.maxNumItems = maxNumItems
        self.itemSize = itemSize
        self.totalSize = maxNumItems*itemSize
        self.data = shared_array
        self.write_cursor = write_cursor
        self.read_cursor = read_cursor
        self.rLock = shared_rlock
        self.wLock = shared_wlock
        self._debug = False

    def full(self):
        return self.write_cursor.value == ((self.read_cursor.value - self.itemSize) % self.totalSize)

    def empty(self):
        return self.write_cursor.value == self.read_cursor.value

    def check(self,item):
        pass

    def push(self, item, block=False, timeout=0.1):
        ''' Add item at the back '''
        
        # check that item is the right size/type
        self.check(item)

        self.wLock.acquire()

        # if buffer is full wait until data is read
        if block:
            while self.full():
                self.wLock.release()
                time.sleep(timeout)
                self.wLock.acquire()
        else:
            tStart = tNow = time.monotonic()
            while tNow-tStart < timeout and self.full():
                self.wLock.release()
                time.sleep(timeout)
                tNow = time.monotonic()
                self.wLock.acquire()
            
            if tNow-tStart >= timeout: # timeout occured
                self.wLock.release()
                return
    
        # add item
        tStrt = time.monotonic()
        memoryview(self.data).cast('B')[self.write_cursor.value:self.write_cursor.value+self.itemSize] = item
        if self._debug: print("Pushing took {0}".format(time.monotonic()-tStrt))
        
        # update write cursor
        self.write_cursor.value = (self.write_cursor.value + self.itemSize) % self.totalSize
        
        self.wLock.release()

    def pop(self, block=False, timeout=0.1):
        ''' Return item from the front '''

        self.rLock.acquire()

        # check if buffer is not empty
        if block:
            while self.empty():
                self.rLock.release()
                time.sleep(timeout)
                self.rLock.acquire()
        else:
            tStart = tNow = time.monotonic()
            while self.empty() and tNow-tStart < timeout:
                self.rLock.release()
                time.sleep(timeout)
                tNow = time.monotonic()
                self.rLock.acquire()

            if tNow-tStart >= timeout: # timeout occured
                self.rLock.release()
                return (False, [])

        # fetch item
        tStrt = time.monotonic()
        item = memoryview(self.data).cast('B')[self.read_cursor.value:self.read_cursor.value+self.itemSize]
        if self._debug: print("Poping took {0}".format(time.monotonic()-tStrt))

        # update read cursor
        self.read_cursor.value = (self.read_cursor.value + self.itemSize) % self.totalSize
        
        self.rLock.release()

        return True, item

    def size(self):
        ''' Return number of items currently stored in the buffer '''
        return (self.write_cursor.value - self.read_cursor.value)%self.totalSize

def writer(M, sz, shr_array, lock, wc, rc):
    buf = SharedRingBuffer(M,sz,shr_array,lock,wc,rc)
    buf.push([1])
    time.sleep(2)
    ok, val = buf.pop()
    if ok:
        print(val)

def reader(M, sz, shr_array, lock, wc, rc):
    buf = SharedRingBuffer(M,sz,shr_array,lock,wc,rc)
    ok, val = buf.pop()
    if ok:
        print(val)
    buf.push([2])
    
if __name__ == '__main__':

    itemSize = 1
    maxNumItems = 10
    l = Lock()
    A = RawArray('i',maxNumItems*itemSize)
    wc = RawValue('i',0)
    rc = RawValue('i',0)
    w = Process(target=writer, args=(maxNumItems,itemSize,A,l,wc,rc)) 
    r = Process(target=reader, args=(maxNumItems,itemSize,A,l,wc,rc)) 
    w.start()
    r.start()
    w.join()
    r.join()

    
