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
        print ' '.join(["INFO: Extracting outline for",image_name])
    size = image.shape

    # Tag dictionary for saving intermediate image files if requested by user
    tagDict =   {   1:'morphopen.jpg',
                    2:'rgbfilter.jpg',
                    3:'contrast.jpg',
                    4:'grayscale.jpg',
                    5:'bw.jpg',
                    6:'fill.jpg',
                    7:'border.jpg',
                    8:'noise.jpg',
                    9:'edge.jpg',
                    10:'smooth.jpg'
                }
    try:
        # Morphological opening (erosion followed by dilation)
        image_open = filters.morphOpen(image,settings['disk_size_opening'])
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_open,image_name,'_'.join(['1',tagDict[1]]))
        # RGB filter
        image_rgb = filters.rgbFilter(image_open)
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_rgb,image_name,'_'.join(['2',tagDict[2]]))

        # Contrast adjustment
        image_contrast = filters.contrastAdjust(image_rgb,settings['contrast_adjustment'])
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_contrast,image_name,'_'.join(['3',tagDict[3]]))

        # Grayscale conversion
        image_gray = filters.rgb2gray(image_contrast)
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_gray,image_name,'_'.join(['4',tagDict[4]]))

        # Black & White conversion
        image_bw = filters.convertBW(image_gray,image_name,settings['threshold_adjustment'])
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_bw,image_name,'_'.join(['5',tagDict[5]]))

        # Created hole-filled version and -unfilled version (the latter is for
        # run3dmorph)
        image_filled = filters.fillHoles(image_bw)
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_filled,image_name,'_'.join(['6',tagDict[6]]))
        if run3dmorph:
            image_unfilled = image_bw

        # Remove objects that touch border
        image_border = filters.clearBorder(image_filled,size)
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_border,image_name,'_'.join(['7',tagDict[7]]))
        if run3dmorph:
            image_border_unfilled = filters.clearBorder(image_unfilled,size)

        # Remove background noise
        image_clean = filters.removeNoise(image_border)
        if settings['save_intermediates']:
            save.saveIntermediates(settings,image_clean,image_name,'_'.join(['8',tagDict[8]]))
        if run3dmorph:
            image_clean_unfilled = filters.removeNoise(image_border_unfilled)

        # Edge detection (original)
        edge_unsmoothed = cv2.Canny(image_clean,100,200) * 1
        if settings['save_intermediates']:
            save.saveIntermediates(settings,edge_unsmoothed,image_name,'_'.join(['9',tagDict[9]]))
        # Smooth image
        if not run3dmorph:
            image_smoothed = filters.smoothImage(image_clean,settings['disk_size_smoothing'])
            # Edge detection (smoothed)
            edge_smoothed = cv2.Canny(image_smoothed,100,200) * 1
            if settings['save_intermediates']:
                save.saveIntermediates(settings,edge_smoothed,image_name,'_'.join(['10',tagDict[10]]))
        print ''
    except:
        print ' '.join(["ERROR: Outline extraction failed; check intermediates and/or input parameters\n"])

    # Save final image of extracted outline overlaid on original image
    if not run3dmorph:
        try:
            save.saveFinalOverlay(settings,image,edge_unsmoothed,image_name)
        except:
            return None # Return nothing if outline extraction runs into trouble

        return edge_unsmoothed,edge_smoothed,image_clean,image_smoothed,image_border # Return necessary output for 2dmorph

    else:
        try:
            return edge_unsmoothed,image_clean,image_clean_unfilled # Return necessary output for 3dmorph
        except:
            return None # Unless something went wrong
