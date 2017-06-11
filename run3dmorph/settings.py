#!/usr/bin/env python

# All of these functions written originally by K. Nelson for segment
#
# 2016-03: Adapted for run3dmorph by A. Hsiang

import ConfigParser
from io import StringIO
from datetime import datetime
import numpy as np
import sys
import os
import getpass


def parse(filename):
    # Set up defaults
    defaults = {
                'pixel_size_x':1,
                'pixel_size_y':1,
                'macro':False,
                'kernel_heightmap':11,
                'kernel_outlierfilter':45,
                'grid_size':1,
                'latex':True,
                'disk_size_opening':10,
                'contrast_adjustment':3,
                'threshold_adjustment':0
                }

    required_list = ['in_directory','out_directory','sampleID','stack_image_ext']
    boolean_list = ['macro','latex']
    float_list = ['pixel_size_x','pixel_size_y','slices','zstep','kernel_heightmap','kernel_outlierfilter','grid_size','disk_size_opening','contrast_adjustment','threshold_adjustment']

    # Parse setting
    settings = defaults

    settings['timestamp'] = datetime.now().strftime('%Y-%m-%d at %H:%M:%S')

    parser = ConfigParser.SafeConfigParser(allow_no_value=True)
    parser.optionxform = str  # Preserve case

    if os.path.isfile(filename):
        try:
            parser.read(filename)
        except ConfigParser.MissingSectionHeaderError:
            vfile = StringIO(u'[morph3d]\n%s' % open(filename).read())
            parser.readfp(vfile)
    else:
        sys.exit("Error: Cannot open settings file " + filename)

    # Set optional variables
    for setting in parser.options('morph3d'):
        if setting in boolean_list:
            try:
                settings[setting] = parser.getboolean('morph3d', setting)
            except:
                pass
        elif setting in float_list:
            try:
                settings[setting] = parser.getfloat('morph3d', setting)
            except:
                pass
        else:
            settings[setting] = str(parser.get('morph3d', setting))

    # Check for required parameters
    for required in required_list:
        if required not in settings.keys():
            sys.exit('Error: '+ required + ' must be set in settings file.')

    # Set default output directory if none specified
    if not settings['out_directory']:
        settings['out_directory'] = settings['in_directory'] + os.sep + 'morph3d'

    # Set up additional global settings
    if settings['in_directory'].endswith(os.sep):
        settings['in_directory'] = settings['in_directory'].rstrip(os.sep)

    return settings


def save(settings):
    write_directory = settings['out_directory']

    parser = ConfigParser.SafeConfigParser()
    parser.optionxform = str  # Preserve case

    username = getpass.getuser()
    timestamp = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
    filename = 'settings_morph3d_%s_%s.txt' % (username, timestamp)

    if not os.path.exists(write_directory):
        os.makedirs(write_directory)

    section = 'morph3d'
    parser.add_section(section)

    for option, value in settings.iteritems():
        parser.set(section, str(option), str(value))

    with open(write_directory + os.sep + filename, 'wb') as f:
        f.write('# Saved Settings:\n')
        parser.write(f)
