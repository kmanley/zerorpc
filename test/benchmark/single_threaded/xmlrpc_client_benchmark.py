import sys
sys.path.append("..")
from xpersec import XPerSec
import xmlrpclib

counter = XPerSec("calls") 

s = xmlrpclib.ServerProxy('http://localhost:8000')

ITERS = 20000
for i in range(ITERS):
    result = s.mult(i, i+1)
    assert result == (i * (i+1)), (result, i*(i+1))
    counter.incr()
    
