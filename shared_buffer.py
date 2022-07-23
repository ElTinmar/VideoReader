from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import RawArray, RawValue
from ctypes import c_int
import time
import numpy as np

class SharedRingBuffer:
    
    def __init__(
        self, 
        maxNumItems, 
        itemSize, 
        shared_array, 
        shared_lock, 
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
        self.lock = shared_lock

    def full(self):
        return self.write_cursor.value == ((self.read_cursor.value - self.itemSize) % self.totalSize)

    def empty(self):
        return self.write_cursor.value == self.read_cursor.value

    def push(self, item, block=False, timeout=0.1):
        ''' Add item at the back '''

        # check that item is the right size/type other throw ValueError

        self.lock.acquire()

        # if buffer is full wait until data is read
        if block:
            while self.full():
                self.lock.release()
                time.sleep(0.1)
                self.lock.acquire()
        else:
            tStart = tNow = time.monotonic()
            while self.full() and tNow-tStart < timeout:
                self.lock.release()
                time.sleep(0.1)
                tNow = time.monotonic()
                self.lock.acquire()
            
            if tNow-tStart >= timeout: # timeout occured
                self.lock.release()
                return
    
        # add item
        self.data[self.write_cursor.value:self.write_cursor.value+self.itemSize] = item
        
        # update write cursor
        self.write_cursor.value = (self.write_cursor.value + self.itemSize) % self.totalSize
        
        self.lock.release()

    def pop(self, block=False, timeout=0.1):
        ''' Return item from the front '''
        
        self.lock.acquire()

        # check if buffer is not empty
        if block:
            while self.empty():
                self.lock.release()
                time.sleep(0.1)
                self.lock.acquire()
        else:
            tStart = tNow = time.monotonic()
            while self.empty() and tNow-tStart < timeout:
                self.lock.release()
                time.sleep(0.1)
                tNow = time.monotonic()
                self.lock.acquire()

            if tNow-tStart >= timeout: # timeout occured
                self.lock.release()
                return (False, [])

        # fetch item
        item = self.data[self.read_cursor.value:self.read_cursor.value+self.itemSize]

        # update read cursor
        self.read_cursor.value = (self.read_cursor.value + self.itemSize) % self.totalSize
        
        self.lock.release()

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

    
