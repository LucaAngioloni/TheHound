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
import socket
import struct
import io
import cv2
import numpy as np

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))

# Works only on Mac
#get_ip = os.popen('dns-sd -G  v4 raspberrypi2.local | grep  -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"').read()
#client.connect((get_ip, 50001))

client.connect(('192.168.01.175', 50001))

while True:
    s = client.recv(1)
    print(s)
    if s.decode('utf-8') == 'S':

        i = client.recv(3)
        print(i)
        l = client.recv(4)
        #print(l)
        length = int.from_bytes(l,byteorder='big')
        print(length)
        rem = length
        img = bytearray()
        while rem > 0:
            im = client.recv(rem)
            im = bytearray(im)
            img.extend(im)
            rem = rem-len(im)

        im = np.array(img)
        #print(type(im))
        print(im.shape)
        image = cv2.imdecode(im,3)
        cv2.imshow('test', image)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
    else:
        client.close()








