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
import time
import scipy as sp
import serial
import math

arduino = False

if arduino:
    sr = serial.Serial('/dev/cu.usbmodem1411', 115200)
    time.sleep(3)
cv2.ocl.setUseOpenCL(False)

detector = xf.SURF_create(400, 10, 5, extended=True)
#detector = xf.SIFT_create()
#detector = xf.SURF_create()
#detector = cv2.ORB_create()
#detector = cv2.FastFeatureDetector_create()
matcher = cv2.BFMatcher(cv2.NORM_L2)

"""
FLANN_INDEX_KDTREE = 0
# index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
index_params = dict(algorithm=FLANN_INDEX_KDTREE,
                    table_number=12,  # 12
                    key_size=20,     # 20
                    multi_probe_level=2)  # 2
search_params = dict(checks=50)
matcher = cv2.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)
"""

compute = detector
#compute = xf.SURF_create()
#compute = cv2.ORB_create()


def resize(mat, preferred_dimensions=(1334,750), dimensions=(None,None)):
    original_dimensions = (mat.shape[0], mat.shape[1])
    if(original_dimensions != (0,0)):
        if dimensions == (None,None):
            max_size_out = min(preferred_dimensions)
            max_size_in = max(original_dimensions)
            factor = max_size_out/max_size_in
            if(factor<1):
                mat = cv2.resize(mat, dsize=None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)
                # print("Resized")
        else:
            factorx = dimensions[0] / original_dimensions[0]
            factory = dimensions[1] / original_dimensions[1]
            mat = cv2.resize(mat, dsize=None, fx=factorx, fy=factory, interpolation=cv2.INTER_AREA)
            # print("Resized")
    return mat

def match_images(d1, img2):
    kp2 = detector.detect(img2, None)

    kp2, d2 = compute.compute(img2, kp2)

    if (kp2 is not None) and (d2 is not None):
        # print('#keypoints in image1: %d, image2: %d' % (len(d1), len(d2)))

        # match the keypoints
        matches = matcher.match(d1, d2)

        dist = [m.distance for m in matches]

        # threshold: half the mean
        thres_dist = (sum(dist) / len(dist)) * 0.5

        # keep only the reasonable matches
        dist_match = [m for m in matches if m.distance < thres_dist]

        sel_matches = dist_match

        # sel_matches = matches
        # print('#selected matches:', len(sel_matches))
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
        #don't use in final production
        for m in sel_matches:
            # draw the keypoints matches
            color = tuple([sp.random.randint(0, 255) for _ in iter(range(3))])
            cv2.line(view, (int(k1[m.queryIdx].pt[0]),int(k1[m.queryIdx].pt[1])), (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)

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
            if area > (w2 * h2 / 150) and area < (w2 * h2 / 1.4):
                corners = sp.int32(position + (w1, 0))
                cv2.polylines(view, [corners], True, (255, 255, 255))
            else:
                position = None

    cv2.imshow("view", view)
    return position

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



#fn1 = '/Users/LucaAngioloni/Desktop/pile.jpeg'

fn1 = 'flowers.jpg'

img1 = cv2.imread(fn1, 0)

camera = cv2.VideoCapture(0)

if camera.isOpened(): # try to get the first frame
    rval, frame = camera.read()
else:
    rval = False

img1 = resize(img1, preferred_dimensions=(720, 400))

kp = detector.detect(img1, None)

kp, desc = compute.compute(img1, kp)

count = 0
start_time = timer()

while rval:
    count += 1

    img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img2 = resize(img2, preferred_dimensions=(1280,720))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img2 = clahe.apply(img2)
    kp_pairs , kp2 = match_images(desc, img2)

    """
    if kp_pairs:
        draw_matches(img1, img2, kp_pairs, kp, kp2)
    """

    position = draw_matches(img1, img2, kp_pairs, kp, kp2)

    if position is not None:
        x = 0
        y = 0

        for point in position:
            x += point[0]
            y += point[1]

        x = x/4
        y = y/4

        h2, w2 = img2.shape[:2]
        dx = x - (w2/2)
        dy = y - (h2/2)
        if abs(dx) > w2/8:
            msg = '{"coordinates": {"x": ' + str(dx/w2) + ', "y": ' + str(dy/h2) + '}, "found": true}'
            print(msg)
            if arduino:
                sr.write(msg.encode('utf-8'))
                print(sr.readline())
        else:
            msg = '{"found": true}'
            print(msg)
            if arduino:
                sr.write(msg.encode('utf-8'))
                print(sr.readline())
    else:
        msg = '{"found": false}'
        print(msg)
        if arduino:
            sr.write(msg.encode('utf-8'))
            print(sr.readline())

    now = timer()
    if (now - start_time >= 1):
        print("                                   " + str(count) + "fps")
        count = 0
        start_time = now
    rval, frame = camera.read()
    key = cv2.waitKey(100)
    if key == 27: # exit on ESC
        break


cv2.destroyWindow("view")