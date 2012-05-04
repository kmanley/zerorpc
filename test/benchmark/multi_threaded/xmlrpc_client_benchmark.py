import sys
sys.path.append("..")
from xpersec import XPerSec
import xmlrpclib
import threading

counter = XPerSec("calls") 

def thread_func():
    ITERS = 10000
    s = xmlrpclib.ServerProxy('http://localhost:8000')
    for i in range(ITERS):
        result = s.mult(i, i+1)
        assert result == (i * (i+1)), (result, i*(i+1))
        counter.incr()
    
threads = []    
NUM_THREADS = 5
for i in range(NUM_THREADS):
    threads.append(threading.Thread(target=thread_func))
    threads[-1].start()

for thread in threads:
    thread.join()
    