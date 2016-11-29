import xml.etree.ElementTree as xml_tree
from skimage.measure import regionprops
from skimage import color
from PIL import Image, ImageFont, ImageDraw, TiffImagePlugin
import tifffile

import numpy as np
from scipy import ndimage, misc
import cv2
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
        run['bigtiff'] = False
    except IOError:
        if run['input_ext'] == 'tif':
            print "File may be a BIGtiff, attempting alternate read..."
            img = tifffile.imread(filename)
            run['bigtiff'] = True
        else:
            raise

    print np.shape(img)
    end = time.time()
    print 'INFO: images.load() processed %s ( %f seconds)' % (filename, end-start)

    if run['pixel_size_x'] != run['pixel_size_y']:
        print 'INFO: x and y pixel sizes differ, resizing image to have square pixels'
        img = resize(img, run)

    return img


def save(image, filename, tags=''):

    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(image)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    if tags:
        image.save(filename, tiffinfo=tags)
    else:
        image.save(filename)


def save_test_image(image, run, tag):

    # save entire image
    if run["mode"] == "final":
        output_dir = run['full_output'].replace('/final', '')
    else:
        output_dir = run['full_output']

    filename_full_image = "%s%s%s_%s.jpg" % (output_dir, os.sep, run['unique_id'], tag)

    save(image, filename_full_image)


def save_overview_image(image, box_list, orig_filename, run):
    '''
    Save low resolution jpg of entire image with boxes marked
    '''

    if run['bigtiff']:
        # if bigtiff, drop resolutions significantly
        resize_factor = 0.25
        factor = int(round(1/resize_factor))
        # shrunk_image = ndimage.interpolation.zoom(image, [resize_factor, resize_factor, 1])
        shrunk_image = image[::factor, ::factor, :]
        print 'INFO: Finished resizing'
        image = draw_bounding_boxes(shrunk_image, box_list, run, resize_factor=resize_factor)
        
    else:
        image = draw_bounding_boxes(image, box_list, run)    

    # save entire image
    if run["mode"] == "final":
        output_dir = run['full_output'].replace('/final', '')
    else:
        output_dir = run['full_output']
    
    file_label = run['image_file_label']
    if not run['box_once']:
        file_label += "_"+os.path.splitext(os.path.basename(orig_filename))[0]

    filename_full_image = "%s%s%s_boxes_%s.jpg" % (output_dir, os.sep, run['unique_id'],
                                                   file_label)

    description = 'Full Image'
    labeled_image, _ = label_image(image, orig_filename, description, run)

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
    if run['fill_kernel']:
        kernel = np.ones((run['fill_kernel'], run['fill_kernel']), np.uint8)
        bw_filled_img = cv2.morphologyEx(bw_img, cv2.MORPH_CLOSE, kernel)
    else:
        bw_filled_img = ndimage.morphology.binary_fill_holes(bw_img/255.).astype(int)*255

    if run['debug_images']:
        save_test_image(bw_img, run, "bw_img")
        save_test_image(bw_filled_img, run, "bw_filled_img")

    # label connected objects
    connected_objs, n = ndimage.measurements.label(bw_filled_img)

    # Create list of bounding boxes and filled
    region_list = regionprops(connected_objs)
    num_objects = len(region_list)

    bounding_boxes = [region.bbox for region in region_list]

    # Extract the size of the bounding box into arrays
    size_x = np.array([box[2]-box[0] for box in bounding_boxes])
    size_y = np.array([box[3]-box[1] for box in bounding_boxes])

    minimum_size = run['minimum_size'] / run['units_per_pixel']
    maximum_size = run['maximum_size'] / run['units_per_pixel']

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
    bar_in_pixels_L = run['scale_bar_length']/run['units_per_pixel']
    bar_in_pixels_S = bar_in_pixels_L / 4.
    bar_in_units_S = run['scale_bar_length'] / 4.

    y_L = orig_height+7
    y_S = y_L + 10
    width = 2

    start_S_x = int(mid_x - bar_in_pixels_S/2)
    start_L_x = int(mid_x - bar_in_pixels_L/2)

    draw.line((start_L_x, y_L, start_L_x + bar_in_pixels_L, y_L), fill='black', width=width)
    draw.line((start_S_x, y_S, start_S_x + bar_in_pixels_S, y_S), fill='black', width=width)

    font = set_fontsize(10)
    draw.text((start_L_x+bar_in_pixels_L+10, y_L - 4), str(run['scale_bar_length'])+' '+run['unit'], fill='black', font=font)
    draw.text((start_S_x+bar_in_pixels_S+10, y_S - 4), str(bar_in_units_S)+' '+run['unit'], fill='black', font=font)

    orig_filename = os.path.basename(orig_filename)

    label = run['image_label'][:]
    label.insert(0, description)
    label.append('File: %s' % orig_filename)

    text_y = y_S + 7 + np.array([0, 20, 40, 70, 85, 100, 115])
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


def draw_bounding_boxes(image, box_list, run, resize_factor=None):

    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(np.uint8(image))

    draw = ImageDraw.Draw(image)

    font_size = run['box_thickness']*3

    # Mark the bounding boxes of all objects
    for i, box in enumerate(box_list):
        if resize_factor is not None:
            this_box = np.empty(4)
            for j in range(len(box)):
                this_box[j] = int(round(box[j]*resize_factor))
        else:
            this_box = box

        y1 = math.ceil(this_box[0])
        x1 = math.ceil(this_box[1])
        y2 = math.ceil(this_box[2])
        x2 = math.ceil(this_box[3])

        draw.line([x1, y2, x2, y2], fill='red', width=int(run['box_thickness']))
        draw.line([x1, y1, x2, y1], fill='red', width=int(run['box_thickness']))
        draw.line([x1, y1, x1, y2], fill='red', width=int(run['box_thickness']))
        draw.line([x2, y1, x2, y2], fill='red', width=int(run['box_thickness']))

        font = set_fontsize(int(font_size))
        draw.text(((x1+x2)/2, (y1+y2)/2), str(i+1), fill='red', font=font)

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
    '''
    Retrieves microns per pixel from associated xml file
    DEPRECATED: now require pixel size input into settings file
    '''
    xml_name = os.path.splitext(filename)[0]+'.xml'
    # Get the microns-per-pixel values:
    root = xml_tree.parse(xml_name).getroot()

    sub_root = root.findall('Calibration')[0]
    x = float(sub_root.findtext('MicronsPerPixelX'))
    y = float(sub_root.findtext('MicronsPerPixelY'))

    return x, y


def resize(image, run):
    '''
    Scales image based on units per pixel
    Only works on non-bigtiffs
    '''
    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(image)

    print 'INFO: resizing...'
    height, width, _ = np.shape(image)
    # x_image, y_image = image.size
    # Calculate the new dimensions

    scale_factor_x = run['units_per_pixel'] / run['pixel_size_x']
    scale_factor_y = run['units_per_pixel'] / run['pixel_size_y']

    m_resized = int(math.ceil(scale_factor_x * width))
    n_resized = int(math.ceil(scale_factor_y * height))

    resized = image.resize((m_resized, n_resized), Image.ANTIALIAS)

    return np.array(resized)
    #return ndimage.zoom(image, (scale_factor_y, scale_factor_x)) # for big tiff, but very inefficient
