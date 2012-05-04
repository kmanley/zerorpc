import unittest
import sys
sys.path.append(r"..\..\..\..")
import zerorpc.server

def mult(a, b):
    return a * b

server = zerorpc.server.ZeroRpcServer()
server.register_function(mult)
server.start(5, blocking=True)

