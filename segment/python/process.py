import os
import math
import images

import aux

import numpy as np


def sample(image, box_list, orig_filename, run):
    '''
    Deprecated. This functionality was never particularly useful apparently.
    To be removed.
    '''

    # Define the size of the length of the square of our region to save
    region_size = 3000

    # make list of 5 sample images and define cropping boundaries
    samples = pick_and_expand_sample_boxes(image, box_list, region_size)

    for i, sample in enumerate(samples):

        output_filename = '%s%s%s_sample_%s_%02d.%s' % (run['full_output'], os.sep, run['unique_id'],
                                                        run['image_file_label'], i+1,
                                                        run['output_ext'])

        image_subsample = images.crop(image, sample)

        description = 'Sample Window %05d of %05d ( %d x %d pixels at slide position %05.2f%% x %05.2f%% )' \
                      % (i+1, len(samples), region_size, region_size, sample[0], sample[1])

        labeled_image_subsample, _ = images.label_image(image_subsample, orig_filename, description, run)

        images.save(labeled_image_subsample, output_filename)


def final(orig_filename, box_list, run, plane_num):

    image = images.load(orig_filename, run)
    image_size = image.size   # [width, height]

    for box_num, box in enumerate(box_list):

        # crop expects [x1, y1, x2, y2], box is [y1, x1, y2, x2]
        crop_box = [box[1], box[0], box[3], box[2]]
        width = crop_box[2] - crop_box[0]
        height = crop_box[3] - crop_box[1]
        image_subsample = images.crop(image, crop_box)

        x_percent = crop_box[0] / image_size[0] * 100
        y_percent = crop_box[1] / image_size[1] * 100
        description = 'Object #%05d of %05d ( %d x %d pixels at slide position %05.2f x %05.2f )' \
                      % (box_num+1, len(box_list), width, height, x_percent, y_percent)

        labeled_image_subsample, label = images.label_image(image_subsample, orig_filename,
                                                            description, run)

        object_directory = '%s%s%s_obj%05d' % (run['full_output'], os.sep, run['unique_id'], box_num+1)
        if not os.path.exists(object_directory):
            os.makedirs(object_directory)

        print object_directory
        output_filename = '%s%s%s_obj%05d_plane%03d.%s' % (object_directory, os.sep,
                                                           run['unique_id'], box_num+1, plane_num,
                                                           run['output_ext'])

        tags = images.add_comment(output_filename, '. '.join(label))
        images.save(labeled_image_subsample, output_filename, tags=tags)


def save_overview_image(full_image, box_list, orig_filename, run):
    '''
    Save low resolution jpg of entire image with boxes marked
    '''

    full_image = images.draw_bounding_boxes(full_image, box_list)

    # save entire image
    if run["mode"] == "final":
        output_dir = run['full_output'].replace('/final','')
    else:
        output_dir = run['full_output']    
    filename_full_image = "%s%s%s_boxes_%s.jpg" % (output_dir, os.sep, run['unique_id'],
                                                   run['image_file_label'])

    description = 'Full Image'
    labeled_image, _ = images.label_image(full_image, orig_filename, description, run)

    images.save(labeled_image, filename_full_image)


def pick_and_expand_sample_boxes(image, box_list, region_size):

    image_size = image.size

    image = np.array(image)

    chosen_boxes = []

    chosen_locations = [(0.25, 0.25),
                        (0.75, 0.25),
                        (0.50, 0.50),
                        (0.25, 0.75),
                        (0.75, 0.75)]

    for location in chosen_locations:
        chosen_boxes.append(closest_box(image, box_list, location))

    if len(chosen_boxes) > len(set(chosen_boxes)):
        chosen_boxes = set(chosen_boxes)
        print('At least one object is picked twice as a sample image; only %d images will be created.' % len(chosen_boxes))

    samples = [box_list[chosen_box] for chosen_box in chosen_boxes]

    # size cropping boxes to a specified region size
    for i, sample in enumerate(samples):

        mid_y = (sample[0]+sample[2])/2
        mid_x = (sample[1]+sample[3])/2

        corner_x = mid_x - region_size/2
        if corner_x < 1:
            corner_x = 0
        elif (corner_x + region_size) > image_size[0]:
            corner_x = image_size[0] - region_size

        corner_y = mid_y - region_size/2
        if corner_y < 1:
            corner_y = 0
        elif (corner_y + region_size) > image_size[1]:
            corner_y = image_size[1] - region_size

        samples[i] = [corner_x, corner_y, corner_x + region_size, corner_y + region_size]

    return samples


def closest_box(image, box_list, x_and_y):
    # NOT SURE IF THIS X AND Y IS CORRECT
    search_x = x_and_y[0] * image.shape[0]
    search_y = x_and_y[1] * image.shape[1]

    closest_index = None
    closest_distance = image.shape[0]

    for i, box in enumerate(box_list):
        box_x = (box[0]+box[3])/2.
        box_y = (box[1]+box[2])/2.

        distance = math.sqrt((search_x - box_x)**2 + (search_y - box_y)**2)
        if distance < closest_distance:
            closest_index = i
            closest_distance = distance

    return closest_index
