#!/usr/bin/env python

import os


def makeOutputDirectories(settings):
    '''
    Create output directories.
    '''
    outPath = settings['out_directory']
    outlinePath = os.path.join(outPath,'outlines')
    coordPath = os.path.join(outPath,'coordinates')
    aspPath = os.path.join(outPath,'aspect_ratio')
    intrmedPath = os.path.join(outPath,'intermediates')

    toMake = [outPath,outlinePath,coordPath,aspPath]
    if settings['save_intermediates']:
        toMake = toMake + [intrmedPath]

    for path in toMake:
        if not os.path.exists(path):
            os.mkdir(path)
