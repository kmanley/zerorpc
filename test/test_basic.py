import unittest
import sys
sys.path.append(r"..\..")
import zerorpc.server
import zerorpc.client

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO) 

class TestZeroRpc(unittest.TestCase):
    def __del__(self):
        self.server.shutdown()
        
    def setUp(self):
        self.server = zerorpc.server.ZeroRpcServer()
        self.server.start(3, blocking=False)
        self.client = zerorpc.client.ZeroRpcClient("tcp://localhost:5555")
        
    def tearDown(self):
        self.server.shutdown()

    def testMult(self):        
        def mult(a, b):
            return a * b

        self.server.unregister_all()        
        self.server.register_function(mult, name="my.namespace.mult")
        result = self.client.my.namespace.mult(5, 7)
        self.assertEqual(result, 35)
        
    def testMissingFunc(self):
        self.server.unregister_all()
        try:
            result = self.client.my.namespace.mult(5, 7)
        except Exception, e:
            self.assertEqual(e.error_type, "KeyError")
        
    def testMultiCall(self):
        def reverse(s):
            return s[::-1]

        self.server.unregister_all()        
        self.server.register_function(reverse)
        multicall = zerorpc.client.MultiCall(self.client)
        for i in range(5):
            multicall.reverse("string %d" % i)
        for i, result in enumerate(multicall()):
            #print result
            assert result == ("string %d" % i)[::-1]
            
    def testInstance(self):
        class Foobar(object):
            @zerorpc.server.exposed
            def subtract(self, a, b):
                return a - b
            @zerorpc.server.exposed
            def add(self, x, y):
                return x + y
    
        self.server.unregister_all()
        self.server.register_instance(Foobar(), "my.cool.namespace")
        result = self.client.my.cool.namespace.subtract(5, 7)
        self.assertEqual(result, -2)
        result = self.client.my.cool.namespace.add(2, 9)
        self.assertEqual(result, 11)
        
    def testServerException(self):
        class OddException(Exception):
            pass    
        
        def odd_raiser(x):
            if x % 2 == 0:
                return x
            else:
                raise OddException("x is odd!")
    
        self.server.unregister_all()
        self.server.register_function(odd_raiser, "my_namespace.raise_if_odd")
        result = self.client.my_namespace.raise_if_odd(4)
        self.assertEqual(result, 4)
        try:
            result = self.client.my_namespace.raise_if_odd(3)
        except Exception, e:
            self.assertEqual(e.error_type, "OddException")

if __name__ == "__main__":
    unittest.main()
    