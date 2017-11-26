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
from timeit import default_timer as timer
from array import array
import socket
import os

def resize(mat, preferred_dimensions = (1334,750)):
    original_dimensions = (mat.shape[0], mat.shape[1])
    if(original_dimensions != (0,0)):
        max_size_out = min(preferred_dimensions)
        max_size_in = max(original_dimensions)
        factor = max_size_out/max_size_in
        if(factor<1):
            mat = cv2.resize(mat, dsize=None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)
            # print("Resized")
    return mat

def mat_to_byte_array(mat, ext):
    mat = resize(mat)
    # print(mat.shape)
    succes, img = cv2.imencode(ext, mat)
    bytedata = img.tostring()
    return succes, bytedata

try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    # fullBody = cv2.CascadeClassifier('/usr/local/Cellar/opencv3/3.1.0_3/share/OpenCV/haarcascades/haarcascade_fullbody.xml')


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    get_ip = os.popen('ifconfig | grep -Eo "inet (addr:)?([0-9]*\.){3}[0-9]*" | grep -Eo "([0-9]*\.){3}[0-9]*" | grep -v "127.0.0.1"').read()

    myip = get_ip.strip("\n")

    server_address = (myip, 50001)

    print(server_address)

    sock.bind(server_address)
    sock.listen(1)

    print("Listening")

    connection, client_address = sock.accept()
    print("Connected to " + str(client_address))

    camera = cv2.VideoCapture(0)

    if camera.isOpened(): # try to get the first frame
        rval, frame = camera.read()
    else:
        rval = False

    count = 0
    start_time = timer()

    while rval:
        count +=1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

        success, encodedimg = mat_to_byte_array(frame, ".jpg")

        if success:
            # print(str(len(encodedimg)))

            start = "S"

            type = "img"

            array = bytearray(start.encode('utf-8'))

            array.extend(type.encode('utf-8'))

            array.extend(len(encodedimg).to_bytes(4,'big'))
            array.extend(encodedimg)

            try:
                connection.sendall(array)
                # print("Frame sent")
            except:
                print("Connection Lost, reconnecting...")
                connection, client_address = sock.accept()
                print("Connected to " + str(client_address))
        #time.sleep(0.1)

        now = timer()
        if (now - start_time >= 1):
            print(str(count) + "fps")
            count = 0
            start_time = now
        rval, frame = camera.read()

    print("Out of While")
    # Clean up the connection
    connection.close()
    print("Connection closed")
except KeyboardInterrupt:
    # Clean up the connection
    connection.close()
    print("Connection closed")
    # raise KeyboardInterrupt