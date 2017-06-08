#!/usr/bin/python

from classes import *

import sys
import os
import shutil
import glob
from datetime import datetime


def displayVersion(version):
    print '\nRUN3DMORPH (v.%s)\n' % version


def displayTime():
    print str(datetime.now()) + '\n'


def makeOutputFolders(settings,morph3dPath):
    # Make morph3d output path
    if not os.path.exists(morph3dPath):
        os.mkdir(morph3dPath)
    # Top output subdirectories
    toMake = ['heightmaps','coordinates','volumes','offs','objs']
    topPaths = [os.path.join(morph3dPath,x) for x in toMake]
    # Heightmap output subdirectories
    toMake = ['FIJI_focused','macros']
    subPathsHM = [os.path.join(morph3dPath,'heightmaps',x) for x in toMake]
    # PDF output subdirectories
    if settings['latex']:
        toMake = ['idtf','u3d','latex','pdf']
        pdfPaths = [os.path.join(morph3dPath,'pdfs')] + [os.path.join(morph3dPath,'pdfs',x) for x in toMake]
    else:
        pdfPaths = []

    for p in topPaths + subPathsHM + pdfPaths:
        if not os.path.exists(p):
            os.mkdir(p)

    return morph3dPath


def resetRun(morph3dPath):
    shutil.rmtree(morph3dPath)


def getObjects(dataPath):
    strippedPath = os.path.join(dataPath,'stripped')
    allObjects = [os.path.basename(x) for x in glob.glob(os.path.join(strippedPath,'*obj*'))]
    allObjects.sort()
    return allObjects


def initializeObjects(settings):
    objList = getObjects(settings['in_directory'])
    allObjects = [Object(objList[i-1],settings,i) for i in range(1,len(objList)+1)]
    allObjects[0].showTotal()
    return allObjects
