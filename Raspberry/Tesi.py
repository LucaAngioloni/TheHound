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

headerLen = 12

#cv2.ocl.setUseOpenCL(False)

detector = xf.SURF_create(10000, 10, 5, extended=True)
#detector = cv2.ORB_create()
# detector = cv2.FastFeatureDetector_create()
matcher = cv2.BFMatcher(cv2.NORM_L2)

compute = detector
#compute = xf.SURF_create()
# compute = cv2.ORB_create()


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


def match_images(d1, img2):
    kp2 = detector.detect(img2, None)

    kp2, d2 = compute.compute(img2, kp2)

    if (kp2 is not None) and (d2 is not None):
        # print('#keypoints in image1: %d, image2: %d' % (len(d1), len(d2)))

        # match the keypoints
        matches = matcher.match(d1, d2)
        if len(matches) == 0:
            return None, None

        dist = [m.distance for m in matches]

        # threshold: half the mean
        thres_dist = (sum(dist) / len(dist)) * 0.5

        # keep only the reasonable matches
        dist_match = [m for m in matches if m.distance < thres_dist]

        sel_matches = dist_match

        # sel_matches = matches
        print('#selected matches:', len(sel_matches))
        return sel_matches, kp2
    else:
        return None, None


def draw_matches(img1, img2, sel_matches, k1, k2):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    view[:h1, :w1, 0] = img1
    view[:h2, w1:, 0] = img2
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    position = None

    if (sel_matches is not None) and (k2 is not None):
        # don't use in final production
        for m in sel_matches:
            # draw the keypoints matches
            color = tuple([sp.random.randint(0, 255) for _ in iter(range(3))])
            cv2.line(view, (int(k1[m.queryIdx].pt[0]), int(k1[m.queryIdx].pt[1])),
                     (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)

        kp2 = [k2[m.trainIdx] for m in sel_matches]
        kp1 = [k1[m.queryIdx] for m in sel_matches]

        p1 = cv2.KeyPoint_convert(kp1)
        p2 = cv2.KeyPoint_convert(kp2)

        if sum(1 for _ in sel_matches) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        else:
            H, status = None, None
        if H is not None:
            corners = sp.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
            position = cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2)
            area = computeArea(position)
            print("Area : " + str(area))
            if area > (w2*h2/150) and area < (w2*h2/1.4):
                corners = sp.int32(position + (w1, 0))
                cv2.polylines(view, [corners], True, (255, 255, 255))
            else:
                position = None

    return view, position


def computeArea(points):
    p1 = points[0]
    p2 = points[1]
    p3 = points[2]
    p4 = points[3]

    a = distance(p1,p2)
    b = distance(p2,p3)
    c = distance(p3,p4)
    d = distance(p4,p1)

    diag = distance(p1,p3)

    return triangleArea(a,b,diag) + triangleArea(c,d,diag)

def triangleArea(a,b,c):
    # calculate the semi-perimeter
    s = (a + b + c) / 2

    # calculate the area
    intern = (s * (s - a) * (s - b) * (s - c))
    if intern < 0:
        return 0
    area = intern ** 0.5
    return area

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def receiveImage(con):
    header_c = []
    bytes_recd = 0
    while bytes_recd < headerLen:
        chunk = con.recv(headerLen - bytes_recd)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        header_c.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    header = b''.join(header_c)
    print("Header Received")
    t = header[:4]
    l = header[4:]

    h = t.decode(encoding='utf-8')
    #print("Header init: " + h)
    if h != 'Simg':
        print("Not an Image")
        return None

    MSGLEN = int.from_bytes(l, byteorder='little')

    #print("Image len: " + str(MSGLEN))
    if MSGLEN < 1:
        print("Lenght error, too short")
        return None
    print("Receiving image")
    chunks = []
    bytes_recd = 0
    while bytes_recd < MSGLEN:
        chunk = con.recv(MSGLEN - bytes_recd)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)

    print("Image Received")
    data = np.array(bytearray(b''.join(chunks)))
    #print(data.shape)
    return cv2.imdecode(data, 0)

try:

    if arduino:
        sr = serial.Serial('/dev/ttyACM0', 115200)
        time.sleep(3)

    img1 = None

    if remote:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        get_ip = os.popen(
            'ifconfig | grep -Eo "inet (addr:)?([0-9]*\.){3}[0-9]*" | grep -Eo "([0-9]*\.){3}[0-9]*" | grep -v "127.0.0.1"').read()

        myip = get_ip.strip("\n")

        server_address = (myip, 50001)

        print(server_address)

        sock.bind(server_address)
        sock.listen(1)

        print("Listening")

        connection, client_address = sock.accept()
        print("Connected to " + str(client_address))

        img1 = receiveImage(connection)
        #print(img1.shape)
        #cv2.imwrite("receivedimg.jpg", img1)
        """
        if recimg is not None:
            img1 = cv2.cvtColor(recimg, cv2.COLOR_BGR2GRAY)
        else:
            img1 = None
        """

    if img1 is None:
        fn1 = 'volantino.jpg'

        img1 = cv2.imread(fn1, 0)

    camera = PiCamera()
    #camera.resolution = (1920, 1080)
    #camera.framerate = 32
    rawCapture = PiRGBArray(camera)
    #rawCapture = io.BytesIO()

    time.sleep(2.0)

    img1 = resize(img1, preferred_dimensions=(640, 480))

    kp = detector.detect(img1, None)

    kp, desc = compute.compute(img1, kp)

    count = 0
    start_time = timer()

    for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        rawCapture.truncate(0)
        count += 1
        frame = image.array
        frame = cv2.flip(frame, -1)
        img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #img2 = cv2.equalizeHist(img2)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img2 = clahe.apply(img2)
        kp_pairs, kp2 = match_images(desc, img2)

        output, position = draw_matches(img1, img2, kp_pairs, kp, kp2)

        if position is not None:
            # Calculate position in a simple way. Not quite right
            x = 0
            y = 0

            for point in position:
                x += point[0]
                y += point[1]

            x /= 4
            y /= 4

            h2, w2 = img2.shape[:2]
            dx = x - (w2 / 2)
            dy = y - (h2 / 2)
            if abs(dx) > w2 / 8:
                # print("Movement: X = " + str((dx / w2)) + " , Y = " + str((dy / h2)))
                msg = '{"coordinates": {"x": ' + str(dx / w2) + ', "y": ' + str(dy / h2) + '}, "found": true}'
                if arduino:
                    sr.write(msg.encode('utf-8'))
            else:
                msg = '{"found": true}'
                if arduino:
                    sr.write(msg.encode('utf-8'))
        else:
            msg = '{"found": false}'
            if arduino:
                sr.write(msg.encode('utf-8'))

        print(msg)

        success, encodedimg = mat_to_byte_array(output, ".jpg")

        if success and remote:
            start = "S"

            type = "img"

            array = bytearray(start.encode('utf-8'))

            array.extend(type.encode('utf-8'))

            array.extend(len(encodedimg).to_bytes(8, 'big'))
            array.extend(encodedimg)

            try:
                connection.sendall(array)
            except:
                print("Connection Lost, reconnecting...")
                connection, client_address = sock.accept()
                print("Connected to " + str(client_address))

        now = timer()
        if (now - start_time >= 1):
            print(str(count) + "fps")
            count = 0
            start_time = now

        #read buffer to see if there are messages


    print("Out of While")
    # Clean up the connection
    if remote:
        start = "S"

        type = "msg"

        array = bytearray(start.encode('utf-8'))

        array.extend(type.encode('utf-8'))

        msg = "closeConnection".encode('utf-8')
        array.extend(len(msg).to_bytes(4, 'big'))
        array.extend(msg)
        connection.sendall(array)
        connection.close()
        print("Connection closed")
except KeyboardInterrupt:
    # Clean up the connection
    if remote:
        start = "S"

        type = "msg"

        array = bytearray(start.encode('utf-8'))

        array.extend(type.encode('utf-8'))

        msg = "closeConnection".encode('utf-8')
        array.extend(len(msg).to_bytes(4, 'big'))
        array.extend(msg)
        connection.sendall(array)
        connection.close()
        print("Connection closed")
    # raise KeyboardInterrupt