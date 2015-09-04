import settings
import images
import sys

# Segment uses the bounding box identified by the sharpest image in a
# set of stacks to chop just the edf into individual images

# Started on 3/21/2014 by Yusu Liu
# code uses base code of PM Hull (20-Oct-13)with updates by B. Dobbins, PMH, and Y. Liu
# converted to python by K. Nelson (2015-Sept)
# NOTE: It is now a function, not a stand-alone script
#       (Additional info on the parameters coming soon by brian)


def segment(settings_file):

    version = '2015-8-31'

    runs = settings.parse(settings_file)

    for i, run in enumerate(runs):

        print('Segment - running configuration %d of %d from %s'
              % (i+1, len(runs), settings_file))

        # Get list of images in directory
        target_images = images.list_files(run['directory'], run['debug'])

        # Get the microns per pixel for this image: (new, and ugly, modification - Oct. 2014)
        run['microns_per_pixel'] = images.microns_per_pixel_xml(target_images[0])[2]

        # Load, resize and border top-level image
        current_image = images.load(target_images[0], run)

        # Identify all objects based on threshold & minimumLight values
        objects = images.find_objects(current_image, run)

        # If we're running in 'sample' or 'save' modes, we've got more to do
        if run['mode'] in ['sample', 'save']:
            # Loop over the planes we're interested in, load an image, then process it
            for plane in range(len(target_images)):
                current_image = images.load(target_images[plane])

                if run['mode'] == 'sample':
                    process.sample(current_image, objects, target_images[plane], version, run)
        #        elif run['mode'] == 'save':
        #            process.save_all(current_image, objects, target_images[plane], plane, version, run)

        # dire


if __name__ == "__main__":

    if len(sys.argv) == 2:
        segment(sys.argv[1])

    else:
        print 'Usage: segment <settings_file>'
        sys.exit('Error: incorrect usage')
