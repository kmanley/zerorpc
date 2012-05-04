import zmq
import logging
log = logging.getLogger("zerorpc.client")

class Error(Exception):
    def __init__(self, error_type, message, tb):
        self.error_type = error_type
        self.message = message
        self.traceback = tb
    def __repr__(self):
        return "%s('%s')" % (self.error_type, self.message)
    __str__ = __repr__ 

# NOTE: _Method and _MultiCall stuff adapted (ripped off) from stdlib xmlrpclib
class _Method:
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, *args, **kwargs):
        result = self.__send(self.__name, *args, **kwargs)[0]
        if result["success"]:
            return result["result"]
        else:
            raise Error(result["error_type"], result["message"], result["traceback"])

class MultiCallIterator:
    def __init__(self, results):
        self.results = results
    def __getitem__(self, i):
        result = self.results[i]
        if result["success"]:
            return result["result"]
        else:
            raise Error(result["error_type"], result["message"], result["traceback"])
    
class _MultiCallMethod:
    def __init__(self, call_list, name):
        self.__call_list = call_list
        self.__name = name
    def __getattr__(self, name):
        return _MultiCallMethod(self.__call_list, "%s.%s" % (self.__name, name))
    def __call__(self, *args, **kwargs):
        self.__call_list.append((self.__name, args, kwargs))

class MultiCall:
    def __init__(self, server):
        self.__server = server
        self.__call_list = []
    def __getattr__(self, name):
        return _MultiCallMethod(self.__call_list, name)
    def __call__(self):
        return MultiCallIterator(self.__server._multi_call(self.__call_list))

class ZeroRpcClient(object):
    def __init__(self, 
                 url_server,
                 json_serializer = None,
                 json_deserializer = None,
                 ):
        self.url_server = url_server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(url_server)
        if json_serializer:
            self.json_serializer = json_serializer
        else:
            import ujson
            self.json_serializer = ujson.dumps
                                            
        if json_deserializer:
            self.json_deserializer = json_deserializer
        else:
            import ujson
            self.json_deserializer = ujson.loads
            
    def __getattr__(self, name):
        return _Method(self._single_call, name)
    
    def _single_call(self, func_name, *args, **kwargs):
        request_packet = self.json_serializer([[func_name, args, kwargs],])
        return self._communicate(request_packet)
    
    def _multi_call(self, call_list):
        request_packet = self.json_serializer(call_list)
        return self._communicate(request_packet)

    def _communicate(self, request_packet):
        log.debug("request packet: %s" % request_packet)
        self.socket.send(request_packet)
        response_packet = self.socket.recv()
        log.debug("response packet: %s" % response_packet)
        result_list = self.json_deserializer(response_packet)
        log.debug("result: %s" % result_list) # TODO:
        return result_list

if __name__ == "__main__":
    pass
