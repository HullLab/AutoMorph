#!/usr/bin/env python

import numpy as np
from scipy import interpolate
import pandas


def extractCoordinates(edge,downsample,num_points,region_properties):
    '''
    Takes extracted 2D outline of object and returns x,y-coordinates corresponding
    to outline, downsampling if requested by user.
    '''
    all_coords = np.where(edge == 255)
    x_coords = list(all_coords[0])
    y_coords = list(all_coords[1])
    num_coords = len(x_coords)

    # Translate coordinates so that centroid is at (0,0)
    centroid = region_properties.centroid
    xc = [x - centroid[0] for x in x_coords]
    yc = [y - centroid[1] for y in y_coords]

    if downsample:
        # ORDERING POINTS
        # Convert cartesian coordinates to polar coordinate system
        rho = [np.sqrt(x ** 2 + y ** 2) for x,y in zip(xc,yc)]
        phi = [np.arctan2(y,x) for x,y in zip(xc,yc)]

        # Sort by increasing order of phi
        pr_sorted = sorted(zip(phi,rho))
        phis = [p[0] for p in pr_sorted]
        rhos = [r[1] for r in pr_sorted]

        # Convert back to cartesian coordinates (now ordered)
        xs = [r * np.cos(p) for p,r in zip(phis,rhos)]
        ys = [r * np.sin(p) for p,r in zip(phis,rhos)]

        # INTERPOLATION
        # First decimate points naively by slicing
        slice_factor = int(round(num_coords / num_points))
        xd = xs[::slice_factor]
        yd = ys[::slice_factor]

        # Close circle by appending first coordinate to end of coordinate list
        xdr = np.r_[xd,xd[0]]
        ydr = np.r_[yd,yd[0]]

        # Interpolate using closed, ordered, decimated coordinates
        tck,u = interpolate.splprep([xdr,ydr],s=0,per=True)
        xi,yi = interpolate.splev(np.linspace(0,1,num_points),tck)

        return np.column_stack((yi,-xi))

    else:

        return np.column_stack((np.array(yc),-np.array(xc)))
