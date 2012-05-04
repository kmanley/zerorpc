import sys
import traceback
import threading
import zmq
import logging
log = logging.getLogger("zerorpc.server")

DEFAULT_URL_CLIENT = "tcp://*:5555"
DEFAULT_URL_WORKER = "inproc://workers"

def exposed(func):
    func._zerorpc_exposed = True
    return func

class Error(Exception):
    pass

class ZeroRpcServer(object):
    
    def __init__(self, 
                 url_client = DEFAULT_URL_CLIENT,
                 url_worker = DEFAULT_URL_WORKER,
                 json_serializer = None,
                 json_deserializer = None,
                 ): 

        self.url_client = url_client
        self.url_worker = url_worker

        self.main_thread = None
        self.worker_threads = []        
        self.context = zmq.Context(1)

        # Socket to talk to clients
        self.clients = self.context.socket(zmq.ROUTER)
        self.clients.bind(url_client)

        # Socket to talk to workers
        self.workers = self.context.socket(zmq.DEALER)
        self.workers.bind(url_worker)
        
        self.funcs = {}
        
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
        
    def register_function(self, func, name=None):
        name = name or func.__name__
        log.debug("registering %s" % name)
        self.funcs[name] = func 
    
    def register_instance(self, instance, namespace=None):
        for key, value in instance.__class__.__dict__.items():
            if callable(value) and getattr(value, "_zerorpc_exposed", False):
                name = "%s.%s" % (namespace, key) if namespace else key
                self.register_function(getattr(instance, key), name) # use instance-bound method
                
    def unregister_all(self):
        self.funcs = {}

    def _start(self, num_threads=1):
        log.debug("main thread %s starting" % threading.currentThread().ident)
        
        for unused in range(num_threads):
            thread = threading.Thread(target=self.thread_func)
            thread.start()
            self.worker_threads.append(thread)

        try:
            zmq.device(zmq.QUEUE, self.clients, self.workers)
        except zmq.core.error.ZMQError, e:
            if e.errno == zmq.ETERM:
                # server was shut down
                pass
            else:
                raise
        
        log.debug("main thread %s exiting" % threading.currentThread().ident)
    
    def start(self, num_threads=1, blocking=True):
        if self.main_thread:
            raise Error("already started with %d thread(s)" % len(self.worker_threads))
        
        self.main_thread = threading.Thread(target=self._start, args=(num_threads,))
        self.main_thread.start()
        
        if blocking:
            log.debug("blocked joining main server thread")
            self.main_thread.join()
            
        log.debug("start exiting")

    def shutdown(self):
        self.clients.close()
        self.workers.close()
        self.context.term()
        log.debug("waiting for all worker threads to exit")
        for thread in self.worker_threads:
            thread.join()
        self.worker_threads = []
        
        self.main_thread.join()
        self.main_thread = None
        
        log.debug("server stopped")
        
    def _execute(self, request):
        func_name, args, kwargs = request
        try:
            func = self.funcs[func_name]
        except KeyError:
            return {"success" : False,
                    "error_type" : sys.exc_info()[0].__name__,
                    "message" : "Function '%s' not found" % func_name,
                    "traceback" : ""}
        else:
            try:
                result = func(*args, **kwargs)
            except Exception, e:
                log.warning("call to %s failed:" % func_name)
                return {"success" : False,
                        "error_type" : sys.exc_info()[0].__name__,
                        "message" : str(e),
                        "traceback" : traceback.format_exc()}
            else:
                return {"success" : True,
                        "result" : result}
        
    def thread_func(self):
        log.debug("worker thread %s starting" % threading.currentThread().ident)
        
        socket = self.context.socket(zmq.REP)
        socket.connect(self.url_worker)
    
        while True:
            try:
                request_packet = socket.recv()
            except zmq.core.error.ZMQError, e:
                if e.errno == zmq.ETERM:
                    break
            else:
                log.debug("thread %s got request packet: %s" % (threading.currentThread().ident, request_packet))
                request_list = self.json_deserializer(request_packet)
                response_list = [self._execute(request) for request in request_list]
                response_packet = self.json_serializer(response_list)
                log.debug("thread %s sending response packet: %s" % (threading.currentThread().ident, response_packet))
                socket.send(response_packet)
                
        log.debug("worker thread %s exiting" % threading.currentThread().ident)

if __name__ == "__main__":
    pass
