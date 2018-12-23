#!/usr/bin/env python

import numpy as np
from scipy import signal
import pandas
import math


def getDistance(point1,point2):
    '''
    Calculates Euclidean distance between two points.
    '''
    return math.hypot(point2[0]-point1[0],point2[1]-point1[1])


def extractCoordinates(edge,downsample,num_points,region_properties,major_axis_length):
    '''
    Takes extracted 2D outline of object and returns x,y-coordinates corresponding
    to outline, downsampling if requested by user.
    '''
    all_coords = np.where(edge == 255)
    x_coords = list(all_coords[1])
    y_coords = list(-all_coords[0])
    num_coords = len(x_coords)

    # Translate coordinates so that centroid is at (0,0)
    centroid = region_properties.centroid
    centroid_adjusted = (centroid[1],-centroid[0])
    xc = [x - centroid_adjusted[0] for x in x_coords]
    yc = [y - centroid_adjusted[1] for y in y_coords]
    coords = np.array([(x,y) for x,y in zip(xc,yc)])

    # Set up variables for outline closing
    endgame = False
    min_distance = major_axis_length * 0.01

    # Order points using nearest neighbor
    ordered = [coords[0]]
    processing = np.delete(coords,0,0)

    for i in range(len(coords)):
        distances = [getDistance(ordered[i],processing[j]) for j in range(len(processing))] # Distances between i-th point and i+1-th point
        min_index = np.argmin(distances)

        if distances[min_index] > min_distance:
            processing = np.delete(processing,min_index,0)
            break
        else:
            ordered.append(processing[min_index])
            processing = np.delete(processing,min_index,0)

        if len(processing) == 1:
            break

        # Add starting point to processing list if 75% of points have been processed
        if i == int(0.75 * num_coords):
            np.append(processing,coords[0])
            endgame = True

        #if endgame:
        #    if min_index == len(processing) - 1:
        #        break

    ordered = np.vstack(ordered) # Put points into correct data structure

    if downsample:
        resampled = signal.resample(ordered,num_points)
        return resampled

    else:
        return ordered
