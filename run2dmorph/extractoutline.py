#!/usr/bin/env python

import filters

# Exception for run3dmorph operation
try:
    import images
    import save
except:
    pass

import os
import cv2
import numpy as np


def extractOutline(settings,image_name,image,run3dmorph):
    '''
    Runs image filters (see Hsiang et al. 2017, Figure 4) to extract 2D outline
    of object.
    '''
    if not run3dmorph:
        print ' '.join(["INFO: Extracting outline for",image_name,'\n'])
    size = image.shape

    # Morphological opening (erosion followed by dilation)
    image_open = filters.morphOpen(image,settings['disk_size_opening'])

    # RGB filter
    image_rgb = filters.rgbFilter(image_open)

    # Contrast adjustment
    image_contrast = filters.contrastAdjust(image_rgb,settings['contrast_adjustment'])

    # Grayscale conversion
    image_gray = filters.rgb2gray(image_contrast)

    # Black & White conversion
    image_bw = filters.convertBW(image_gray,image_name,settings['threshold_adjustment'])

    # Created hole-filled version and -unfilled version (the latter is for
    # run3dmorph)
    image_filled = filters.fillHoles(image_bw)
    if run3dmorph:
        image_unfilled = image_bw

    # Remove objects that touch border
    image_border = filters.clearBorder(image_filled,size)
    if run3dmorph:
        image_border_unfilled = filters.clearBorder(image_unfilled,size)

    # Remove background noise
    image_clean = filters.removeNoise(image_border)
    if run3dmorph:
        image_clean_unfilled = filters.removeNoise(image_border_unfilled)

    # Smooth image
    if not run3dmorph:
        image_smoothed = filters.smoothImage(image_clean,settings['disk_size_smoothing'])
        # Edge detection (smoothed)
        edge_smoothed = cv2.Canny(image_smoothed,100,200) * 1
    # Edge detection (original)
    edge_unsmoothed = cv2.Canny(image_clean,100,200) * 1

    # Save output files
    if not run3dmorph:
        # Save intermediates if requested by user
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_rgb,image_contrast,image_gray,image_bw,image_filled,image_border,image_clean,edge_unsmoothed,edge_smoothed,image_name)
        # Save final image of extracted outline overlaid on original image
        save.saveFinalOverlay(settings,image,edge_unsmoothed,image_name)

        return edge_unsmoothed,edge_smoothed,image_clean,image_smoothed,image_border

    else:
        return edge_unsmoothed,image_clean,image_clean_unfilled
