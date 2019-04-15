#!/usr/bin/env python3

# MIT License
# (c) 2017 Kevin J. Walchko

# Update 2018-12-04 Cavon
# 1. Python 2 to Python 3
# 2. Uses cv2.VideoCapture(0)
# 3. remove argparse

# install dependency:
# sudo pip3 install opencv-python
# sudo apt-get install libatlas-base-dev
# sudo apt-get install libjasper-dev
# sudo apt-get install libqtgui4

# sudo apt-get install libqt4-test

from ezblock.basic import _Basic_class
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import time
import socket as Socket
import os
import re

# I use to do 0.0.0.0 to bind to all interfaces, but that seemed to be really
# slow. feeding it the correct ip address seems to greatly speed things up.

class Camera(_Basic_class):

    port = 9000
    RES = [
        [320, 240],
        [640, 480],
        [1024, 576],
        [1280, 800],
    ]

    def __init__(self, res=0):
        self.getCamera()
        width = self.RES[res][0]
        height = self.RES[res][1]
        self.setUpCameraCV(width, height)
        ipv4, ipv6 = self.getIP('wlan0')
        self.ip = ipv4
        self.hostname = Socket.gethostname()

    def getCamera(self):
        devices = []
        devs = os.listdir('/dev')
        for dev in devs:
            if 'video' in dev:
                dev = dev.replace('video', '')
                devices.append(dev)
        camera_works = False
        for dev in devices:
            try:
                self.camera = cv2.VideoCapture(0)
                camera_works = True
                break
            except:
                camera_works = False
        if not camera_works:
            raise IOError("Camera not found, please the connection of your camera")

    def getIP(self, iface='wlan0'):
        search_str = 'ip addr show wlan0'.format(iface)
        ipv4 = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M),
                        os.popen(search_str).read()).groups()[0]
        ipv6 = re.search(re.compile(r'(?<=inet6 )(.*)(?=\/)', re.M),
                        os.popen(search_str).read()).groups()[0]
        ip = [ipv4, ipv6]
        return ip

    def setUpCameraCV(self, width, height):
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def start(self):
        print("server starts at %s:%s" % (self.ip, self.port))
        self.mjpgServer.camera = self.camera
        self.server = HTTPServer((self.ip, self.port), self.mjpgServer)
        self.server.socket = ssl.wrap_socket(self.server.socket,
                                             server_side=True,
                                             certfile='ca.pem',
                                             ssl_version=ssl.PROTOCOL_TLSv1)
        self.server.serve_forever()

    def stop(self):
        self.server.socket.close()

    class mjpgServer(BaseHTTPRequestHandler):
        camera = None
        def do_GET(self, freq=50):
            print("do_get successed")
            if self.path == '/mjpg':
                self.send_response(200)
                self.send_header(
                    'Content-type',
                    'multipart/x-mixed-replace; boundary=--jpgboundary'
                )
                self.end_headers()

                while True:
                    if self.camera:
                        ret, img = self.camera.read()
                    else:
                        raise Exception('Error, camera not setup')
                    if not ret:
                        print('no image from camera')
                        time.sleep(1)
                        continue

                    ret, jpg = cv2.imencode('.jpg', img)
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(jpg.size))
                    self.end_headers()
                    self.wfile.write(jpg.tostring())
                    time.sleep(1.0/freq)
            else:
                print('error', self.path)
                self.send_response(404)
                self.send_header('Content-type', 'text/html'.encode())
                self.end_headers()
                self.wfile.write('<html><head></head><body>'.encode())
                self.wfile.write(
                    '<h1>{0!s} not found</h1>'.format(self.path).encode())
                self.wfile.write('</body></html>'.encode())

if __name__ == '__main__':
    try:
        print(Camera(0).getIP('wlan0')[0])
        Camera(0).start()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
