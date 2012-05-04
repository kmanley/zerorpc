import sys
sys.path.append(r"..")
from xpersec import XPerSec
sys.path.append(r"..\..\..\..")
import zerorpc.client

counter = XPerSec("calls") 

s = zerorpc.client.ZeroRpcClient("tcp://localhost:5555")

ITERS = 40000
for i in range(ITERS):
    result = s.mult(i, i+1)
    assert result == (i * (i+1)), (result, i*(i+1))
    counter.incr()
    
