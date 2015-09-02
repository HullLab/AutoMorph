from aux import debug_msg

import xml.etree.ElementTree as xml_tree
from skimage.measure import regionprops
from PIL import Image

import numpy as np
from scipy import ndimage
import time
import glob
import math
import os


def load(filename, run):

    start = time.time()

    # Get the dimensions of the image
    img = Image.open(filename)
    m_image, n_image = img.size

    # Get the microns-per-pixel values
    (m_x, m_y, _) = microns_per_pixel_xml(filename)

    # Calculate the new dimensions

    scale_factor_y = run['microns_per_pixel'] / m_y
    scale_factor_x = run['microns_per_pixel'] / m_x

    m_resized = int(math.ceil(scale_factor_x * n_image))
    n_resized = int(math.ceil(scale_factor_y * m_image))

    # resize image
    scaled = img.resize((m_resized, n_resized), Image.ANTIALIAS)
    del img

    # apply the border
    border_size = 0.01
    img = border(scaled, border_size)
    del scaled

    end = time.time()
    debug_msg('INFO: images.load() processed %s ( %f seconds)' % (filename, end-start), run['debug'] >= 1)

    return img


def list_files(directory, verbosity, file_extension='tif'):
    '''
    This function takes a directory and returns a list of all TIF images in that
    directory
    '''

    file_list = glob.glob(directory+os.sep+"*."+file_extension)

    if verbosity >= 1:
        num_files = len(file_list)

        debug_msg('INFO: images.find() found %d files' % num_files, True)

    return file_list


def find_objects(img, run):

    # Make image black and white
    bw_img = img.convert('L')
    bw_img = np.array(bw_img)
    # Pixel range is 0...255
    bw_img[bw_img < 255*run['threshold']] = 0     # Black
    bw_img[bw_img >= 255*run['threshold']] = 255  # White

    # and fill holes
    bw_filled_img = ndimage.morphology.binary_fill_holes(bw_img)

    # label connected objects
    connected_objs, n = ndimage.measurements.label(bw_filled_img)
    print connected_objs

    # Create list of bounding boxes and filled
    box_list = regionprops(connected_objs).bbox
    num_objects = len(box_list)

    # Extract the size of the bounding box into arrays
    size_x = box_list[]  # take every 4th element starting at 3 (width)
    size_y = box_list[]  # take ever 4th element starting at 4 (hieght)

    minimum_size = run['minimum_size'] / run['microns_per_pixel']
    maximum_size = run['maximum_size'] / run['microns_per_pixel']

    minimum_size = sqrt((minimum_size * maximum_size) / 2.)
    box_list = box_list[]

    box_list = expand_bounding_box(box_list, 0.20, n)

    debug_msg('INFO: findObjects -> %d total [ Thresh: %f ] -->  %d valid'
              % (n, run['threshold'], len(box_list)), run['debug'] >= 1)

    return box_list


def border(img, border_size):

    height, width = img.size
    img = np.array(img)

    # Top, Bottom, Left, Right
    img[:round(height * border_size), :, :] = 0
    img[height-round(height * border_size * 6):height, :, :] = 0
    img[:, :round(width * border_size), :] = 0
    img[:, width-round(width * border_size):width, :] = 0

    return Image.fromarray(np.uint8(img))


def microns_per_pixel_xml(filename):

    xml_name = os.path.splitext(filename)[0]+'.xml'
    # Get the microns-per-pixel values:
    root = xml_tree.parse(xml_name).getroot()

    sub_root = root.findall('Calibration')[0]
    x = float(sub_root.findtext('MicronsPerPixelX'))
    y = float(sub_root.findtext('MicronsPerPixelY'))

    # Calculate the new dimensions
    m_p_p = round(y * 10) / 10.0  # Nearest tenth of original factor
    return x, y, m_p_p
