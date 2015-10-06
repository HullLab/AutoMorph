import ConfigParser
from io import StringIO
from datetime import datetime
import numpy as np
import sys
import os


debug_settings = {'off': 0, 'low': 1, 'high': 2}


def parse(filename):
    #
    # Originally written by B. Dobbins
    #
    # 2015-08-04:   Changed check for blank lines such that errant spaces won't cause program
    # to try to parse that line (causing an "Index exceeds matrix dimensions"
    # error (A. Hsiang)
    #
    # 2015-09: Ported to python (K. Nelson)

    # Set up defaults
    default_step_size = 0.01
    defaults = {'threshold': 0.20,
                'minimumSize': 100,
                'maximumSize': 2000,
                'mode': 'sample',
                'source': 'Unspecified Source',
                'age': 'Unspecified Age',
                'debug': 0,
                'input_ext': 'tif',
                'output_ext': 'tif',
                'pixel_size_x': None,
                'pixel_size_y': None,
                'location': 'Yale Peabody Museum',
                'catalog_prefix': 'YPM IP',
                'unit': 'microns',
                'author': None
                }

    # Parse setting
    settings = defaults

    settings['timestamp'] = datetime.now().strftime('%Y-%m-%d at %H:%M:%S')

    parser = ConfigParser.SafeConfigParser(allow_no_value=True)
    parser.optionxform = str  # preserve case

    try:
        parser.read(filename)
    except ConfigParser.MissingSectionHeaderError:
        vfile = StringIO(u'[settings]\n%s' % open(filename).read())
        parser.readfp(vfile)
    except:
        raise

    # set required variable
    settings['directory'] = parser.get('settings', 'directory')
    if settings['directory'].endswith('/'):
        settings['directory'] = settings['directory'][:-1]

    settings['output'] = parser.get('settings', 'output')

    # set optional variables
    for setting in parser.options('settings'):
        if setting == 'threshold':
            threshold_str = parser.get('settings', 'threshold')

            # remove human language
            thresholds = threshold_str.replace('-', ',').replace('by', ',').split(',')
            thresholds = map(float, thresholds)

            if len(thresholds) == 2 or len(thresholds) == 3:
                # use default step size
                if len(thresholds) == 2:
                    thresholds.append(default_step_size)
                thresholds = np.arange(thresholds[0], thresholds[1],
                                       thresholds[2])
            elif len(thresholds) > 3:
                sys.exit('Error: unrecognized syntax for threshold setting')

            num_permutations = len(thresholds)

        elif setting == 'debug':
            debug_option = parser.get('settings', 'debug')
            if len(debug_option) > 1:
                settings['debug'] = debug_settings[debug_option]
            else:
                settings['debug'] = int(debug_option)

        elif 'Size' in setting or 'size' in setting:
            settings[setting] = float(parser.get('settings', setting))
        else:
            settings[setting] = str(parser.get('settings', setting))

    # Backwards compatibility tweaks
    if settings['mode'] == 'save':
        settings['mode'] = 'final'

    if settings['mode'] not in ['final','sample']:
        sys.exit('Error: unrecognized mode settings. Please specify final or sample only.')
    if settings['mode'] != 'sample' and num_permutations > 1:
        sys.exit('Error: for final mode, only give a single threshold value, not a range.')

    # Set up additional global settings
    # define full output directory
    settings['subdirectory'] = os.path.basename(settings['directory'])
    new_directory = settings['output'] + os.sep + settings['subdirectory']
    settings['full_output'] = new_directory + os.sep + settings['mode']

    # create a unique id
    settings['unique_id'] = settings['subdirectory'].split('_')[0]

    # duplicate settings for each value of threshold
    all_settings = []
    for i in range(num_permutations):
        all_settings.append(settings.copy())
        all_settings[i]['threshold'] = thresholds[i]

    return all_settings


def drop_extra_settings(settings):

    del settings['subdirectory']
    del settings['unique_id']
    del settings['image_label']
    del settings['full_output']
    del settings['timestamp']
    del settings['image_file_label']
    del settings['units_per_pixel']

    return settings


def save(settings):

    write_directory = settings['full_output']
    settings = drop_extra_settings(settings)

    parser = ConfigParser.SafeConfigParser()
    parser.optionxform = str  # preserve case

    username = os.getuid()
    timestamp = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
    filename = 'settings_%s_%s.txt' % (username, timestamp)

    if not os.path.exists(write_directory):
        os.makedirs(write_directory)

    section = 'settings'
    parser.add_section(section)

    for option, value in settings.iteritems():
        if option == 'debug':
            value = debug_settings.keys()[debug_settings.values().index(value)]

        parser.set(section, str(option), str(value))

    with open(write_directory+'/'+filename, 'w') as f:
        f.write('# Saved Settings:\n')
        parser.write(f)
