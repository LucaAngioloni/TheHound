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
"""
import cv2
from cv2 import xfeatures2d as xf
import numpy as np

img = cv2.imread('/Users/LucaAngioloni/Desktop/cancellino.JPG',0)

surf = xf.SURF_create(400)

kp, des = surf.detectAndCompute(img, None)

print(len(kp))

img2 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)

img2 = cv2.pyrDown(img2)
img2 = cv2.pyrDown(img2)

cv2.imshow("SURF detect", img2)
cv2.waitKey(0)
"""

#!/usr/bin/env python

'''
Uses SURF to match two images.

Based on the sample code from opencv:
  samples/python2/find_obj.py

USAGE
  find_obj.py <image1> <image2>
'''

import numpy
import cv2
from cv2 import xfeatures2d as xf

import sys


detector = xf.SURF_create(400, 5, 5)
matcher = cv2.BFMatcher(cv2.NORM_L2)

###############################################################################
# Image Matching
###############################################################################

def match_images(kp1, desc1, img2):
    """Given two images, returns the matches"""

    kp2, desc2 = detector.detectAndCompute(img2, None)
    #print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=2) #2
    kp_pairs = filter_matches(kp1, kp2, raw_matches)
    return kp_pairs

def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    kp_pairs = zip(mkp1, mkp2)
    return kp_pairs


###############################################################################
# Match Diplaying
###############################################################################

def explore_match(win, img1, img2, kp_pairs, status=None, H=None):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    vis = numpy.zeros((max(h1, h2), w1+w2), numpy.uint8)
    vis[:h1, :w1] = img1
    vis[:h2, w1:w1+w2] = img2
    vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    if H is not None:
        corners = numpy.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
        corners = numpy.int32( cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0) )
        cv2.polylines(vis, [corners], True, (255, 255, 255))

    if status is None:
        status = numpy.ones(sum(1 for _ in kp_pairs), numpy.bool_)
    p1 = numpy.int32([kpp[0].pt for kpp in kp_pairs])
    p2 = numpy.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)
    print(str(p2) + " and " + str(p2))

    green = (0, 255, 0)
    red = (0, 0, 255)
    white = (255, 255, 255)
    kp_color = (51, 103, 236)
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            col = green
            cv2.circle(vis, (x1, y1), 2, col, -1)
            cv2.circle(vis, (x2, y2), 2, col, -1)
        else:
            col = red
            r = 2
            thickness = 3
            cv2.line(vis, (x1-r, y1-r), (x1+r, y1+r), col, thickness)
            cv2.line(vis, (x1-r, y1+r), (x1+r, y1-r), col, thickness)
            cv2.line(vis, (x2-r, y2-r), (x2+r, y2+r), col, thickness)
            cv2.line(vis, (x2-r, y2+r), (x2+r, y2-r), col, thickness)
    vis0 = vis.copy()
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            cv2.line(vis, (x1, y1), (x2, y2), green)

    cv2.imshow(win, vis)



def draw_matches(window_name, kp_pairs, img1, img2):
    """Draws the matches for """
    mkp1, mkp2 = zip(*kp_pairs)

    p1 = numpy.float32([kp.pt for kp in mkp1])
    p2 = numpy.float32([kp.pt for kp in mkp2])

    if sum(1 for _ in kp_pairs) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        #print '%d / %d  inliers/matched' % (numpy.sum(status), len(status))
    else:
        H, status = None, None
        #print '%d matches found, not enough for homography estimation' % len(p1)

    if len(p1):
        explore_match(window_name, img1, img2, kp_pairs, status, H)

###############################################################################
# Test Main
###############################################################################

fn1 = '/Users/LucaAngioloni/Desktop/cancellino.JPG'

img1 = cv2.imread(fn1, 0)

img1 = cv2.pyrDown(img1)
img1 = cv2.pyrDown(img1)

kp, desc = detector.detectAndCompute(img1, None)

camera = cv2.VideoCapture(0)

if camera.isOpened(): # try to get the first frame
    rval, frame = camera.read()
else:
    rval = False

while rval:
    frame = cv2.pyrDown(frame)
    img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_pairs = match_images(kp, desc, img2)

    if kp_pairs:
        draw_matches('find_obj', kp_pairs, img1, img2)

    rval, frame = camera.read()
    key = cv2.waitKey(100)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow('find_obj')