from ConfigParser import SafeConfigParser
from io import StringIO
from datetime import datetime
import numpy as np
import sys
import os


def parse_settings(filename):
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
    defaults = {'tag': '',
                'threshold': 0.20,
                'minimumSize': 100,
                'maximumSize': 2000,
                'mode': 'sample',
                'source': 'Unspecified Source',
                'age': 'Unspecified Age',
                'debug': 0
                }

    debug_settings = {'off': 0, 'low': 1, 'high': 2}

    # Parse setting
    settings = {}

    settings['timestamp'] = datetime.now().strftime('%Y-%m-%d at %H:%M:%S')
    settings['microns_per_pixel'] = 0.0

    parser = SafeConfigParser()
    vfile = StringIO(u'[settings]\n%s' % open(filename).read())
    parser.readfp(vfile)

    # set required variable
    settings['directory'] = parser.get('settings', 'directory')
    settings['output'] = parser.get('settings', 'output')

    # set optional variables
    for setting in defaults.keys():
        print setting
        if setting == 'threshold':
            threshold_str = parser.get('settings', 'threshold', defaults['threshold'])

            # remove human language
            thresholds = threshold_str.replace('-', '').replace('by', '').split()
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
            settings['debug'] = debug_settings[parser.get('settings', 'debug', defaults['debug'])]
        else:
            settings[setting] = parser.get('settings', setting, defaults[setting])

    # duplicate settings for each value of threshold

    all_settings = []
    for i in range(num_permutations):
        all_settings.append(settings)
        all_settings[i]['threshold'] = thresholds[i]

    return all_settings


def save_settings(settings, write_directory):

    parser = ConfigParser.SafeConfigParser()

    username = os.getuid()
    timestamp = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
    filename = 'settings_%s_%s.txt' % (username, timestamp)

    if not os.path.exists(write_directory):
        os.makedirs(write_directory)

    for option, value in settings.keys():
        if option == 'debug':
            debug = debug_settings.keys()[debug_settings.values().index(value)]
        else:
            parser.set(option, value)

    with open(write_directory+'/'+filename) as f:
        f.write('# Saved Settings:')
        parser.write(f)
