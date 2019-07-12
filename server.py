#!/usr/bin/env python
from __future__ import print_function

import cgi
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        with open('server_index.html', 'r') as server_index:
            self.wfile.write(server_index.read().replace('\n', ''))


    def do_POST(self):
        # self._set_headers()
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        elif ctype == 'text/xml':
            length = int(self.headers.getheader('content-length'))
            postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        path = postvars.get('path')
        xml = postvars.get('project')
        properties = postvars.get('properties')
        option = postvars.get('option')
        
        if not xml:
            self.send_response(552, message='No SoapUI Project')
            self.end_headers()
            self.wfile.write('you need to specify the SoapUI project!')
            return
        else:
            xml = xml[0]

        f = open('/tmp/soapui-project.xml', 'w')
        print(xml, file=f)
        f.close()
        
        arguments = ['/opt/readyapi/ReadyAPI-2.5.0/bin/testrunner.sh']

        if path: 
            arguments.append('-f"%s"' % path[0])

        if option:
            for op in option:
                for line in op.splitlines():
                    arguments.append('%s' % line)

        if properties:
            properties = properties[0]
            f = open('/tmp/global.properties', 'w')
            print(properties, file=f)
            f.close()
            arguments.append('-Dsoapui.properties=/tmp/global.properties')

        arguments.append('/tmp/soapui-project.xml')

        p = Popen(arguments, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
        try:
            output, error = p.communicate()

            if p.returncode >= 1:
                self.send_response(550, message='Test Failure(s)')
                self.end_headers()
                self.wfile.write(output)
                self.wfile.write(error)
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output)

        except Exception as e:
            self.send_response(500)
            self.wfile.write(e)


def run(server_class=HTTPServer, handler_class=S, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('SoapUI Test Runner Started on port %s...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
