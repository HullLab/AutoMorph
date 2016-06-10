#!/usr/bin/env python

### All of these functions are duplicated in segment/images.py ###


def list_files(directory, file_extension):
    '''
    This function takes a directory and returns a list of all TIF images in that
    directory
    '''

    file_list = glob.glob(directory+os.sep+"*."+file_extension)

    print 'INFO: images.find() found %d files' % len(file_list)

    return sorted(file_list)


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
    # return ndimage.zoom(image, (scale_factor_y, scale_factor_x)) # for big tiff, but very inefficient


def save(image, filename, tags=''):

    if isinstance(image, (np.ndarray, np.generic)):
        image = Image.fromarray(image)

    if tags:
        image.save(filename, tiffinfo=tags)
    else:
        image.save(filename)