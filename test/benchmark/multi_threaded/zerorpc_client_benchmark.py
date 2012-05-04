import threading
import sys
sys.path.append(r"..")
from xpersec import XPerSec
sys.path.append(r"..\..\..\..")
import zerorpc.client

counter = XPerSec("calls") 

def thread_func():
    ITERS = 40000
    s = zerorpc.client.ZeroRpcClient("tcp://localhost:5555")
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
    