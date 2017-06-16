#!/usr/bin/python

from __future__ import division

import os
import time

import extractoutline
import extractmorph
import extractcoordinates
import initialize
import aspectratio

import numpy as np
import cv2
from scipy.ndimage.filters import generic_filter

from scipy.spatial import Delaunay
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from matplotlib.tri.triangulation import Triangulation


def macroSetup(heightmap):
    '''
    Inverts ImageJ heightmap if object being processed is macro-scale (i.e.,
    original images taken with camera instead of microscope).
    '''
    heightmap_inverted = 255 - heightmap
    return heightmap_inverted


def resize(image,x_calibration,y_calibration):
    '''
    Resizes an image.
    '''
    resized = cv2.resize(image,(0,0),fx=x_calibration,fy=y_calibration)
    return resized


def imagePreparation(settings,obj):
    '''
    Reads in heightmap and original image in RGB colorspace, performs macro
    adjustments if necessary, and resizes the images based on user-input
    calibration values.
    '''
    hmap = cv2.imread(obj.heightmap,0)
    rgb = cv2.cvtColor(cv2.imread(obj.rgb),cv2.COLOR_BGR2RGB)

    if settings['macro']:
        hmap = macroSetup(hmap)

    hmap_resized = resize(hmap,settings['pixel_size_x'],settings['pixel_size_y'])
    rgb_resized = resize(rgb,settings['pixel_size_x'],settings['pixel_size_y'])

    return hmap_resized,rgb_resized


def pixelToHeight(heightmap,slices,zstep):
    '''
    Converts every individual grayscale pixel value in heightmap to real world
    height based on number of z-slices and z-step distance in object's original
    image stack.
    '''
    scale = 255 // slices
    heights = (heightmap / scale) * zstep
    return heights


def outlierFilter(kernel):
    '''
    Computes median and upper and lower quartiles of height values; returns
    median value if center pixel of kernel is higher or lower than the upper
    and lower quartile values, respectively. Input for Scipy's generic_filter
    function, which applies this function to all pixels in the image.
    '''
    # Calculate quartiles
    [q25,q50,q75] = [np.percentile(kernel[:],x) for x in [25,50,75]]
    # Kernel is reshaped into a (k x k) x 1 array
    center_index = int((kernel.shape[0] - 1) / 2)
    if kernel[center_index] < q25 or kernel[center_index] > q75:
        return q50
    else:
        return kernel[center_index]


def countPerLevel(image):
    '''
    Returns number of pixels in each unique height level.
    '''
    counts = dict(zip(*np.unique(image,return_counts=True)))
    return counts


def deleteOutliers(image,counts):
    '''
    Deletes pixels at outlier heights, i.e., pixels at height levels for which
    the number of pixels occupying that height level is less than 1% of the total
    number of pixels in the image.
    '''
    lvls_to_delete = []
    for lvl in counts:
        if (counts[lvl] / sum(counts.itervalues())) < 0.01:
            lvls_to_delete.append(lvl)
    for lvl in lvls_to_delete:
        # If outlier point is surrounded by non-zero points, set the outlier
        # equal to the average of its 4-connected neighbors. Otherwise, set the
        # outlier equal to 0.
        currentPoints = np.where(image == lvl)
        # Loop over all outlier points
        for i in range(len(currentPoints[0])):
            x = currentPoints[0][i]
            y = currentPoints[1][i]
            # Find 4-connected neighbors
            neighbors = [image[x,y+1],image[x-1,y],image[x+1,y],image[x,y-1]]
            if all(neighbors):
                average = np.mean(neighbors)
                image[x,y] = average
            else:
                image[x,y] = 0

    return image


def meshDelaunay(settings,heights):
    '''
    Convert coordinates to mesh using Delaunay triangulation. Also returns
    colormap for writing the mesh in IDTF format, surface triangles from
    triangulation (as opposed to tetrahedra), and the top surface area of
    the mesh.
    '''
    # Get coordinates of all height points (omitting zeros)
    coordinates = np.where(heights != 0)
    x_3D = coordinates[0]
    y_3D = coordinates[1]

    # Generate 3D mesh from heights using meshgrid and griddata
    dx = (max(x_3D) - min(x_3D)) / settings['grid_size']
    dy = (max(y_3D) - min(y_3D)) / settings['grid_size']

    x_grid = np.linspace(min(x_3D),max(x_3D),max(dx,dy))
    y_grid = np.linspace(min(y_3D),max(y_3D),max(dx,dy))

    X,Y = np.meshgrid(x_grid,y_grid)
    z = np.array([heights[x_3D[i],y_3D[i]] for i in range(len(coordinates[0]))])
    Z = griddata((x_3D,y_3D),z,(X,Y))

    # Convert NaNs to zeros and find non-zero coordinates
    Z[np.isnan(Z)] = 0
    nonZero = np.where(Z > 0) # Indices of non-zero points
    # Subset X,Y, and Z to contain only non-zero points
    Z_nz = Z[nonZero[0],nonZero[1]]
    X_nz= np.array([X[0][xi] for xi in nonZero[0]])
    Y_nz = np.array([Y[:,0][yi] for yi in nonZero[1]])

    xyz_points = np.column_stack((X_nz,Y_nz,Z_nz))
    triangulation = Delaunay(xyz_points)

    # Get surface triangles
    triang,args,kwargs = Triangulation.get_from_args_and_kwargs(X_nz,Y_nz,Z_nz,triangles=triangulation.simplices)
    triangles = triang.get_masked_triangles() # From matplotlib.tri.triangulation

    # Get color values for mesh triangle faces
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_trisurf(X_nz,Y_nz,Z_nz,triangles=triangles,cmap=plt.cm.viridis)
    m = plt.cm.ScalarMappable(cmap=surf.cmap,norm=surf.norm)
    colors = m.to_rgba(Z_nz)

    return z,triangulation,triangles,colors


def writeCoordinates(obj,triangulation):
    '''
    Writes a CVS file containing x,y,z-coordinates for extracted mesh.
    '''
    coordinates = triangulation.points
    with open(obj.coordinates,'wb') as f:
        f.write('object,x,y,z\n')
        for coord in coordinates:
            line = ','.join([obj.name,str(coord[0]),str(coord[1]),str(coord[2])])
            f.write('{:s}\n'.format(line))


def getTopBottom(image,heights):
    '''
    Returns the distance between the background (height = 0) and the
    beginning of the mesh (bottom height), although with length and
    width of the minimum bounding box enclosing the object.
    '''
    mbb,_ = aspectratio.getMBB(image)
    length,width,_ = aspectratio.measureMBB(mbb)
    bottom_height = np.amin(heights[np.nonzero(heights)]) # Height from 0 to bottom of mesh
    top_height = np.amax(heights) # Top height of mesh

    return length,width,bottom_height,top_height


def aperture(binary_outline,binary_outline_unfilled,heights,bottom_height):
    '''
    If aperture present, replaces pixel values of aperture with average pixel
    value from getAverageLevel().
    '''
    mask = np.pad(binary_outline,1,'constant')
    flooded = cv2.floodFill(binary_outline_unfilled,mask,(0,0),1)
    aperture = np.where(binary_outline_unfilled == 0)

    if len(aperture[0]):
        for i in range(len(aperture[0])):
            x = aperture[0]
            y = aperture[1]
            heights[x[i],y[i]] = bottom_height

    return heights



def extractMesh(settings,obj):
    '''
    Extracts semi-3D mesh using ImageJ-generated heightmap.
    '''
    # Start timer on object processing
    start = time.time()

    # Resize height map and focused RGB image, and invert height map if macro = True
    hmap_resized,rgb_resized = imagePreparation(settings,obj)

    # Get 2D binary outline map for background removal
    edge,image_clean,image_clean_unfilled = extractoutline.extractOutline(settings,obj.name,rgb_resized,True)

    # Remove background in height map by performing element-wise multiplication with binary outline map from run2dmorph
    hmap_no_BG = hmap_resized * (image_clean / 255)

    # Convert pixel greyscale values from background-pruned height map to real-world heights
    heights = pixelToHeight(hmap_no_BG,settings['slices'],settings['zstep'])

    # Run neighborhood filter to remove outliers
    k = settings['kernel_outlierfilter'] # Kernel size
    filtered = generic_filter(heights,outlierFilter,(k,k))

    # Get number of pixels on each z-level
    counts = countPerLevel(filtered)

    # Delete outliers from filtered heights
    no_outliers = deleteOutliers(filtered,counts)

    # Get length, width, and top and bottom heights
    length,width,bottom_height,top_height = getTopBottom(image_clean,no_outliers)

    # If aperture present, set aperture height to average height. Also extract length, width,
    # and top and bottom heights
    final_heights = aperture(image_clean,image_clean_unfilled,no_outliers,bottom_height)

    # Extract mesh from x,y,z point cloud
    z_values,triangulation,triangles,faceColors = meshDelaunay(settings,final_heights)

    # Write 3D x,y,z-coordinates file
    writeCoordinates(obj,triangulation)

    end = time.time()
    time_elapsed = end - start
    print '\tINFO: Time elapsed: {0:.3f} seconds\n'.format(time_elapsed)

    return edge,image_clean,triangulation,triangles,faceColors,length,width,bottom_height,top_height
