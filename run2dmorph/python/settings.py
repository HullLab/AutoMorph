import ConfigParser
from io import StringIO
from datetime import datetime
import numpy as np
import sys
import os
import getpass


def parse(filename):

    # Set up defaults
    default_step_size = 0.01
    defaults = {
                'input_ext': 'tif',
                'output_ext': 'tif',
                'pixel_size_x': 1,
                'pixel_size_y': 1,
                'save_intermediates': False,
                'get_coordinates': True,
                'intensity_range_in': [0, 0.2],
                'intensity_range_out': [0, 1],
                'gamma': 2,
                'threshold_adjustment': 0,
                'smoothing_sigma': 7,
                'noise_limit': 0.05,
                'write_csv': False,
                'downsample': True,
                'num_points': 100,
                'draw_ar': True,
                'subdirectory': 'final'+os.sep+'focused_unlabeled'
                }

    translate = {
                 'image_extension': 'input_ext',
                 'microns_per_pixel_X': 'pixel_size_x',
                 'microns_per_pixel_Y': 'pixel_size_y'
    }

    required_list = ['directory', 'sampleID']
    boolean_list = ['save_intermediates', 'get_coordinates', 'write_csv', 'downsample', 'draw_ar']
    float_list = ['pixel_size_x', 'pixel_size_y', 'gamma', 'threshold_adjustment',
                  'smoothing_sigma', 'noise_limit', 'num_points']

    # Parse setting
    settings = defaults

    settings['timestamp'] = datetime.now().strftime('%Y-%m-%d at %H:%M:%S')

    parser = ConfigParser.SafeConfigParser(allow_no_value=True)
    parser.optionxform = str  # preserve case

    if os.path.isfile(filename):
        try:
            parser.read(filename)
        except ConfigParser.MissingSectionHeaderError:
            vfile = StringIO(u'[morph2d]\n%s' % open(filename).read())
            parser.readfp(vfile)
    else:
        sys.exit("Error: Cannot open settings file "+filename)

    # set optional variables
    for setting in parser.options('morph2d'):
        if settings in translate.keys():
            settings = translate[settings]

        if 'intensity' in setting:
            intensity_str = parser.get('morph2d', setting)

            # remove human language
            intensity_range = threshold_str.replace('[', '').split(',')

            intensity_range = map(float, intensity_range)
            print setting, intensity_range

            if len(thresholds) != 2:
                sys.exit('Error: unrecognized syntax for setting:', setting)

            settings[setting] = intensity_range

        elif setting in boolean_list:
            settings[setting] = parser.getboolean('morph2d', setting)
        elif setting in float_list:
            settings[setting] = parser.getfloat('morph2d', setting)
        else:
            settings[setting] = str(parser.get('morph2d', setting))

    # check for required parameters
    for required in required_list:
        if required not in settings.keys():
            sys.exit('Error: '+required+' must be set in settings file.')

    if 'output_filename' not in settings.keys():
        settings['output_filename'] = settings['sampleID']

    settings['directory'] = settings['directory'].rstrip(settings['subdirectory'])

    if 'out_directory' not in settings.keys():
        settings['out_directory'] = settings['directory']+os.sep+'morph2d'

    # Set up additional global settings
    if settings['directory'].endswith(os.sep):
        settings['directory'] = settings['directory'].rstrip(os.sep)

    print settings

    return settings


def drop_extra_settings(settings):

    del settings['subdirectory']
    del settings['unique_id']
    del settings['image_label']
    del settings['full_output']
    del settings['timestamp']
    del settings['units_per_pixel']
    del settings['bigtiff']

    return settings


def save(settings):

    write_directory = settings['full_output']
    settings = drop_extra_settings(settings)

    parser = ConfigParser.SafeConfigParser()
    parser.optionxform = str  # preserve case

    username = getpass.getuser()
    timestamp = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
    filename = 'settings_morph2d_%s_%s.txt' % (username, timestamp)

    if not os.path.exists(write_directory):
        os.makedirs(write_directory)

    section = 'morph2d'
    parser.add_section(section)

    for option, value in settings.iteritems():

        parser.set(section, str(option), str(value))

    with open(write_directory+'/'+filename, 'w') as f:
        f.write('# Saved Settings:\n')
        parser.write(f)
