#!/usr/bin/env python

# Originally written by A. Hsiang
#
# 2016-06: Ported to python (K. Nelson)

import settings
import images

from datetime import datetime
import glob

import cv2

import os
from scipy import ndimage
from skimage import morphology
from skimage.filters import sobel
from skimage.feature import canny
from skimage.measure import perimeter
import socket
import sys


def morph2d(settings_file):

    version = '2016-6-8'

    print "Loading settings from %s..." % settings_file
    run = settings.parse(settings_file)

    if not os.path.exists(run['out_directory']):
        os.mkdir(run['out_directory'])

    print str(datetime.now())

    image_list = images.list_files(run['directory']+os.sep+run['subdirectory'], run['input_ext'])

    for image in image_list:

        print image
        outline = extract_outline(image, run)


def extract_outline(image_file, run):

    image = images.load(image_file, run)

    size = np.shape(image)

    print "Extracting outline for ", image_file

    # morphological opening
    image_open = morphology.opening(image, morphology.disk(10))

    # Not yet implemented: Gamma adjustment and RGB Filter
    image_gamma = image_open
    image_rgb = image_gamma

    # Convert to grayscale and then black and white
    image_gs = rgb2gray(image_rgb)

    ret2, threshold = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    if threshold + run['threshold_adjustment'] >= 0:
        image_bw = im2bw(image_gs, threshold+run['threshold_adjustment'])
    else:
        print 'Threshold adjustment value too large! Using automatic value for', image_file
        image_bw = im2bw(image_gs, threshold)

    # Fill holes, remove border objects, and delete remaining background noise
    # from thresholded object
    image_filled = ndimage.morphology.binary_fill_holes(image_bw/255.).astype(int)*255

    # Not yet implemented: CLEAR BORDER
    image_cleared = image_filled

    # remove noisy objects that are 5% of the total image size or smaller
    noise_limit_size = int(math.ceil(size[0]*size[1]*run['noise_limit]']))
    obj = np.ones(noise_limit_size, noise_limit_size)

    # Not yet implemented
    image_cleaned = 

    # detect edge
    # get unsmoothed edge
    unsmooth_edge = sobel(image_cleaned)

    # Get smoothed edge and delete small (relative to entire perimeter)
    # unconnected components that may result during smoothing process...
    smooth_edge = canny(image_cleaned, run['smoothing_sigma'])
    if np.amax(image_cleaned) != 0:
        smooth_perimeter = math.ceil(perimeter(smooth_edge) * 0.0)
        # Not yet implemented
        smooth_edge = 

    # save output files
    object_id = '.'/join(image_file.split(',')[0:-1])

    if run['save_intermediate']:
        images.save(image_open, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_1_open.tif')
        images.save(image_gamma, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_2_gamma.tif')
        images.save(image_rgb, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_3_rgbfilter.tif')
        images.save(image_gs, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_4_grayscale.tif')
        images.save(image_bw, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_5_bw.tif')
        images.save(image_filled, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_6_fill.tif')
        images.save(image_cleared, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_7_border.tif')
        images.save(image_cleaned, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_8_noise.tif')
        images.save(unsmooth_edge, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_9_edge.tif')
        images.save(smooth_edge, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_10_smooth.tif')

    diff = diff(image, smooth_edge)
    images.save(image_diff, run['out_directory']+os.sep+str(sampleID)+'_'+object_id+'_final.tif')


def rgb2gray(rgb):

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray


def im2bw(image, threshold):

    image[image < 255 * threshold] = 0     # Black
    image[image >= 255 * threshold] = 255  # White


if __name__ == "__main__":

    if socket.gethostname() == 'tide.geology.yale.edu':
        os.nice(10)

    if len(sys.argv) == 2:
        morph2d(sys.argv[1])

    else:
        print 'Usage: run2dmorph <settings_file>'
        sys.exit('Error: incorrect usage')
