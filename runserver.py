# -*- coding: utf-8 -*-
import wsgiref.simple_server
from os.path import abspath, dirname, join

from ladon.server.wsgi import LadonWSGIApplication


scriptdir = dirname(abspath(__file__))
service_modules = ['which_bus']
# Create the WSGI Application
application = LadonWSGIApplication(
    service_modules,
    [scriptdir, join(scriptdir, 'appearance')],
    catalog_name='Which Bus Web Service',
    catalog_desc='Click on the link to see how'
                 'to use the WhichBus service')

if __name__ == '__main__':
    # Starting the server from command-line will
    # create a stand-alone server on port 8080
    port = 8080
    print("\nExample services are running on port %(port)s."
          "\nView browsable API at http://localhost:%(port)s\n"
          % {'port': port})

    server = wsgiref.simple_server.make_server(
        '', port, application)
    server.serve_forever()
