#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
import cv
import cv2

import cgi
import time

from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn


BOUNDARY = '--separador'
JPEG_QUALITY = 95
HEADER_HTML = 'text/html; charset=utf-8'


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.name, self.extension = os.path.splitext(self.path)
        self.name = self.name.replace('/', '')
        self.extension = self.extension.replace('.', '')

        print self.name, self.extension

        try:
            if self.extension == 'html':
                self.send_response(200)
                self.send_header('Content-type', HEADER_HTML)
                self.end_headers()

                self.wfile.write('Bancá, hugo! BANCÁ!!!')

                return

            if self.extension == 'mjpeg':
                device = int(re.findall('[\d+]', self.name)[0])
                camera = cv2.VideoCapture(device)

                self.send_response(200)
                self.wfile.write('Content-Type: multipart/x-mixed-replace; boundary=%s' % (BOUNDARY,))
                self.wfile.write('\r\n\r\n')

                while 1:
                    flag, image_raw = camera.read()

                    tmp = cv.fromarray(image_raw)
                    image = cv.EncodeImage('.jpeg',
                                            tmp,
                                            (cv.CV_IMWRITE_JPEG_QUALITY, JPEG_QUALITY)
                    )
                    image_data = image.tostring()

                    self.wfile.write('%s\r\n' % (BOUNDARY,))
                    self.wfile.write('Content-Type: image/jpeg\r\n')
                    self.wfile.write('Content-length: ' + str(len(image_data)) + '\r\n\r\n')
                    self.wfile.write(image_data)
                    self.wfile.write("\r\n\r\n\r\n")

                    time.sleep(0.05)

                camera.release()

                return

            if self.path.endswith(".jpeg"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type','image/jpeg')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            else:
                self.send_response(200)
                self.send_header('Content-type', HEADER_HTML)
                self.end_headers()
                self.wfile.write('URL inválida')
                return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        global rootnode, cameraQuality
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)

            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            value=int(upfilecontent[0])
            cameraQuality=max(2, min(99, value))
            self.wfile.write("<HTML>POST OK. Camera Set to<BR><BR>");
            self.wfile.write(str(cameraQuality));

        except :
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#class ThreadedHTTPServer(HTTPServer):
    """Handle requests in a separate thread."""

def main():
    try:
        server = ThreadedHTTPServer(('0.0.0.0', 8080), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
