# zerorpc

A protocol (and Python implementation) for RPC over [ZeroMQ] which uses JSON for
data serialization. The resulting Python implementation is approx 5x faster than the 
corresponding xmlrpcserver & client in the single-threaded case, and nearly 10x faster in the
multithreaded case. It is simple to achieve over 10K RPC calls/sec with this implementation.   

[ZeroMQ]: http://www.zeromq.org/

## Requirements

- [Python] tested with 2.7
- [ZeroMQ Python bindings]
- [UltraJson] but you can plug in your own JSON serializer/deserializer

[Python]: http://www.python.org 
[ZeroMQ Python bindings]: http://www.zeromq.org/bindings:python
[UltraJson]: https://github.com/esnme/ultrajson

## Example

### Server

Create an instance of ZeroRpcServer, register functions and/or class instances, and call start().
Functions can be referenced by different names and/or organized into dotted namespaces.

    ```python
    def mult(a, b):
        return a * b

    server = zerorpc.server.ZeroRpcServer("tcp://*:5555")
    server.register_function(mult, name="my.namespace.mult")
    server.start(3, blocking=False)
    ```
    
### Client

Create an instance of ZeroRpcClient and call methods on it as if the functions were defined on that
instance. The call is marshaled to the server transparently. Exceptions on the server are propagated
to the client.  
    
    ```python
    client = zerorpc.client.ZeroRpcClient("tcp://localhost:5555")
    result = client.my.namespace.mult(5, 7)
    ```

### MultiCall

MultiCall works similarly to the xmlrpclib implementation. The calls are marshaled to the server, and the
result is returned, in one network roundtrip.

    ```python
    client = zerorpc.client.ZeroRpcClient("tcp://localhost:5555")
    multicall = zerorpc.client.MultiCall(client)
    multicall.my.namespace.mult(2, 2)
    multicall.my.namespace.mult(3, 3)
    multicall.my.namespace.mult(4, 4)
    for result in multicall():
        print result
    ```
        
## Example Benchmarks        

To run benchmarks on your own machine see the benchmarks subdirectory

I got these results on Win XP x64 edition, Intel Xeon CPU W3530 @ 2.80GHz, 12GB RAM

- xmlrpc  client & server (single-threaded):  850 calls/sec
- zerorpc client & server (single-threaded): 4500 calls/sec
- xmlrpc  client & server (multi-threaded):  1200 calls/sec
- zerorpc client & server (multi-threaded): 11000 calls/sec

## Todo

- Write more tests
- Documentation

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## License

Copyright (c) 2012 Kevin T. Manley

MIT License

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
