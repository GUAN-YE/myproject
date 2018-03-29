#!/usr/bin/env python
import os
import sys

# http1.1 patch
from django.core.servers import basehttp

def run_tornado(addr, port, wsgi_handler, ipv6=False, threading=False):
    import tornado.wsgi, tornado.httpserver, tornado.ioloop

    container = tornado.wsgi.WSGIContainer(wsgi_handler)
    server = tornado.httpserver.HTTPServer(container)
    server.listen(port=port, address=addr)
    tornado.ioloop.IOLoop.instance().start()

def run_gevent(addr, port, wsgi_handler, ipv6=False, threading=False):
    from gevent import monkey; monkey.patch_all(thread=False)
    from gevent.pywsgi import WSGIServer
    
    WSGIServer((addr, port), wsgi_handler).serve_forever()

try:
    import gevent
    basehttp.run = run_gevent
    print 'run_gevent'
except ImportError:
    pass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tbkt.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
