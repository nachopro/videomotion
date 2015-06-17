#! /usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, Response, jsonify, g
from v4l import V4L2

import cv
import cv2
import re

JPEG_QUALITY = 95

app = Flask(__name__)

def stream(device_name):
    device = int(re.findall('[\d+]', device_name)[0])
    camera = cv2.VideoCapture(device)

    while True:
        flag, image_raw = camera.read()
        tmp = cv.fromarray(image_raw)
        image = cv.EncodeImage('.jpeg',
            tmp,
            (cv.CV_IMWRITE_JPEG_QUALITY, JPEG_QUALITY)
        )
        image_data = image.tostring()

        yield(b'--bound'
              b'Content-Type: image/jpeg\r\n'
              b'Content-length: ' + str(len(image_data)) + '\r\n\r\n'
              b''+image_data+''
              b'\r\n'
        )

    camera.release()

@app.route('/')
def camera_list():
    v = V4L2()
    g.cameras = v
    del(v)

    data = {
        'cameras': [s.__dict__ for s in g.cameras.devices]
    }
    print data
    return jsonify(**data)

@app.route('/<device>/json')
def camera_properties(device):
    data = {'id': 123}
    return jsonify(**data)

@app.route('/<device>/mjpeg')
def camera_stream(device):
    return Response(
        stream(device),
        mimetype='multipart/x-mixed-replace; boundary=--bound'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
