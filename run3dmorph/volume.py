#!/usr/bin/env python

# Original version of coneSurfaceArea() written by Andrew Wells
# (C3O Consulting; 12-08-15) in MATLAB

from __future__ import division

import aspectratio
import extractmorph
import extractcoordinates

import math
import pandas
import numpy as np
import time

from shapely.geometry.polygon import Polygon


def getVolumeSurfaceArea(settings,obj,image_clean,edge,triangulation,triangles,bottom_height,top_height):
    '''
    Wrapper function for estimating surface area and volume for object,
    assuming one of three 'Platonic' base shapes: 1) Dome; 2) Cylinder; and
    3) Cone. Returns length and width of minimum bounding box of the object
    base for PDF labeling.
    '''
    start = time.time()

    # Calculate top surface area
    top_surface_area = getTopSurfaceArea(triangulation,triangles)

    # Calculate top volume
    top_volume = getTopVolume(triangulation)

    # Get coordinates, 2D area, and 2D perimeter for bottom surface area/volume estimation
    properties = extractmorph.getRegionProps(image_clean)
    measures = extractmorph.extractMorphology(properties,properties)
    area = measures['Area']
    perimeter = measures['Perimeter']
    centroid = np.array(properties.centroid)

    # Get bottom volume and surface area for idealized dome, cylinder, and cone bases
    bd_volume,bd_surface_area = dome(length,width,bottom_height)
    bcy_volume,bcy_surface_area = cylinder(area,perimeter,bottom_height)
    bco_volume,bco_surface_area = cone(bcy_volume,centroid,bottom_height,edge,properties)

    # Get final volumes and surface areas
    dome_volume = bd_volume + top_volume
    dome_surface_area = bd_surface_area + top_surface_area

    cylinder_volume = bcy_volume + top_volume
    cylinder_surface_area = bcy_surface_area + top_surface_area

    cone_volume = bco_volume + top_volume
    cone_surface_area = bco_surface_area + top_surface_area

    # Save 3D measures as CSV file
    saveVolumes(settings,obj,[top_volume,top_surface_area],[dome_volume,dome_surface_area],[cylinder_volume,cylinder_surface_area],[cone_volume,cone_surface_area],length,width,top_height,bottom_height)

    end = time.time()
    time_elapsed = end - start
    print '\tINFO: Time elapsed: {:.3f} seconds\n'.format(time_elapsed)

    return length,width


def getTopVolume(triangulation):
    '''
    Calculates top volume by summing volume of all simplices comprising the mesh.
    '''
    top_volume = 0
    for s in triangulation.simplices:
        vertices = triangulation.points[s]
        top_volume += volumeTetrahedron(vertices)

    #top_volume = sum(z_values - bottom_height)

    return top_volume


def getTopSurfaceArea(triangulation,triangles):
    '''
    Get top surface area by summing areas of all triangles comprising the mesh.
    '''
    coord_groups = [triangulation.points[t] for t in triangles]
    polygons = [Polygon(cg) for cg in coord_groups]
    top_surface_area = sum([x.area for x in polygons])

    return top_surface_area


def saveVolumes(settings,obj,top_measures,dome_measures,cylinder_measures,cone_measures,length,width,top_height,bottom_height):
    '''
    Saves volume and surface area estimates in a CSV file.
    '''
    with open(obj.volume,'wb') as v:
        columns = 'Volume_Dome,Volume_Cylinder,Volume_Cone,Volume_Top,Surface_Area_Dome,Surface_Area_Cylinder,Surface_Area_Cone,Surface_Area_Top,Grid_Size,Height,Base_Height,Width,Length,Base_Unit'
        data = ','.join(map(str,[dome_measures[0],cylinder_measures[0],cone_measures[0],top_measures[0],dome_measures[1],cylinder_measures[1],cone_measures[1],top_measures[1],settings['grid_size'],top_height,bottom_height,width,length,settings['unit']]))
        v.write('{:s}\n{:s}'.format(columns,data))


def volumeTetrahedron(vertices):
    '''
    Calculates the volume of an individual tetrahedron given its vertices.
    '''
    matrix = np.vstack((vertices.T,np.ones(4)))
    volume = (1/6) * np.linalg.det(matrix)
    return abs(volume)


def dome(length,width,height):
    '''
    Volume and surface area estimate for a Platonic dome base.
    '''
    semi_X = length / 2
    semi_Y = width / 2
    semi_Z = height

    bottom_volume = 0.5 * (4/3) * math.pi * semi_X * semi_Y * semi_Z
    p = 1.6075
    bottom_surface_area = (4 * math.pi * ((semi_Z ** p * semi_X ** p + semi_Z ** p * semi_Y ** p + semi_X ** p * semi_Y ** p) / 3) ** (1 / p)) / 2

    return bottom_volume,bottom_surface_area


def cylinder(area2D,perimeter2D,height):
    '''
    Volume and surface area estimate for a Platonic cylinder base.
    '''
    bottom_volume = area2D * height
    bottom_surface_area = (perimeter2D * height) + area2D

    return bottom_volume,bottom_surface_area


def cone(cylinderVolume,centroid2D,height,edge,properties):
    '''
    Volume and surface area estimate for a Platonic cone base.
    '''
    bottom_volume = cylinderVolume / 3

    coordinates = extractcoordinates.extractCoordinates(edge,False,0,properties)

    def coneSurfaceArea(centroid2D,height,coordinates):
        '''
        Approximates the curve surface area of a generalized conical surface,
        where all points on a basal perimeter (rho,phi,0) are joined by a linear
        segment to the vertex at (0,0,H) in cylindrical coordinates (rho,phi,z)
        rho > 0; 0 <= phi <= 2 * pi, H fixed constant.

        Note that this forumulation assumes that the first point has phi
        closest to zero, and last point phi is close to 2 * pi, with phi
        increasing monotonically in between.

        The integration rule used is a midpoint rule (equivalent to approximating
        the integral via small trapeziums, but with possibly unequal width).
        '''
        # Initialize Numpy array to hold distances between coordinates and centroid
        distances = np.empty((len(coordinates),1))

        # Calculate angle of inclination between each coordinate and centroid
        phis = np.arctan2(coordinates[:,0],coordinates[:,1])

        # Loop through coordinates and 1) Calculate distance between coordinate
        # and centroid; and 2) Add 2 * pi to negative phi values so that all phis
        # are placed on a 0 to 2 * pi scale.
        for i,coord in enumerate(coordinates):
            # (1)
            distances[i] = np.linalg.norm(coord - centroid2D)
            # (2)
            if phis[i] < 0:
                phis[i] = phis[i] + (2 * math.pi)

        phi = np.array(sorted(phis))
        indices = [p[0] for p in sorted(enumerate(phis),key=lambda i:i[1])]
        rho = distances[indices]

        # Calculate integrand at each point
        y = 0.5 * rho * np.sqrt((rho ** 2 + height ** 2))
        # Preallocate vector to hold areas of each trapeziums
        areas = np.empty((len(y),1))

        # Calculate area of trapezia between points, one by one
        # For first point, area of trapezium is:
        #       (average of y at edges) * (change in phi)
        # However, we need to subtract off 2 * pi to account for phi
        # jumping from 2 * pi back to zero as we loop around
        areas[0] = 0.5 * (y[0] + y[-1]) * (phi[0] - (phi[-1] - 2 * math.pi))

        # For subsequent points, area of trapezium is:
        #       (average of y at edges) * (change in phi)
        areas[1:] = 0.5 * ((y[0:-1] + y[1:]) * ((phi[1:] - phi[0:-1]).reshape((areas.shape[0]-1,1))))

        # Output total area by summing over areas of all trapezia
        return sum(areas)[0]

    bottom_surface_area = coneSurfaceArea(centroid2D,height,coordinates)

    return bottom_volume,bottom_surface_area
