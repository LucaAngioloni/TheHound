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
from imutils.video import VideoStream
import imutils
from pivideostream import PiVideoStream

arduino = False

if arduino:
    sr = serial.Serial('/dev/cu.usbmodem1411', 115200)
    time.sleep(3)

cv2.ocl.setUseOpenCL(False)

detector = xf.SURF_create(10000, 5, 5)
# detector = cv2.ORB_create(200)
# detector = cv2.FastFeatureDetector_create()
matcher = cv2.BFMatcher(cv2.NORM_L2)

compute = detector
# compute = xf.SURF_create()
# compute = cv2.ORB_create()

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

        dist = [m.distance for m in matches]

        # threshold: half the mean
        thres_dist = (sum(dist) / len(dist)) * 0.7

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
            corners = sp.int32(position + (w1, 0))
            cv2.polylines(view, [corners], True, (255, 255, 255))

    return view, position


try:
    fn1 = 'volantino.jpg'

    img1 = cv2.imread(fn1, 0)

    """
    camera = PiCamera()
    #camera.resolution = (640, 480)
    #camera.framerate = 32
    rawCapture = PiRGBArray(camera)
    #rawCapture = io.BytesIO()

    time.sleep(0.1)

    """

    # initialize the picamera stream and allow the camera
    # sensor to warmup
    stream = PiVideoStream(resolution=(640, 480),
                                framerate=32)

    vs = stream.start()
    time.sleep(2.0)

    img1 = resize(img1, preferred_dimensions=(640, 480))

    kp = detector.detect(img1, None)

    kp, desc = compute.compute(img1, kp)

    count = 0
    start_time = timer()

    frame = vs.read()

    #for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        #rawCapture.truncate(0)
    while frame is not None:
        count += 1
        #frame = image.array
        #frame = cv2.flip(frame, 1)
        img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

        success, encodedimg = mat_to_byte_array(output, ".jpg")

        if success:
            start = "S"

            type = "img"

            array = bytearray(start.encode('utf-8'))

            array.extend(type.encode('utf-8'))

            array.extend(len(encodedimg).to_bytes(4, 'big'))
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

        frame = vs.read()


    print("Out of While")
    # Clean up the connection

    connection.close()
    print("Connection closed")
except KeyboardInterrupt:
    # Clean up the connection
    connection.close()
    print("Connection closed")
    # raise KeyboardInterrupt