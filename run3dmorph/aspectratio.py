#!/usr/bin/env python

import cv2
import numpy as np

from scipy import spatial


def getMBB(image_clean):
    '''
    Get minimum bounding box of object contour.
    '''
    # Get contours
    try: # OpenCV 3.3.0+
        _,contours,_ = cv2.findContours(image_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except: # Olden versions
        contours,_ = cv2.findContours(image_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Get minimum bounding box
    rect = cv2.minAreaRect(contours[0])
    try: # OpenCV 3.3.0+
        mbb = cv2.boxPoints(rect)
    except: # Olden versions
        mbb = cv2.cv.BoxPoints(rect)
    return mbb,contours[0]


def measureMBB(mbb):
    '''
    Get height (max length), width (min length), and aspect ratio of minimum bounding box.
    '''
    distances = spatial.distance.pdist(mbb)
    height = max(distances)
    width = min(distances)
    aspect_ratio = height / width
    return height,width,aspect_ratio
