#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cv, cv2
import json
import re
import time

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

from v4l import V4L2


HTTP_ADDRESS = '0.0.0.0'
HTTP_PORT = 8383
BOUNDARY = '--FOTO--'
JPEG_QUALITY = 95

v = V4L2()


class HTTPHandler(BaseHTTPRequestHandler):
    def version_string(self):
        return 'Videomotion/1.0'

    def _response(self, code=200, mime='text/html; charset=utf-8', content=''):
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def _urls(self, path):
        tmp = filter(None, path.split('/'))
        try:
            self._dev, self._ext = tmp[0].split('.')
        except IndexError:
            self._dev, self._ext = 'list', 'json'

    ##

    def do_GET(self):
        self._urls(self.path)

        if self._ext == 'mjpeg':
            device = int(re.findall('[\d+]', self._dev)[0])
            camera = cv2.VideoCapture(device)

            self.send_response(200)
            self.wfile.write('Content-Type: multipart/x-mixed-replace; boundary=%s' % (BOUNDARY,))
            self.wfile.write('\r\n\r\n')

            while True:
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
                self.wfile.write('\r\n')

                time.sleep(0.05)

            camera.release()

        elif self._ext == 'jpeg':
            self._response(content='.jpeg sin implementar')

        elif self._ext == 'json':
            if self._dev == 'list':
                data = {'cameras': []}

                for dev in v.devices:
                    data['cameras'].append({
                        'bus_info': dev.bus_info,
                        'capabilities': dev.capabilities,
                        'card': dev.card,
                        'driver': dev.driver,
                        'id': dev.id,
                        'path': dev.path,
                        'version': dev.version,
                        'info_url': 'http://%s/%s.json' % (self.headers.get('Host'), dev.id),
                        'stream_url': 'http://%s/%s.mjpeg' % (self.headers.get('Host'), dev.id),
                    })

            else:

                data = {}

            self._response(mime='application/json; charset=utf-8', content=json.dumps(data))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def start_server():
    try:
        server = ThreadedHTTPServer(
            (HTTP_ADDRESS, HTTP_PORT),
            HTTPHandler
        )
        print 'running at {0}:{1}'.format(HTTP_ADDRESS, HTTP_PORT)
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down server.'
        server.socket.close()


if __name__ == '__main__':
    start_server()
