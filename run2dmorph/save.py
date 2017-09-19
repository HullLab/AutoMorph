#!/usr/bin/env python

import images

import numpy as np
import cv2
import os
import shutil

import pandas
import matplotlib
matplotlib.use('agg') # Agg backend to avoid X-server on Linux
import matplotlib.pyplot as plt


def saveObject2D(dataFrame,sampleID,objectID,measures,height,width,aspectRatio):
    '''
    Adds extracted 2D measurements from current object to compilation data frame.
    '''
    toAdd = pandas.DataFrame(
                            [[
                            sampleID,
                            objectID,
                            measures['Area'],
                            measures['Eccentricity'],
                            measures['Perimeter'],
                            measures['MajorAxisLength'],
                            measures['MinorAxisLength'],
                            measures['Rugosity'],
                            height,
                            width,
                            aspectRatio
                            ]],
                            columns = dataFrame.columns
                            )

    dataFrame = dataFrame.append(toAdd,ignore_index=True)
    return dataFrame


def saveCoordinates(settings,coordinates,sampleID,objectID,object_name,tag):
    '''
    Outputs list of x,y-coordinates to file with name: dst_coordinates_tag.csv.
    '''
    # Populate Pandas dataframe
    save = pandas.DataFrame(columns=['SampleID','ObjectID','x','y'])
    save['x'] = coordinates[:,0]
    save['y'] = coordinates[:,1]
    save['SampleID'] = sampleID
    save['ObjectID'] = objectID

    # Save dataframe to csv
    dst = os.path.join(settings['out_directory'],'coordinates','_'.join([object_name,'coordinates','.'.join([tag,'csv'])]))
    save.to_csv(dst)


def saveMBBFigure(settings,mbb,contour,aspect_ratio,object_name):
    '''
    Save plot of object contour and minimum bounding box with aspect ratio label.
    '''
    # Close minimum bounding box by appending first coordinate to end (? Not sure this is needed)
    mbb_closed = np.r_['0,2',mbb,mbb[0]]

    # Remove redundant axes from contour data structure and close contour
    c = np.vstack(contour).squeeze()
    cc = np.vstack((c,c[0]))

    # Plot figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(cc[:,0],-cc[:,1]) # Negate y-points to reflect outline over x-axis
    plt.gca().set_aspect('equal',adjustable='box')
    plt.plot(mbb_closed[:,0],-mbb_closed[:,1],'r--')
    plt.text(0.01,0.96,'Aspect ratio = {0:.4f}'.format(aspect_ratio),transform=ax.transAxes)

    # Save output figure
    dst = os.path.join(settings['out_directory'],'aspect_ratio','_'.join([object_name,'aspect_ratio.pdf']))
    fig.savefig(dst)

    plt.close()


def saveIntermediates(settings,image_rgb,image_contrast,image_gray,image_bw,image_filled,image_border,image_clean,edge_unsmoothed,edge_smoothed,image_name):
    '''
    Saves intermediate files (output of each individual image filter).
    '''
    images.save(image_rgb,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'1','rgbfilter.tif'])))
    images.save(image_contrast,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'2','contrast.tif'])))
    images.save(image_gray,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'3','grayscale.tif'])))
    images.save(image_bw,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'4','bw.tif'])))
    images.save(image_filled,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'5','fill.tif'])))
    images.save(image_border,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'6','border.tif'])))
    images.save(image_clean,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'7','noise.tif'])))
    images.save(edge_unsmoothed,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'8','edge.tif'])))
    images.save(edge_smoothed,os.path.join(settings['out_directory'],'intermediates','_'.join([settings['sampleID'],image_name,'9','smooth.tif'])))


def saveFinalOverlay(settings,image,edge,image_name):
    '''
    # Overlay unsmoothed edge on original image (grayscale) and save resulting image
    '''
    bg = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    overlay = np.where(edge == 255,255,bg)
    filename = os.path.join(settings['out_directory'],'outlines','_'.join([settings['sampleID'],image_name,'final.tif']))
    images.save(overlay,filename)

    # If save_intermediates is on, copy the final image into the intermediates
    # folder for easier comparison of image filter results
    if settings['save_intermediates']:
        shutil.copy2(filename,os.path.join(settings['out_directory'],'intermediates'))
