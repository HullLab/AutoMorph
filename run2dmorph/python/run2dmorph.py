#!/usr/bin/env python

# Originally written by A. Hsiang
#
# 2016-06: Ported to python (K. Nelson)

import settings

from datetime import datetime
import glob
import os
import socket
import sys


def morph2d(settings_file):

    version = '2016-6-8'

    print "Loading settings from %s..." % settings_file
    run = settings.parse(settings_file)

    if not os.path.exists(run['out_directory']):
        os.mkdir(run['out_directory'])

    print str(datetime.now())

    image_list = list_files(run['directory']+os.sep+run['subdirectory'], run['input_ext'])

    for image in image_list:

        print image
        outline = extract_outline(image, run)


def extract_outline(image, run):

    return


# def load(filename, run):
#     '''
#     Load image from given path and resizes it.
#     '''

#     start = time.time()

#     try:
#         img = Image.open(filename)
#         img = np.array(img)
#         run['bigtiff'] = False
#     except IOError:
#         if run['input_ext'] == 'tif':
#             print "File may be a BIGtiff, attempting alternate read..."
#             img = tifffile.imread(filename)
#             run['bigtiff'] = True
#         else:
#             raise

#     print np.shape(img)
#     end = time.time()
#     print 'INFO: images.load() processed %s ( %f seconds)' % (filename, end-start)

#     if run['pixel_size_x'] != run['pixel_size_y']:
#         print 'INFO: x and y pixel sizes differ, resizing image to have square pixels'
#         img = resize(img, run)

#     return img


def list_files(directory, file_extension):
    '''
    This function takes a directory and returns a list of all TIF images in that
    directory
    '''

    file_list = glob.glob(directory+os.sep+"*."+file_extension)

    print 'INFO: images.find() found %d files' % len(file_list)

    return sorted(file_list)


if __name__ == "__main__":

    if socket.gethostname() == 'tide.geology.yale.edu':
        os.nice(10)

    if len(sys.argv) == 2:
        morph2d(sys.argv[1])

    else:
        print 'Usage: run2dmorph <settings_file>'
        sys.exit('Error: incorrect usage')
