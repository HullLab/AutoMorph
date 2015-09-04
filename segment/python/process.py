import os
import math
import images


def sample(image, box_list, source, version, run):

    # Define the size of the length of the square of our region to save (in microns)
    region_size = 3000

    # Get the original (end-level) directory
    directory_id = os.path.basename(run['directory'])
    # Set up main level directory
    main_directory = run['output'] + os.sep + directory_id

    if run['tag'] == 'final':
        sub_directory = 'final'
    else:
        sub_directory = '%s_th=%05.4f_size=%04.0fu-%04.0fu' \
                        % (run['tag'], run['threshold'], run['minimumSize'], run['maximumSize'])

    output_directory = main_directory + os.sep + sub_directory
    source_label = directory_id + os.sep + os.path.basename(source)

    image_array = draw_bounding_boxes(image, box_list)

    # create a unique id
    unique_id = directory_id.split('_')[0]

    output_directory = output_directory + os.sep + 'sample'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # save entire image
    filename_tif = output_directory + os.sep + unique_id + '_boxes.tif'
    filename_jpg = output_directory + os.sep + unique_id + '_boxes.jpg'
    images.save(image_array, filename_tif)
    # images.save(image_array, filename_jpg)

    # make list of 5 sample images
    sample = pick_sample(image_array, box_list)


def draw_bounding_boxes(image, box_list):

    image_array = np.array(image)

    # Mark the bounding boxes of all objects
    for box in box_list:
        X = math.ceil(box[0])
        Y = math.ceil(box[1])
        size_X = math.ceil(box[2]) - X
        size_Y = math.ceil(box[3]) - Y

        pixel_size = 3
        red_value = 192

        # top, bottom, left, right borders
        image_array[Y:(Y + pixel_size), X:(X + size_X), 1] = red_value
        image_array[(Y + size_Y - pixel_size):(Y + size_Y), X:(X + size_X), 1] = red_value
        image_array[Y:(Y + size_Y), X:(X + pixel_size), 1] = red_value
        image_array[Y:(Y + size_Y), (X + size_X - pixel_size):(X + size_X), 1] = red_value

    return image


def pick_sample(image, box_list):

    chosen_boxes = []

    chosen_locations = [(0.25, 0.25),
                        (0.75, 0.25),
                        (0.50, 0.50),
                        (0.25, 0.75),
                        (0.75, 0.75)]

    for location in chosen_locations:
        chosen_boxes.append(closest_box(image, box_list, location))

    if len(chosen_boxes) > len(set(chosen_boxes)):
        print('At least one object is picked twice as a sample image; less than five images will be created.')
    
        chosen_boxes = set(chosen_boxes)

    return chosen_boxes


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
 
