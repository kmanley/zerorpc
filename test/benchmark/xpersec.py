import time
import threading
lock = threading.RLock()

class XPerSec:
    def __init__(self, things):
        self.things = things
        self.start = time.clock()
        self.count = 0

    def incr(self):
        lock.acquire()
        try:
            now = time.clock()
            elapsed = now - self.start
            if elapsed > 1.0:
                print("%.2f %s/sec" % (self.count/elapsed, self.things)) 
                self.count = 1
                self.start = now
            else:
                self.count += 1
        finally:
            lock.release()