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


def save(image, filename):

    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(np.uint8(image))

    image.save(filename)


def list_files(directory, verbosity, file_extension='tif'):
    '''
    This function takes a directory and returns a list of all TIF images in that
    directory
    '''

    file_list = glob.glob(directory+os.sep+"*."+file_extension)

    if verbosity >= 1:
        num_files = len(file_list)

        debug_msg('INFO: images.find() found %d files' % num_files, True)

    print file_list
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
    region_list = regionprops(connected_objs)
    num_objects = len(region_list)

    bounding_boxes = [region.bbox for region in region_list]

    # Extract the size of the bounding box into arrays
    size_x = np.array([box[2] for box in bounding_boxes])  # take every 4th element starting at 3 (width)
    size_y = np.array([box[3] for box in bounding_boxes])  # take every 4th element starting at 4 (height)

    minimum_size = run['minimumSize'] / run['microns_per_pixel']
    maximum_size = run['maximumSize'] / run['microns_per_pixel']

    minimum_size = math.sqrt((minimum_size * maximum_size) / 2.)
    mask = ((size_x > minimum_size) & (size_x < maximum_size) &
            (size_y > minimum_size) & (size_y < maximum_size))

    box_list = np.array(bounding_boxes)
    box_list = box_list[mask]

    box_list = expand_bounding_box(box_list, 0.20, connected_objs.shape)

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


def expand_bounding_box(box_list, scale_factor, i_size):

    num_boxes = len(box_list)

    for i, bounding_box in enumerate(box_list):
        # PROBABLY WRONG SINCE BOUNDING BOXES ARE DEFINED DIFFERENTLY
        # (min_row, min_col, max_row, max_col)
        new_left = bounding_box[0] - round(bounding_box[2] * scale_factor)
        if new_left < 1:
            new_left = 1

        new_top = bounding_box[1] - round(bounding_box[3] * scale_factor)
        if new_top < 1:
            new_top = 1

        new_width = bounding_box[2] + round(bounding_box[2] * 2 * scale_factor)
        if new_left + new_width > i_size[1]:
            new_width = i_size[1] - new_left - 1

        new_height = bounding_box[3] + round(bounding_box[3] * 2 * scale_factor)
        if new_top + new_height > i_size[0]:
            new_height = i_size[0] - new_top - 1

        new_box = [new_left, new_top, new_width, new_height]
        box_list[i] = new_box

    return box_list


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
