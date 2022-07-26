from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import RawArray, RawValue
import time
import numpy as np

class SharedRingBuffer:
    
    def __init__(
        self, 
        maxNumItems, 
        itemSize = 1,
        buftype = 'B'
    ):
        ''' Allocate shared array '''
        
        #TODO check input args type/size/values

        self.maxNumItems = maxNumItems
        self.itemSize = itemSize
        self.totalSize = maxNumItems*itemSize
        self.buftype = buftype
        self.data = RawArray(buftype, maxNumItems*itemSize)
        self.write_cursor = RawValue('i',0)
        self.read_cursor = RawValue('i',0)
        self.rLock = Lock()
        self.wLock = Lock()
        self._debug = False

    def full(self):
        return self.write_cursor.value == (
            (self.read_cursor.value - self.itemSize) % self.totalSize
            )

    def empty(self):
        return self.write_cursor.value == self.read_cursor.value

    def check(self,item):
        # TODO check size
        # TODO check type, has to be a bytes object (np array with ndim = 1 works)
        
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
        
        # update buffer, use memoryview for direct buffer access 
        idx_start = self.write_cursor.value
        idx_stop = idx_start + self.itemSize
        if self.buftype == 'B':
            mview = memoryview(self.data).cast('B')
        elif self.buftype == 'i':
            mview = memoryview(self.data).cast('B').cast('i')
        
        if self.itemSize == 1:
            mview[idx_start] = item
        else:
            mview[idx_start:idx_stop] = item
        
        # update write cursor
        self.write_cursor.value = idx_stop % self.totalSize
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

        idx_start = self.read_cursor.value
        idx_stop = idx_start + self.itemSize
        # fetch item, use memoryview for direct buffer access
        if self.buftype == 'B':
            mview = memoryview(self.data).cast('B')
        elif self.buftype == 'i':
            mview = memoryview(self.data).cast('B').cast('i')

        # make a copy outside of the buffer before you return it     
        if self.itemSize == 1:
            item = mview[idx_start]
        else:
            item = np.array(mview[idx_start:idx_stop],copy=True)
        
        # update read cursor
        self.read_cursor.value = idx_stop % self.totalSize
        self.rLock.release()

        return True, item

    def size(self):
        ''' Return number of items currently stored in the buffer '''
        return (
            (self.write_cursor.value - self.read_cursor.value) % self.totalSize
            )

    
