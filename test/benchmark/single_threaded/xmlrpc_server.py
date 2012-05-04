from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            logRequests=False,
                            requestHandler=RequestHandler)

# Register a function under a different name
def mult(x, y):
    return x * y

server.register_function(mult, 'mult')

# Run the server's main loop
server.serve_forever()