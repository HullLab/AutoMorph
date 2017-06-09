#!/usr/bin/env python

import cv
import cv2
import numpy as np

from PIL import Image, ImageEnhance
from scipy import ndimage
from skimage import morphology


def morphOpen(image,disk_size):
    '''
    Performs morphological opening (erosion followed by dilation using same
    structuring element); equivalent of 'imopen' in MATLAB.
    '''
    strel = morphology.disk(disk_size)
    erosion = cv2.erode(image,strel)
    dilation = cv2.dilate(erosion,strel)
    return dilation


def rgb2gray(image):
    '''
    Converts image in RGB colorspace to grayscale.
    '''
    gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    return gray


def rgbFilter(image):
    '''
    Takes an image in RGB colorspace, finds the strongest RGB color band (i.e.,
    the band with the highest value), and discards the other color bands.
    '''
    rgbBands = [image[:,:,i] for i in range(3)]
    # Determine most intense color band
    maxBand = np.argmax([x.sum() for x in rgbBands])
    # Discard less intense bands
    for i in range(3):
        if not i == maxBand:
            image[:,:,i] = 0
    return image


def contrastAdjust(image,contrast_adjustment):
    '''
    Enchances contrast in image.
    '''
    newImg = Image.fromarray(image)
    contrast = ImageEnhance.Contrast(newImg)
    adjusted = contrast.enhance(contrast_adjustment)
    adjArray = np.array(adjusted)
    adjArray[adjArray < 50] = 0 # Remove low values
    return adjArray


def convertBW(image,image_name,threshold_adjustment):
    '''
    Converts a grayscale image to black and white.
    '''
    threshold,image_bw = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    if threshold + threshold_adjustment >= 0:
        image_bw = cv2.threshold(image,threshold + threshold_adjustment,255,cv2.THRESH_BINARY)[1]
    else:
        print 'INFO: Threshold adjustment value too large! Using automatic value for', image_file
    return image_bw


def fillHoles(image):
    '''
    Files holes contained within a binary object.
    '''
    image_filled = ndimage.morphology.binary_fill_holes(image/255.0).astype("uint8") * 255
    return image_filled


def clearBorder(image,size):
    '''
    Deletes binary objects that touch the border of the image.
    '''
    h,w = size[:2]
    image_noise = image.copy()
    imgMat = cv.fromarray(image_noise)

    # Loop through border pixels as seeds
    for x in range(w):
        temp = cv.FloodFill(imgMat,(x,0),0)
        temp = cv.FloodFill(imgMat,(x,h-1),0)
    for y in range(h):
        temp = cv.FloodFill(imgMat,(0,y),0)
        temp = cv.FloodFill(imgMat,(w-1,y),0)

    image_border = np.asarray(imgMat)
    return image_border


def removeNoise(image):
    '''
    Removes all noise from a binary image by deleting all contained areas except
    the largest.
    '''
    labels,area_index = ndimage.label(image)
    sizes = ndimage.sum(image,labels,range(1,area_index + 1))
    max_patch = np.where(sizes == sizes.max())[0] + 1
    max_index = np.zeros(area_index + 1,np.uint8)
    max_index[max_patch] = 1
    max_object = max_index[labels]
    image_clean = max_object * 255

    return image_clean


def smoothImage(image,disk_size):
    '''
    Smooths the outline of a binary object by using morphological opening with
    a user-defined kernel size.
    '''
    smoothed = ndimage.binary_opening(image,structure=np.ones((disk_size,disk_size))).astype('uint8') * 255
    return smoothed


""" # Unused functions from old pipeline
def genGammaMap(gamma):
    invGamma = gamma ** -1
    gamma_map = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0,256)]).astype("uint8")
    return gamma_map


def gammaFilter(image,gamma):
    gamma_map = genGammaMap(gamma)
    return cv2.LUT(image,gamma_map)


# Threshold value version; newer version keeps largest labeled area
def removeNoise(image,size,noise_limit):
    h,w = size[:2]

    labels,areaIndex = ndimage.label(image)
    areas = np.array(ndimage.sum(image,labels,np.arange(labels.max() + 1)))
    areas_scaled = [x / 255.0 for x in areas]
    mask = areas > h * w * noise_limit

    image_clean = mask[labels.ravel()].reshape(labels.shape).astype('uint8') * 255

    return image_clean
"""
