from threading import Thread
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import RawArray, RawValue
import time

class SharedRingBuffer:
    
    def __init__(
        self, 
        maxNumItems, 
        itemSize, 
    ):
        ''' Allocate shared array '''
        
        self.maxNumItems = maxNumItems
        self.itemSize = itemSize
        self.totalSize = maxNumItems*itemSize
        self.data = RawArray('B',maxNumItems*itemSize)
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
        # TODO check type
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
       
        idx_start = self.write_cursor.value
        idx_stop = idx_start + self.itemSize
        # update buffer, use memoryview for direct buffer access 
        memoryview(self.data).cast('B')[idx_start:idx_stop] = item
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
        item = memoryview(self.data).cast('B')[idx_start:idx_stop]
        # update read cursor
        self.read_cursor.value = idx_stop % self.totalSize
        self.rLock.release()

        return True, item

    def size(self):
        ''' Return number of items currently stored in the buffer '''
        return (
            (self.write_cursor.value - self.read_cursor.value) % self.totalSize
            )

    
