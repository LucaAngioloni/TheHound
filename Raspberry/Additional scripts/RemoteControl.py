##
## MIT License
## 
## Copyright (c) 2016 Luca Angioloni
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
import numpy as np
import cv2
from cv2 import xfeatures2d as xf
from timeit import default_timer as timer
import scipy as sp
import socket
import os
import serial
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import math

arduino = True
remote = True

if arduino:
    sr = serial.Serial('/dev/ttyACM0', 115200)
    time.sleep(3)


if remote:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #sock.settimeout(0.1)
    #sock.setblocking(False)

    get_ip = os.popen(
        'ifconfig | grep -Eo "inet (addr:)?([0-9]*\.){3}[0-9]*" | grep -Eo "([0-9]*\.){3}[0-9]*" | grep -v "127.0.0.1"').read()

    myip = get_ip.strip("\n")

    server_address = (myip, 50001)

    print(server_address)

    sock.bind(server_address)
    sock.listen(1)

    print("Listening")
    notConnected = True
    while notConnected:
        try:
            connection, client_address = sock.accept()
            print("Connected to " + str(client_address))
            notConnected = False
        except:
            notConnected = True


def resize(mat, preferred_dimensions=(1334, 750)):
    original_dimensions = (mat.shape[0], mat.shape[1])
    if (original_dimensions != (0, 0)):
        max_size_out = min(preferred_dimensions)
        max_size_in = max(original_dimensions)
        factor = max_size_out / max_size_in
        if (factor < 1):
            mat = cv2.resize(mat, dsize=None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)
            # print("Resized")
    return mat


def mat_to_byte_array(mat, ext):
    mat = resize(mat)
    # print(mat.shape)
    success, img = cv2.imencode(ext, mat)
    bytedata = img.tostring()
    return success, bytedata


try:
    camera = PiCamera()
    #camera.resolution = (1920, 1080)
    #camera.framerate = 32
    rawCapture = PiRGBArray(camera)
    #rawCapture = io.BytesIO()

    time.sleep(2.0)

    count = 0
    start_time = timer()


    for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        rawCapture.truncate(0)
        count += 1
        frame = image.array
        frame = cv2.flip(frame, -1)
        img2 = frame

        try:
            data = connection.recv(1)
            direction = data.decode('utf-8')
        except:
            direction = "None"

        # Calculate position in a simple way. Not quite right
        if direction == "R":
            msg = '{"coordinates": {"x": ' + "0.5" + ', "y": ' + "0" + '}, "found": true}'
            if arduino:
                sr.write(msg.encode('utf-8'))
        elif direction == "L":
            msg = '{"coordinates": {"x": ' + "-0.5" + ', "y": ' + "0" + '}, "found": true}'
            if arduino:
                sr.write(msg.encode('utf-8'))
        elif direction == "F":
            msg = '{"found": true}'
            if arduino:
                sr.write(msg.encode('utf-8'))
        elif direction == "B":
            msg = '{"back": true}'
            if arduino:
                sr.write(msg.encode('utf-8'))
        else:
            msg = '{"found": false}'
            if arduino:
                sr.write(msg.encode('utf-8'))

        print(msg)

        success, encodedimg = mat_to_byte_array(img2, ".jpg")

        if success and remote:
            start = "S"

            type = "img"

            array = bytearray(start.encode('utf-8'))

            array.extend(type.encode('utf-8'))

            array.extend(len(encodedimg).to_bytes(4, 'big'))
            array.extend(encodedimg)

            try:
                connection.sendall(array)
            except:
                notConnected = True
                c = 0
                while notConnected and c <10000:
                    c = c+1
                    try:
                        print("Connection Lost, reconnecting...")
                        connection, client_address = sock.accept()
                        print("Connected to " + str(client_address))
                        notConnected = False
                    except:
                        notConnected = True

        now = timer()
        if (now - start_time >= 1):
            print(str(count) + "fps")
            count = 0
            start_time = now


    print("Out of While")
    # Clean up the connection
    if remote:
        connection.close()
        print("Connection closed")
except KeyboardInterrupt:
    # Clean up the connection
    if remote:
        connection.close()
        print("Connection closed")
    # raise KeyboardInterrupt