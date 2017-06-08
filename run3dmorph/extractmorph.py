#!/usr/bin/env python

from scipy import ndimage
from skimage.measure import regionprops


def getRegionProps(binary_image):
    '''
    Returns region properties for object identified by outine extraction,
    both original (unsmoothed) and smoothed.
    '''
    labels,a = ndimage.label(binary_image)
    properties = regionprops(labels)[0]

    return properties


def extractMorphology(original_props,smoothed_props):
    '''
    Returns relevant 2D measurements from region properties.
    '''
    area = original_props.area
    eccentricity = original_props.eccentricity
    perimeter = original_props.perimeter
    majorAxisLength = original_props.major_axis_length
    minorAxisLength = original_props.minor_axis_length
    rugosity = original_props.perimeter / smoothed_props.perimeter

    measures = {
                'Area': area,
                'Eccentricity': eccentricity,
                'Perimeter': perimeter,
                'MajorAxisLength': majorAxisLength,
                'MinorAxisLength': minorAxisLength,
                'Rugosity': rugosity
                }

    return measures
