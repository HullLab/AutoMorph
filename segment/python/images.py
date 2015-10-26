import xml.etree.ElementTree as xml_tree
from skimage.measure import regionprops
from skimage import color
from PIL import Image, ImageFont, ImageDraw, TiffImagePlugin
import tifffile

import numpy as np
from scipy import ndimage, misc
import time
import glob
import math
import os


def load(filename, run):
    '''
    Load image from given path and resizes it.
    '''

    start = time.time()

    try:
        img = Image.open(filename)
        img = np.array(img)
    except IOError:
        if run['input_ext'] == 'tif':
            print "File may be a BIGtiff, attempting alternate read..."
            img = tifffile.imread('Plane031.tif')
        else:
            raise

    print np.shape(img)
    end = time.time()
    print 'INFO: images.load() processed %s ( %f seconds)' % (filename, end-start)

    return img


def save(image, filename, tags=''):

    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(image)

    if tags:
        image.save(filename, tiffinfo=tags)
    else:
        image.save(filename)


def save_overview_image(full_image, box_list, orig_filename, run):
    '''
    Save low resolution jpg of entire image with boxes marked
    '''

    # if bigtiff, drop resolutions significantly

    full_image = draw_bounding_boxes(full_image, box_list)

    # save entire image
    if run["mode"] == "final":
        output_dir = run['full_output'].replace('/final', '')
    else:
        output_dir = run['full_output']
    filename_full_image = "%s%s%s_boxes_%s.jpg" % (output_dir, os.sep, run['unique_id'],
                                                   run['image_file_label'])

    description = 'Full Image'
    labeled_image, _ = label_image(full_image, orig_filename, description, run)

    save(labeled_image, filename_full_image)


def add_comment(filename, comment):

    tags = TiffImagePlugin.ImageFileDirectory()
    tags[270] = comment
    tags.tagtype['Description'] = 2

    Image.DEBUG = False
    TiffImagePlugin.WRITE_LIBTIFF = True

    return tags


def list_files(directory, file_extension):
    '''
    This function takes a directory and returns a list of all TIF images in that
    directory
    '''

    file_list = glob.glob(directory+os.sep+"*."+file_extension)

    print 'INFO: images.find() found %d files' % len(file_list)

    return sorted(file_list)


def resize(image, filename, run):
    '''
    Scales image based on units per pixel
    DEPRECATED: this function existed to deal with non-square pixels but is non-square
    longer needed.
    '''
    # if isinstance(image, (np.ndarray, np.generic)):
    #    image = Image.fromarray(image)

    print 'INFO: resizing...'
    height, width, _ = np.shape(image)
    # x_image, y_image = image.size
    # Calculate the new dimensions

    scale_factor_x = run['units_per_pixel'] / run['pixel_size_x']
    scale_factor_y = run['units_per_pixel'] / run['pixel_size_y']

    # if scale_factor_x == 1 and scale_factor_y == 1:
    #    return image

    m_resized = int(math.ceil(scale_factor_x * width))
    n_resized = int(math.ceil(scale_factor_y * height))

    # return image.resize((m_resized, n_resized), Image.ANTIALIAS)
    return ndimage.zoom(image, (scale_factor_y, scale_factor_x))


def crop(image, box):

    image_subsample = image[box[1]:box[3], box[0]:box[2], :]

    return image_subsample


def rgb2gray(rgb):

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray


def find_objects(img, run):

    bw_img = rgb2gray(img)

    # Pixel range is 0...255
    bw_img[bw_img < 255*run['threshold']] = 0     # Black
    bw_img[bw_img >= 255*run['threshold']] = 255  # White

    # and fill holes
    bw_filled_img = ndimage.morphology.binary_fill_holes(bw_img/255.).astype(int)*255

    # label connected objects
    connected_objs, n = ndimage.measurements.label(bw_filled_img)

    # Create list of bounding boxes and filled
    region_list = regionprops(connected_objs)
    num_objects = len(region_list)

    bounding_boxes = [region.bbox for region in region_list]

    # Extract the size of the bounding box into arrays
    size_x = np.array([box[2]-box[0] for box in bounding_boxes])
    size_y = np.array([box[3]-box[1] for box in bounding_boxes])

    minimum_size = run['minimumSize'] / run['units_per_pixel']
    maximum_size = run['maximumSize'] / run['units_per_pixel']

    # Eliminate all boxed objects with a dimension smaller than the minimum and a huge area:
    # True minimum length can be smaller if the minimum length is oriented at a 45-degree angle,
    # so calculate it for vertical / horizontal minimums:
    minimum_size = math.sqrt((minimum_size * minimum_size) / 2.)
    mask = ((size_x > minimum_size) & (size_x < maximum_size) &
            (size_y > minimum_size) & (size_y < maximum_size))

    box_list = np.array(bounding_boxes)
    box_list = box_list[mask]

    box_list = expand_bounding_box(box_list, 0.20, connected_objs.shape)

    print 'INFO: findObjects -> %d total [ Thresh: %f ] -->  %d valid' % (n, run['threshold'],
                                                                          len(box_list))

    return box_list


def add_label_area(image):

    minimum_width = 640

    image = np.array(image)

    height, width, _ = np.shape(image)

    # If we're less than minimumX in the X direction, pad with black:
    if width < minimum_width:
        padding_width = math.ceil((minimum_width - width) / 2)
        padding = np.zeros([height, padding_width, 3])
        image = np.hstack((padding, image, padding))
        width += padding_width*2

    label_area = np.empty([160, width, 3])
    label_area.fill(255)

    image = np.vstack((image, label_area))

    return Image.fromarray(np.uint8(image))


def label_image(orig_image, orig_filename, description, run):

    orig_height = np.shape(orig_image)[0]

    image = add_label_area(orig_image)

    mid_x = image.size[0]/2
    draw = ImageDraw.Draw(image)

    # Draw scale bars
    bar_in_pixels_25 = 25 / run['units_per_pixel']
    bar_in_pixels_100 = bar_in_pixels_25 * 4.

    y_100 = orig_height+7
    y_25 = y_100 + 10
    width = 2

    start_100_x = int(mid_x - bar_in_pixels_100/2)
    start_25_x = int(mid_x - bar_in_pixels_25/2)

    draw.line((start_100_x, y_100, start_100_x + bar_in_pixels_100, y_100), fill='black', width=width)
    draw.line((start_25_x, y_25, start_25_x + bar_in_pixels_25, y_25), fill='black', width=width)

    font = set_fontsize(10)
    draw.text((start_100_x+bar_in_pixels_100+10, y_100 - 4), '100 '+run['unit'], fill='black', font=font)
    draw.text((start_25_x+bar_in_pixels_25+10, y_25 - 4), '25 '+run['unit'], fill='black', font=font)

    orig_filename = os.path.basename(orig_filename)

    label = run['image_label'][:]
    label.insert(0, description)
    label.append('File: %s' % orig_filename)

    text_y = y_25 + 7 + np.array([0, 20, 40, 70, 85, 100, 115])
    text_size = [14, 14, 14, 9, 9, 9, 9]

    for i, line in enumerate(label):
        font = set_fontsize(text_size[i])
        w, h = draw.textsize(line, font=font)
        new_x = (mid_x*2 - w)/2
        draw.text((new_x, text_y[i]), line, fill='black', font=font)

    return image, label


def set_fontsize(font_size):

    font_path = os.path.dirname(os.path.realpath(__file__))+os.sep+'OpenSans-Regular.ttf'
    return ImageFont.truetype(font_path, font_size)


def draw_bounding_boxes(image, box_list):
    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(np.uint8(image))

    draw = ImageDraw.Draw(image)

    # Mark the bounding boxes of all objects
    for i, box in enumerate(box_list):
        y1 = math.ceil(box[0])
        x1 = math.ceil(box[1])
        y2 = math.ceil(box[2])
        x2 = math.ceil(box[3])

        draw.line([x1, y2, x2, y2], fill='red', width=20)
        draw.line([x1, y1, x2, y1], fill='red', width=20)
        draw.line([x1, y1, x1, y2], fill='red', width=20)
        draw.line([x2, y1, x2, y2], fill='red', width=20)

        font = set_fontsize(40)
        draw.text((x2+40, y2), str(i+1), fill='red', font=font)

    return image


def expand_bounding_box(box_list, scale_factor, i_size):

    num_boxes = len(box_list)

    for i, bounding_box in enumerate(box_list):
        width = bounding_box[3]-bounding_box[1]
        height = bounding_box[2]-bounding_box[0]

        # bounding_box -> (min_row, min_col, max_row, max_col)
        new_top = bounding_box[0] - round(height * scale_factor)
        if new_top < 1:
            new_top = 0

        new_left = bounding_box[1] - round(width * scale_factor)
        if new_left < 1:
            new_left = 0

        new_bottom = bounding_box[2] + round(height * scale_factor)
        if new_bottom > i_size[0]:
            new_bottom = i_size[0]

        new_right = bounding_box[3] + round(width * scale_factor)
        if new_right > i_size[1]:
            new_right = i_size[1]

        new_box = [new_top, new_left, new_bottom, new_right]
        box_list[i] = new_box

    return box_list


def microns_per_pixel_xml(filename):

    xml_name = os.path.splitext(filename)[0]+'.xml'
    # Get the microns-per-pixel values:
    root = xml_tree.parse(xml_name).getroot()

    sub_root = root.findall('Calibration')[0]
    x = float(sub_root.findtext('MicronsPerPixelX'))
    y = float(sub_root.findtext('MicronsPerPixelY'))

    return x, y
